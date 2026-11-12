# 框架对照与最小代码

只列本项目会用到的部分。API 以安装后的包为准；装完先跑最小例子，再往里加东西。

## 目录

- [一眼选型](#一眼选型)
- [OpenAI Agents SDK](#openai-agents-sdk)
- [Google ADK](#google-adk)
- [Agno](#agno)
- [CrewAI](#crewai)
- [LangGraph](#langgraph)
- [Pydantic AI](#pydantic-ai)
- [换模型 / 换网关](#换模型--换网关)
- [运行面](#运行面)

## 一眼选型

| 框架 | 最适合 | 多 agent | 学习成本 | 备注 |
|---|---|---|---|---|
| OpenAI Agents SDK | 通用单/多 agent，工具 + handoff + guardrail | handoff / agent-as-tool | 低 | 默认首选；兼容 OpenAI 端点 |
| Google ADK | Gemini 生态，ADK Web 调试，子 agent | `sub_agents` / workflow agents | 中 | 目录里必须有 `root_agent` |
| Agno | 快速起单 agent、内置工具、Team、AgentOS | `Team(members=...)` | 低 | 自带 memory/db/UI，样板少 |
| CrewAI | 角色扮演式团队（role/goal/backstory） | `Crew` | 低 | 适合流程固定的多角色 |
| LangGraph | 明确状态机、可中断/恢复、复杂控制流 | 图节点 | 高 | 控制流值得画图时再用 |
| Pydantic AI | 强类型输入输出、结构化抽取 | 有限 | 中 | 输出 schema 复杂时好用 |

默认顺序：**OpenAI Agents SDK → Agno → Google ADK**。只有明确理由才换。

## OpenAI Agents SDK

安装：`pip install openai-agents`

```python
import asyncio

from agents import Agent, Runner, function_tool


@function_tool
def search_knowledge(query: str, limit: int = 5) -> str:
    """Search the local knowledge base.

    Args:
        query: Short keyword query.
        limit: Maximum number of facts to return.
    """
    return "No results."


agent = Agent(
    name="Research Assistant",
    instructions=(
        "你是研究助理。先判断问题是否需要查资料；需要就调用 search_knowledge。"
        "输出 3 段：结论、依据、下一步。没有资料时直说没找到。"
    ),
    model="gpt-4o-mini",
    tools=[search_knowledge],
)


async def main() -> None:
    result = await Runner.run(agent, "整理一下 MCP 的现状")
    print(result.final_output)


asyncio.run(main())
```

要点：

- `@function_tool` 的函数签名 + docstring 就是工具的 JSON schema，别写 `*args`。
- 同步场景用 `Runner.run_sync`；Streamlit 里用 `asyncio.run(...)` 或 `run_sync`。
- 多 agent：`handoffs=[handoff(other_agent)]`，或把 agent 当工具 `other.as_tool(tool_name=..., tool_description=...)`。
- 会话记忆：`SQLiteSession("thread-id", "memory.db")` 传给 `Runner.run(..., session=session)`。
- 结构化输出：`output_type=PydanticModel`，`result.final_output` 直接是对象。
- 护栏：`@input_guardrail` / `@output_guardrail`，抛 `InputGuardrailTripwireTriggered` 时给用户可读提示。
- 追踪：默认开启 tracing；不想要就设 `OPENAI_AGENTS_DISABLE_TRACING=1`。

## Google ADK

安装：`pip install google-adk`

目录要求：

```text
my_agent/
├── __init__.py       # from . import agent
└── agent.py          # 必须暴露 root_agent
```

```python
from google.adk.agents import LlmAgent


def get_weather(city: str) -> dict:
    """Get the current weather for a city.

    Args:
        city: City name, e.g. "Shanghai".

    Returns:
        A dict with status and a human-readable report.
    """
    return {"status": "success", "report": f"{city}: 22°C, clear"}


root_agent = LlmAgent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="Answers weather questions for a city.",
    instruction=(
        "你是天气助手。用户问天气时调用 get_weather；"
        "没给城市就先问城市。回答不超过 3 句。"
    ),
    tools=[get_weather],
)
```

运行：

```bash
adk web .          # 浏览器调试
adk run my_agent   # 终端单轮
```

要点：

- 工具函数返回 `dict`，ADK 会原样交给模型；错误也做成 `{"status": "error", "error_message": "..."}`。
- 多 agent：`LlmAgent(..., sub_agents=[researcher, writer])`，父 agent 通过 `transfer_to_agent` 转交。
- 固定流程：`SequentialAgent(sub_agents=[...])`；并行：`ParallelAgent`；循环：`LoopAgent(max_iterations=3)`。
- 会话/状态：`tool_context.state` 存中间结果，不要塞进 instruction。
- 认证：`GOOGLE_API_KEY`（AI Studio）或 `GOOGLE_GENAI_USE_VERTEXAI=true` + GCP 凭据。

## Agno

安装：`pip install agno`

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools


agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    description="A concise market research assistant.",
    instructions=[
        "先搜索再回答，至少引用 2 个来源。",
        "输出 Markdown：结论 / 证据 / 风险。",
        "找不到就直说找不到。",
    ],
    markdown=True,
)

agent.print_response("2026 年 AI agent 框架的格局", stream=True)
```

多 agent：

```python
from agno.team import Team

team = Team(
    name="Research Team",
    model=OpenAIChat(id="gpt-4o-mini"),
    members=[web_agent, finance_agent],
    markdown=True,
)
team.print_response("对比 NVDA 和 AMD 的估值", stream=True)
```

服务化：

```python
from agno.os import AgentOS

agent_os = AgentOS(teams=[team])
app = agent_os.get_app()
# uvicorn module:app --reload
```

要点：

- `instructions` 是 list，比一坨字符串更好改；`description` 是给团队路由看的。
- 内置工具很多（DuckDuckGo、YFinance、SQL、文件）；先查有没有，别自己写。
- 记忆：`db=SqliteDb(db_file="agents.db")` + `add_history_to_context=True`。
- `Agent.run()` 返回对象，取 `.content`；流式用 `stream=True`。

## CrewAI

安装：`pip install crewai`

```python
from crewai import Agent, Crew, Process, Task

researcher = Agent(
    role="Market Researcher",
    goal="Find three credible sources about {topic}",
    backstory="You verify claims against primary sources.",
    verbose=True,
)

write_task = Task(
    description="Write a 300-word brief about {topic} using the research.",
    expected_output="Markdown with 3 sections and a source list.",
    agent=researcher,
)

crew = Crew(agents=[researcher], tasks=[write_task], process=Process.sequential)
print(crew.kickoff(inputs={"topic": "AI agents"}))
```

要点：`role/goal/backstory` 是路由和语气的主要来源；`expected_output` 必须具体，否则任务验收不了。适合角色清晰的固定流水线，不适合需要动态分支的流程。

## LangGraph

安装：`pip install langgraph`

```python
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode([search_knowledge]))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")
graph = builder.compile()
result = graph.invoke({"messages": [("user", "查一下 X")]})
```

要点：状态显式、可持久化（checkpointer）、可中断（`interrupt_before`）。只有需要「回到某一步」「人工审批后继续」时才值得上。

## Pydantic AI

安装：`pip install pydantic-ai`

```python
from pydantic import BaseModel

from pydantic_ai import Agent


class Ticket(BaseModel):
    title: str
    priority: int
    tags: list[str]


agent = Agent("openai:gpt-4o-mini", output_type=Ticket)


@agent.tool_plain
def lookup_order(order_id: str) -> str:
    """Look up an order by id."""
    return "not found"


ticket = agent.run_sync("客户说退款三天没到账，订单 A123").output
```

要点：`output_type` 直接给 Pydantic 模型，校验失败会自动重试；适合抽取、分类、表单填充。

## 换模型 / 换网关

所有框架都支持 OpenAI 兼容端点（DeepSeek、Qwen、GLM、vLLM、OneAPI 等），只是写法不同：

| 框架 | 写法 |
|---|---|
| OpenAI Agents SDK | `OpenAIChatCompletionsModel(model="deepseek-chat", openai_client=AsyncOpenAI(base_url="https://api.deepseek.com/v1", api_key=...))` |
| Agno | `OpenAILike(id="deepseek-chat", base_url="https://api.deepseek.com/v1", api_key=...)` |
| ADK | `LiteLlm(model="openai/deepseek-chat", api_base=..., api_key=...)`（需 `pip install litellm`） |
| CrewAI | 环境变量 `OPENAI_API_BASE` + `OPENAI_MODEL_NAME` |
| LangGraph | `ChatOpenAI(model=..., base_url=..., api_key=...)` |
| Pydantic AI | `Agent(OpenAIModel("deepseek-chat", base_url=..., api_key=...))` |

注意：

- 兼容端点不一定支持 function calling、JSON schema、流式工具调用。先跑一个带工具的冒烟用例。
- 模型 id 一律放 `AGENT_MODEL` 环境变量，不要写死在代码里。
- 便宜模型做路由/摘要，贵模型做最终写作，是常见组合；但先证明单模型不够。

## 运行面

| 面 | 适合 | 入口 |
|---|---|---|
| CLI | 本地验证、脚本调用 | `python run.py "..."` |
| Streamlit | 演示、非技术用户 | `streamlit run app.py` |
| FastAPI | 被其它系统调用、定时触发 | `uvicorn scheduler:app --reload` |
| ADK Web | ADK 调试 | `adk web .` |
| AgentOS | Agno 自带 API + UI | `agent_os.serve(...)` |

先做 CLI，再做 UI。UI 只负责收集输入和展示输出，不放业务逻辑。
