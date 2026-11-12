# dsh-agent-create

一个把「我想做一个 XX agent」落成可运行 Python 项目的 Agent Skill。给编码 agent 装上后，说一句「做一个每日竞品简报 agent」，它会按固定流程产出可运行、可评测、README 能照抄的项目。

模板结构与约定参考了 [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)（Apache-2.0），正文、脚本与检查器为本项目重写。

## 它能做什么

- 先定任务契约：谁用、输入从哪来、输出给谁、有没有副作用、什么算做完
- 从 100+ 模板里找同构骨架，而不是从零写
- 在 7 种模式里选一个：单 agent、路由、编排、生成+校验、RAG、always-on、人在环
- 在 OpenAI Agents SDK / Google ADK / Agno 之间选型，并生成可运行骨架
- 写六段式 instructions、工具契约、dry-run 默认值
- 生成 6 类 eval 用例（happy / ambiguous / missing-input / tool-failure / out-of-scope / injection）
- 静态检查：密钥、环境变量、工具 docstring、eval 覆盖、绝对路径

## 安装

任何支持 `SKILL.md` 的 agent 都可以用。DeepSeek Harness 项目级安装：

```bash
mkdir -p <project>/.dsh/skills
cp -r dsh-agent-create <project>/.dsh/skills/
```

用户级安装（所有项目可用）：

```bash
cp -r dsh-agent-create ~/.dsh/skills/
```

Claude Code / Codex / Cursor 等把目录放到各自的 skills 目录即可。

## 使用

对 agent 说：

> 做一个每日竞品简报 agent，输出 3 条带来源的动态

或手动生成骨架：

```bash
python scripts/scaffold_agent.py \
  --name competitor-brief \
  --framework openai-agents \
  --pattern single \
  --ui streamlit \
  --out ./competitor-brief \
  --description "每日竞品简报，输出 3 条带来源的动态"
```

生成的项目包含 `README.md`、`requirements.txt`、`.env.example`、agent 包、CLI/Streamlit 入口和 `evals/`。

## 目录

```text
dsh-agent-create/
├── SKILL.md                     # 主入口：8 步流程、输出模板、约束、校验
├── references/
│   ├── patterns.md              # 7 种 agent 模式与最小结构
│   ├── frameworks.md            # 6 个框架对照 + 最小代码 + 换模型
│   ├── repo-map.md              # awesome-llm-apps 模板索引
│   └── agent-spec.md            # 规格卡、指令、工具契约、评测格式
└── scripts/
    ├── scaffold_agent.py        # 3 框架 × 3 模式 × CLI/Streamlit
    └── check_agent.py           # 静态检查
```

## 校验

```bash
python scripts/check_agent.py <项目目录>
python <项目目录>/evals/run_eval.py --dir <项目目录>
python <项目目录>/run.py "一条真实输入"
```

`check_agent.py` 不需要 API key；`run_eval.py` 和 `run.py` 需要配置模型 key。

## 要求

- Python 3.10+
- 脚手架与检查器只用标准库
- 生成的项目按所选框架安装依赖（见生成的 `requirements.txt`）

## License

Apache-2.0，见 [LICENSE](LICENSE)。
