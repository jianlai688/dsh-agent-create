# Agent 模式卡

选模式的唯一标准：**能说清楚单 agent 缺哪一步**。说不清就留在单 agent。

> 脚手架里的 `--pattern multi` 是 P3 的最小骨架（coordinator + researcher + writer）。要做 P2，把 coordinator 的 handoff 目标换成按意图划分的专家即可，结构不变。

## 目录

- [怎么选](#怎么选)
- [P1 单 agent + 工具](#p1-单-agent--工具)
- [P2 意图路由](#p2-意图路由)
- [P3 编排者 + 工人](#p3-编排者--工人)
- [P4 生成 + 校验](#p4-生成--校验)
- [P5 检索增强](#p5-检索增强)
- [P6 always-on](#p6-always-on)
- [P7 人在环里](#p7-人在环里)
- [组合规则](#组合规则)
- [反模式](#反模式)

## 怎么选

按顺序问：

1. 一次输入、一次输出能完成吗？→ 能：**P1**。
2. 需要按用户意图分到不同专家吗？→ 是：**P2**。
3. 有可命名的多个阶段（先查再写、先计划再执行）吗？→ 是：**P3**。
4. 输出有硬标准、值得返工吗？→ 是：**P4**。
5. 答案依赖私有文档/数据库吗？→ 是：**P5**（P1 加一个检索工具）。
6. 触发不是人点按钮，而是时间或事件吗？→ 是：**P6**。
7. 执行前需要人批准吗？→ 是：**P7**。

一个项目最多组合两个模式。三个以上说明还没想清楚任务边界。

## P1 单 agent + 工具

**适用**：一件事、步骤固定、单轮或短多轮；问答、提取、改写、查询、生成初稿。

**最小结构**

```text
输入 → agent(instructions + tools) → 输出
```

```python
agent = Agent(
    name="...",
    instructions="角色/目标/步骤/输出格式/边界",
    tools=[search, calculate],
)
result = run(agent, user_input)
```

**要点**

- 工具 1~5 个；超过 8 个模型会选错。
- 指令里写清楚「什么时候用哪个工具」，不要只靠工具名。
- 输出格式写死：字段、长度、是否 Markdown。

**失败模式**

- 工具描述互相重叠 → 模型反复试错。合并或删掉一个。
- 指令写成散文 → 每次输出结构不同。改成编号步骤 + 模板。
- 把所有上下文塞进 prompt → 贵且慢。先检索再拼。

**仓库例子**：`starter_ai_agents/ai_data_analysis_agent`（Agno + DuckDB + Streamlit）、`starter_ai_agents/ai_travel_agent`。

## P2 意图路由

**适用**：3~5 类明确不同的请求，每类需要不同工具或知识；客服分流、售前/售后、查询/办理。

**最小结构**

```text
用户输入 → 路由 agent（只做分类 + 转交）
              ├→ 专家 A（工具 A）
              ├→ 专家 B（工具 B）
              └→ 兜底专家（问清需求）
```

- OpenAI Agents SDK：`handoffs=[handoff(a), handoff(b)]`
- Google ADK：`root_agent = LlmAgent(..., sub_agents=[a, b])`
- Agno：`Team(members=[a, b])`

**要点**

- 每个专家的 `description` 写「接什么、不接什么」，这是路由的唯一依据。
- 必须有兜底：路由不确定时问一个澄清问题，不要硬猜。
- 路由 agent 不调用业务工具，只分类和转交。

**失败模式**

- 两个专家职责重叠 → 来回 handoff。用一句话能区分开才拆。
- 没有兜底 → 模型随便选一个，错得还很自信。
- 路由层也写长指令 → 增加延迟，不提升准确率。

**仓库例子**：`starter_ai_agents/openai_research_agent`（triage → research → editor）。

## P3 编排者 + 工人

**适用**：多来源检索、长报告、需要并行或分工的多阶段任务；研究、竞品分析、尽调。

**最小结构**

```text
planner → 产出结构化计划（子问题/查询列表）
   ↓
workers（并行，各自带工具）→ 各自产出带来源的事实
   ↓
synthesizer → 去重、排序、按模板成文
```

```python
plan = planner.run(task)                 # JSON: {"queries": [...], "sections": [...]}
facts = await asyncio.gather(*[worker.run(q) for q in plan.queries])
report = writer.run(render(facts, plan.sections))
```

**要点**

- 计划必须是结构化对象（Pydantic / JSON schema），不要自由文本。
- 工人只负责「找 + 摘」，不写成文；写作留给一个 writer。
- 事实表带 `source` 字段；汇总时丢来源等于不可信。
- 并发上限 3~5，失败重试 1 次。

**失败模式**

- 工人重复搜同一来源 → 去重按 URL/标题，不按文本相似度。
- 计划太细（20 个子问题）→ 成本爆炸。限制 3~7 个。
- writer 拿到一堆原文 → 超上下文。先压缩成事实卡片。

**仓库例子**：`advanced_ai_agents/single_agent_apps/ai_deep_research_agent`、`.../agent_teams/ai_vc_due_diligence_agent_team`。

## P4 生成 + 校验

**适用**：输出有明确验收标准且返工便宜；代码、翻译、结构化报告、合规文案。

**最小结构**

```text
generator → draft
   ↓
critic（按 rubric 逐条打分，只输出问题清单）
   ↓ 未通过且轮次 < 2
generator（带问题清单重写）
   ↓ 通过
输出
```

**要点**

- rubric 必须可判定：字段齐全 / 数字有来源 / 长度 ≤ N / 无禁用词。
- critic 只列问题，不改稿；否则两个模型互相覆盖。
- 最多 2 轮；第 3 轮还不通过就输出「未达标 + 原因」，不要无限循环。

**失败模式**

- critic 说「可以更好」→ 没有信息量。要求引用具体句子 + 违反的规则编号。
- 没有通过阈值 → 永远在改。预先写「全部 rubric 通过即停」。

**仓库例子**：`advanced_ai_agents/single_agent_apps/ai_deep_research_agent`（research → elaboration 两段）。

## P5 检索增强

**适用**：答案在私有文档、工单、数据库里；需要引用；知识会更新。

**最小结构**

```text
文档 → 切块（300~800 字，带标题路径）→ 向量/关键词索引
问题 → agent 改写成 1~3 条查询 → 检索 top-k → 重排 → 带引用回答
```

**要点**

- 检索是代码，不是 agent 的自由发挥；agent 只决定查什么。
- 切块保留标题和来源路径，否则引用无法回溯。
- 没命中就回答「资料里没有」，不要用模型记忆补。
- 先做关键词/BM25 基线，再加向量；混合检索通常更稳。

**失败模式**

- 把整个知识库塞进 prompt → 贵、慢、还会漏。
- 只做向量、不做重排 → 相似但不相关的块排前面。
- 引用写成「根据文档」→ 不可验证。必须带文件名 + 段落。

**仓库例子**：`rag_tutorials/local_rag_agent`、`rag_tutorials/hybrid_search_rag`、`rag_tutorials/knowledge_graph_rag_citations`。

## P6 always-on

**适用**：定时简报、监控告警、发布雷达、每日汇总。触发来自 cron / webhook / 队列，不是用户点按钮。

**最小结构**

```text
cron / webhook → collector（拉数据）→ ranker（打分）→ agent（写简报）
   → deliver（邮件/Slack/webhook，默认 dry-run）→ state（去重、上次运行）
```

**要点**

- 默认 `dry_run=True`；只有显式 `--live` / `"dry_run": false` 才真的发送。
- 状态文件记录 `seen_ids`、`last_run`、`delivery_status`，否则每天重复推送。
- 失败要能被看见：返回非 2xx，或写一条 `status=failed`，不要静默。
- 输出同时给文本和 HTML/JSON，方便接不同渠道。

**失败模式**

- 没有去重 → 同一批内容天天推。
- 抓取失败当成「今天没有新闻」→ 用户以为风平浪静。
- 调度器和 agent 耦合在一个进程 → 重跑会重复发送。

**仓库例子**：`always_on_agents/always_on_hn_briefing_agent`（ADK + FastAPI + dry-run + Gmail/webhook）、`always_on_agents/release_radar_agent`。

## P7 人在环里

**适用**：有副作用且不可逆：发邮件、退款、下单、改生产数据、提交代码。

**最小结构**

```text
agent 准备动作（参数 + 影响范围 + 回滚方式）
   ↓
展示给人 → 批准 / 修改 / 拒绝
   ↓ 批准
执行器（幂等键 + 超时 + 审计日志）
```

**要点**

- 审批界面必须显示「将对谁做什么、影响多少条、能否撤销」。
- 执行器用幂等键，重试不会重复下单。
- 拒绝也要记录，作为后续评测样本。

**失败模式**

- 先执行再让用户确认 → 已经晚了。
- 审批只显示「是否继续」→ 用户不知道在批准什么。

**仓库例子**：`advanced_ai_agents/multi_agent_apps/trust_gated_agent_team`。

## 组合规则

- **agent 数量 ≤ 3**（不含路由兜底）。每多一个，就多一处指令、工具和失败点。
- **一个 agent 只干一件事**；「又查又写又审」拆成三个。
- **共享状态显式化**：用 `facts: list[dict]` 传，不靠聊天历史传递。
- **预算硬编码**：`max_turns=10`、`max_tool_calls=20`、单次超时 60s。
- **每个 handoff 写清边界**：接什么、不接什么、缺信息时问谁。

## 反模式

| 反模式 | 症状 | 改法 |
|---|---|---|
| 为多而多 | 3 个 agent 做一个总结 | 回 P1，单 agent + 一个工具 |
| 路由当装饰 | 所有请求都进同一个专家 | 删掉路由，直接调专家 |
| 让 agent 做算术 | 数字每次不一样 | 用代码算，agent 只解释 |
| 用聊天历史当状态 | 多轮后丢关键字段 | 显式 state / 数据库 |
| 无限反思 | 成本和延迟不可控 | 最多 2 轮 + 通过阈值 |
| 工具返回整页 HTML | 上下文爆炸 | 工具内清洗成 ≤2k 字摘要 |
| 没有兜底 | 异常输入直接崩 | 默认分支 + 澄清问题 |
