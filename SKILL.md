---
name: dsh-agent-create
description: 把一句话的 agent 想法落成可运行的 Python 项目：选模式与框架、生成骨架、写指令与工具、补评测并跑通。当用户说「做一个 agent」「搭个智能体」「把这个流程做成 agent」「agent 应用」「多智能体团队」时使用；不用于改 DSH 插件或只写角色提示词。
whenToUse: 用户要新建一个能跑起来的独立 agent 应用，或要把某个 agent 模板改造成新项目时使用。只是调 prompt、解释概念、修改 DSH 自身插件或 preset 时不要用。
metadata:
  version: 1.0.0
  source: https://github.com/Shubhamsaboo/awesome-llm-apps
  license: Apache-2.0
---

# 造一个能跑的 Agent

## 目标

把「我想做一个 XX agent」变成 `<name>/` 下一个能装、能跑、有评测、README 能照抄的独立 Python 项目（不是 DSH 插件或 preset）。完成标准：`check_agent.py` 报 0 个 error，且用一条真实输入跑通一次。

## 何时使用

- 该用：新建 agent 应用 / 智能体 / 多智能体团队；把仓库模板改造成自己的 agent；给已有脚本套上 agent 外壳。
- 不该用：只改 prompt 或角色设定（直接改文件）；改 DSH 插件、preset、Web UI（走 `cordis-plugin-development` / `editing-cordis-compositions`）；一次性问答（不用建项目）。

## 流程

1. **定任务契约** —— 写清 5 项：谁用、输入从哪来、输出给谁用、有没有副作用（发邮件/下单/写库）、什么算做完。缺的项最多问用户 3 个问题；用户已说清就不问。不要问「你想用什么框架」。
2. **找最近模板** —— 读 [`references/repo-map.md`](references/repo-map.md) 的「按需求找模板」表，只取命中的那一行，再看该模板的 README 和主文件。抄骨架，不整仓复制；网络不通就跳过，直接用模式卡。
3. **定模式** —— 默认 `single`。只有能明确指出「单 agent 缺哪一步」时才升级：按意图分流、或多来源/多阶段，都用 `multi`（对应 router / orchestrator 两种形态）；定时触发用 `always-on`；私有文档用 `single + retrieval tool`。拿不准时只读 [`references/patterns.md`](references/patterns.md) 里对应的那张卡。
4. **定框架** —— 默认 `openai-agents`（模型可换任意 OpenAI 兼容端点）；Gemini/Google 生态用 `google-adk`；要多 agent + 内置会话/服务化用 `agno`；团队角色扮演、显式状态机、强类型输出分别看 CrewAI、LangGraph、Pydantic AI。脚手架只覆盖前三个；`always-on` 只支持 `openai-agents` 和 `agno`。需要换框架或换模型时，再读 [`references/frameworks.md`](references/frameworks.md) 的对应节。
5. **生成骨架** —— 在用户工作目录执行（`scripts/` 相对本 skill 的 Base directory）：
   ```bash
   python scripts/scaffold_agent.py --name <kebab-name> --framework openai-agents \
     --pattern single --ui streamlit --out <项目目录> --description "<一句话用途>"
   ```
   生成后立刻 `pip install -r <项目目录>/requirements.txt`，不要等写完代码才装。
6. **写死规格与工具** —— 用 [`references/agent-spec.md`](references/agent-spec.md) 的六段式写 `agent.py` 的 instructions；把 `tools.py` 里的 TODO 换成真实数据源。每个工具必须有：类型标注、docstring（何时调用 + 参数 + 返回 + 失败形态）、超时、`ERROR: <原因>` 返回。指令不超过 400 词，每条规则都能判定通过/不通过。
7. **补评测并跑通** —— 把 `evals/cases.jsonl` 填成 6 类：happy、ambiguous、missing-input、tool-failure、out-of-scope、injection。先跑 `check_agent.py`，再跑 `evals/run_eval.py`，最后用真实输入跑一次入口。全绿才算完成；有红项就改代码，不要改评测标准。
8. **交付** —— 更新 README 的运行步骤和环境变量表，按「输出格式」回话。把「已验证」和「已知限制」分开写，没验证过的不要说通过。

