#!/usr/bin/env python3
"""Static checks for an agent project.

Checks structure, secret hygiene, env-var coverage, tool contracts, eval
coverage, and a few safety defaults. Does not call the model and needs no
API key.

Usage:
    python check_agent.py <project-dir>
    python check_agent.py <project-dir> --strict   # warnings become errors

Exit code: 0 no errors, 1 errors found, 2 bad invocation.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache"}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".jsonl", ".toml", ".yaml", ".yml", ".example"}

SECRET_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "OpenAI-style secret key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key id"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "Google API key"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
]

ABS_PATH = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:\\")
POSIX_HOME = re.compile(r"(?<![\w.])/(Users|home)/[A-Za-z0-9._-]+/")
REQUIRED_KINDS = {"happy", "ambiguous", "missing-input", "tool-failure", "out-of-scope", "injection"}

ERROR = "ERROR"
WARN = "WARN"


class Report:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == ".env":
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in {".env.example", ".gitignore"}:
            yield path


def find_package(root: Path) -> Path | None:
    candidates = [
        path
        for path in root.iterdir()
        if path.is_dir()
        and path.name not in SKIP_DIRS
        and (path / "agent.py").is_file()
        and (path / "__init__.py").is_file()
    ]
    return candidates[0] if candidates else None


def read_env_example(path: Path) -> set[str]:
    keys: set[str] = set()
    if not path.is_file():
        return keys
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            keys.add(key)
    return keys


def literal(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def collect_env_reads(tree: ast.AST) -> set[str]:
    used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "getenv" and node.args:
                value = literal(node.args[0])
                if value:
                    used.add(value)
            elif (
                isinstance(func, ast.Attribute)
                and func.attr == "get"
                and isinstance(func.value, ast.Attribute)
                and func.value.attr == "environ"
                and node.args
            ):
                value = literal(node.args[0])
                if value:
                    used.add(value)
        elif isinstance(node, ast.Subscript):
            value = node.value
            if (
                isinstance(value, ast.Attribute)
                and value.attr == "environ"
                and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)
            ):
                used.add(node.slice.value)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.endswith("_ENV"):
                    value = literal(node.value)
                    if value:
                        used.add(value)
    return used


def check_structure(report: Report, root: Path, pkg: Path | None) -> None:
    for name in ("README.md", "requirements.txt", ".env.example", "run.py"):
        if not (root / name).is_file():
            report.error(f"缺少 {name}")
    if pkg is None:
        report.error("找不到包目录（需要同时含 agent.py 和 __init__.py）")
        return
    if not (pkg / "agent.py").is_file():
        report.error("包目录缺少 agent.py")
    if not (pkg / "tools.py").is_file():
        report.warn("包目录没有 tools.py：确认这个 agent 不需要工具")


def check_secrets(report: Report, root: Path) -> None:
    for path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pattern, label in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                line = text[: match.start()].count("\n") + 1
                report.error(f"{path.relative_to(root)}:{line} 疑似{label}，立即移除并轮换")


def check_absolute_paths(report: Report, root: Path) -> None:
    for path in iter_text_files(root):
        if path.suffix not in {".py", ".md"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pattern, label in ((ABS_PATH, "Windows 绝对路径"), (POSIX_HOME, "用户目录绝对路径")):
            match = pattern.search(text)
            if match:
                line = text[: match.start()].count("\n") + 1
                report.error(f"{path.relative_to(root)}:{line} 含{label}，换机器会失效")


def check_env(report: Report, root: Path, pkg: Path | None) -> None:
    declared = read_env_example(root / ".env.example")
    used: set[str] = set()
    for path in root.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        used |= collect_env_reads(tree)

    missing = sorted(used - declared)
    for key in missing:
        report.error(f"代码读取了 {key}，但 .env.example 没有声明")
    unused = sorted(declared - used)
    for key in unused:
        report.warn(f".env.example 声明了 {key}，但代码里没读到")


def check_tools(report: Report, pkg: Path | None) -> None:
    if pkg is None or not (pkg / "tools.py").is_file():
        return
    path = pkg / "tools.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        report.error(f"{path.name} 语法错误：{exc}")
        return
    functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    public = [n for n in functions if not n.name.startswith("_")]
    if not public:
        report.warn("tools.py 里没有公开工具函数")
    for node in public:
        if not ast.get_docstring(node):
            report.error(f"tools.py::{node.name} 缺少 docstring，模型看不到工具契约")
        missing_types = [
            arg.arg for arg in node.args.args if arg.annotation is None and arg.arg not in {"self", "cls"}
        ]
        if node.returns is None:
            missing_types.append("return")
        if missing_types:
            report.warn(f"tools.py::{node.name} 缺少类型标注：{', '.join(missing_types)}")


def check_evals(report: Report, root: Path) -> None:
    path = root / "evals" / "cases.jsonl"
    if not path.is_file():
        report.error("缺少 evals/cases.jsonl")
        return
    kinds: set[str] = set()
    asserted = 0
    count = 0
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        try:
            case = json.loads(raw)
        except json.JSONDecodeError as exc:
            report.error(f"evals/cases.jsonl:{line_no} JSON 无效：{exc}")
            continue
        if "input" not in case:
            report.error(f"evals/cases.jsonl:{line_no} 缺少 input")
        count += 1
        kinds.add(str(case.get("kind", "")))
        if case.get("must_contain") or case.get("must_not_contain"):
            asserted += 1
    if count < 3:
        report.error(f"eval 只有 {count} 条，至少 3 条")
    missing = sorted(REQUIRED_KINDS - kinds)
    if missing:
        report.warn(f"eval 缺少类型：{', '.join(missing)}")
    if asserted < 2:
        report.warn("不到 2 条 eval 带断言，等于没测")
    runner = root / "evals" / "run_eval.py"
    if not runner.is_file():
        report.warn("没有 evals/run_eval.py，评测需要手动跑")


def check_requirements(report: Report, root: Path) -> None:
    path = root / "requirements.txt"
    if not path.is_file():
        return
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    if not lines:
        report.error("requirements.txt 为空")
        return
    if not any("==" in line or ">=" in line for line in lines):
        report.warn("requirements.txt 没有版本约束，复现性差")


def check_gitignore(report: Report, root: Path) -> None:
    path = root / ".gitignore"
    if not path.is_file():
        report.warn("没有 .gitignore，.env 可能被提交")
        return
    if ".env" not in path.read_text(encoding="utf-8").split():
        report.warn(".gitignore 没有忽略 .env")


def check_scheduler(report: Report, root: Path) -> None:
    path = root / "scheduler.py"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "dry_run" not in text:
        report.error("scheduler.py 没有 dry_run，测试可能触发真实副作用")
    elif not re.search(r"dry_run\s*:\s*bool\s*=\s*True", text):
        report.warn("scheduler.py 的 dry_run 默认值不是 True")


def check_error_swallowing(report: Report, root: Path) -> None:
    pattern = re.compile(r"except\s+(?:Exception|BaseException)[^:]*:\s*\n\s*(?:pass|return\s+['\"]?(?:ok|done|success))", re.I)
    for path in root.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        if pattern.search(text):
            report.warn(f"{path.relative_to(root)} 有吞异常的分支（except → pass/ok）")


def check_todos(report: Report, root: Path) -> None:
    hits = 0
    for path in iter_text_files(root):
        if path.suffix not in {".py", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        hits += len(re.findall(r"\bTODO\b", text))
    if hits:
        report.warn(f"还有 {hits} 处 TODO；交付前逐条确认或替换")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="project directory")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    report = Report(root)
    pkg = find_package(root)

    check_structure(report, root, pkg)
    check_secrets(report, root)
    check_absolute_paths(report, root)
    check_env(report, root, pkg)
    check_tools(report, pkg)
    check_evals(report, root)
    check_requirements(report, root)
    check_gitignore(report, root)
    check_scheduler(report, root)
    check_error_swallowing(report, root)
    check_todos(report, root)

    print(f"[{'OK' if not report.errors else 'FAIL'}] {root}")
    for message in report.errors:
        print(f"  x {message}")
    for message in report.warnings:
        print(f"  ! {message}")
    print(f"\n{len(report.errors)} error(s), {len(report.warnings)} warning(s)")

    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