## 输出格式

项目结构（`--ui cli` 时没有 `app.py`，`--pattern always-on` 时多 `scheduler.py`）：

```text
<name>/
├── README.md
├── requirements.txt
├── .env.example
├── <pkg>/
│   ├── config.py
│   ├── tools.py
│   └── agent.py
├── run.py
├── app.py
└── evals/
    ├── cases.jsonl
    ├── run_eval.py
    └── README.md
```

最终回复模板：

```markdown
## 做好了：<name>
- 模式 / 框架：<pattern> / <framework>
- 跑起来：`python run.py "<示例输入>"`（或 `streamlit run app.py`）
- 需要配置：<ENV_VAR_1>, <ENV_VAR_2>
- 已验证：check_agent 0 error；eval <通过数>/<总数>；smoke <输入摘要> 通过
- 已知限制：<1~3 条，例如只支持 CSV、单轮、无持久化>
```

## 约束

- 密钥只从环境变量读，`.env.example` 只放占位符 → 硬编码会被提交，泄露后必须轮换。
- 有副作用的工具默认 `dry_run=True`，显式关闭 dry-run 才执行 → 否则测试会真的发邮件、下单、写库。
- 工具失败返回 `ERROR: <原因>`，不抛裸异常、不返回 "ok" → 模型会把失败当成功继续编。
- 每个项目至少 3 条 eval，且至少 1 条 out-of-scope → 否则无法判断改动是变好还是退化。
- 单 agent 能做完就不上多 agent → 多一层 handoff，token 和调试成本都翻倍，质量未必升。
- 所有重试、handoff、工具循环必须有上限（≤3 次） → 无限循环会烧光预算。
- 不得把示例数据、mock 返回值当真实结果交付 → 用户会拿假数据做决策。
- 不得写绝对路径、不得在 import 时读必填环境变量 → 换机器即废，`--help` 都会崩。

## 反例

- ❌ 用户要「总结周报」，却搭 triage + research + writer 三个 agent → 单 agent + 一个读文件工具足够，多出的两层只增加失败点。
- ❌ instructions 写「你是资深专家，请专业、深入地分析」→ 不可判定，十次输出十个样；改成「输出 3 段，每段 ≤80 字，第一段必须是结论」。
- ❌ 工具里 `except Exception: return "done"` → 模型认为数据已取到，拿着空结果往下写。
- ❌ 把 API key 写进 `config.py` 图省事 → 提交即泄露；只能从 `os.getenv` 读并在缺失时给出可读报错。
- ❌ 交付时只说「已完成」，不写怎么跑、要配什么 key → 用户第一步就卡住。

## 校验

`scripts/` 相对本 skill 的 Base directory；`<项目目录>` 用绝对路径或 `cd` 后的相对路径。

```bash
python scripts/check_agent.py <项目目录>          # 结构 + 密钥 + 工具契约 + eval 覆盖
python <项目目录>/evals/run_eval.py --dir <项目目录>   # 需要 API key
python <项目目录>/run.py "<一条真实输入>"
```

逐条打勾：

- [ ] `check_agent.py` 0 error（warning 逐条看过）
- [ ] `.env.example` 覆盖代码里读到的每个环境变量
- [ ] 每个工具的 docstring 写明了「何时调用 / 参数 / 返回 / 失败」
- [ ] 6 类 eval 至少各 1 条，out-of-scope 和 injection 有断言
- [ ] 真实输入跑通，输出符合 instructions 里写的格式
- [ ] README 的命令从干净环境能照抄执行

## 参考

- 模式判定与最小结构：[`references/patterns.md`](references/patterns.md)
- 框架对照与最小代码：[`references/frameworks.md`](references/frameworks.md)
- 模板索引（awesome-llm-apps）：[`references/repo-map.md`](references/repo-map.md)
- 规格卡 / 指令 / 工具契约 / 评测格式：[`references/agent-spec.md`](references/agent-spec.md)
- 脚手架：`scripts/scaffold_agent.py`；静态检查：`scripts/check_agent.py`

模板索引与结构约定来自 [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)（Apache-2.0），本 skill 为改写后的操作手册。
