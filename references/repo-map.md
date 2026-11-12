# 模板索引：awesome-llm-apps

来源：[Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)（Apache-2.0）。100+ 个可运行模板，按用途分成 12 类。**别从零写，先找同构模板。**

## 怎么取模板

```text
README:  https://raw.githubusercontent.com/Shubhamsaboo/awesome-llm-apps/main/<path>/README.md
主文件:  https://raw.githubusercontent.com/Shubhamsaboo/awesome-llm-apps/main/<path>/<file>.py
```

- 先读 README 的 Features / How It Works / How to Run，判断结构是否匹配。
- 再读主文件，只看三处：agent 怎么定义、工具怎么接、状态放哪里。
- 抄骨架和约定，不整目录复制；模板里的 key、模型名、示例数据都要换。
- 路径可能随仓库更新变化；404 就回 [README](https://github.com/Shubhamsaboo/awesome-llm-apps) 找新路径。

## 按需求找模板

| 你想要 | 模板 | 抄什么 |
|---|---|---|
| 最快跑通一个单 agent | `starter_ai_agents/ai_data_analysis_agent` | Agno + Streamlit + 文件上传 + 工具注入 |
| 三 agent 协作 + 结构化输出 | `starter_ai_agents/openai_research_agent` | triage/research/editor、Pydantic `output_type`、handoff |
| 多角色团队 + 内置工具 | `advanced_ai_agents/multi_agent_apps/agent_teams/ai_finance_agent_team` | Agno `Team` + `AgentOS` + SQLite 会话 |
| 定时简报 + 安全投递 | `always_on_agents/always_on_hn_briefing_agent` | ADK `root_agent` + FastAPI + `dry_run` + Gmail/webhook |
| 深度研究（多阶段） | `advanced_ai_agents/single_agent_apps/ai_deep_research_agent` | 搜索 → 初稿 → 增强，两段式 |
| 私有文档问答 | `rag_tutorials/local_rag_agent` | 本地向量库 + 引用 |
| 混合检索 | `rag_tutorials/hybrid_search_rag` | 关键词 + 向量，接 Claude |
| 带引用的知识图谱 RAG | `rag_tutorials/knowledge_graph_rag_citations` | 多跳检索 + 来源归因 |
| 浏览器自动化 | `mcp_ai_agents/browser_mcp_agent` | MCP + 真实浏览器 |
| 语音进语音出 | `voice_ai_agents/voice_rag_openaisdk` | OpenAI 实时语音 + RAG |
| 前端生成式 UI | `generative_ui_agents/generative-ui-starter-project` | 聊天驱动的交互组件 |
| 学框架 | `ai_agent_framework_crash_course/openai_sdk_crash_course` | 从 starter 到 handoff/guardrail/session |
| 学 ADK | `ai_agent_framework_crash_course/google_adk_crash_course` | LlmAgent、工具、memory、多 agent |
| 写 skill 而不是 app | `agent_skills/project-graveyard` | SKILL.md 结构、scripts/ + references/ 分工 |

## 分类清单

### Agent Skills（技能，不是 app）

- `agent_skills/project-graveyard` —— 扫描本地死项目并做尸检
- `agent_skills/first-reader` —— 模拟读者读稿，报告在哪失去兴趣
- `agent_skills/scope-creep-detector` —— 检查 diff 是否超出声明范围
- `agent_skills/commit-archaeologist` —— 从 git 历史还原一段代码的来龙去脉
- `agent_skills/dependency-doctor` —— 依赖清单体检
- `agent_skills/thinking-out-loud` —— 语音碎碎念整理成简报
- `agent_skills/self-improving-agent-skills` —— 用 eval 自动优化 skill

### Starter AI Agents（单文件、一个 key 能跑）

- `starter_ai_agents/ai_blog_to_podcast_agent` —— 博客 URL → 播客
- `starter_ai_agents/ai_breakup_recovery_agent` —— 多 agent 情感陪聊
- `starter_ai_agents/ai_data_analysis_agent` —— CSV/Excel 自然语言分析（Agno + DuckDB）
- `starter_ai_agents/ai_medical_imaging_agent` —— Gemini 读片
- `starter_ai_agents/ai_meme_generator_agent_browseruse` —— 浏览器操作生成梗图
- `starter_ai_agents/ai_music_generator_agent` —— 文本 → MP3
- `starter_ai_agents/ai_travel_agent` —— 行程规划
- `starter_ai_agents/ai_x402_paying_agent` —— 带钱包、按次付费的 agent
- `starter_ai_agents/multimodal_ai_agent` —— 视频分析 + 联网
- `starter_ai_agents/mixture_of_agents` —— 多模型回答 + 聚合
- `starter_ai_agents/openai_research_agent` —— 研究团队（Agents SDK）
- `starter_ai_agents/web_scraping_ai_agent` —— 描述要抓什么，agent 去抓
- `starter_ai_agents/xai_finance_agent` —— Grok 实时股票分析

### Advanced：单 agent

- `advanced_ai_agents/single_agent_apps/ai_deep_research_agent` —— Firecrawl 深度研究
- `advanced_ai_agents/single_agent_apps/ai_consultant_agent` —— 市场分析与策略
- `advanced_ai_agents/single_agent_apps/ai_system_architect_r1` —— DeepSeek R1 架构评审
- `advanced_ai_agents/single_agent_apps/ai_movie_production_agent` —— 一句话电影概念
- `advanced_ai_agents/single_agent_apps/ai_investment_agent` —— 股票对比报告
- `advanced_ai_agents/single_agent_apps/earnings_call_analyst_agent` —— 财报电话会分析
- `advanced_ai_agents/single_agent_apps/ai_health_fitness_agent` —— 饮食与训练计划
- `advanced_ai_agents/single_agent_apps/ai_fraud_investigation_agent` —— 公开记录交叉核查
- `advanced_ai_agents/single_agent_apps/ai_journalist_agent` —— 研究、写作、编辑
- `advanced_ai_agents/single_agent_apps/ai_meeting_agent` —— 会前简报
- `advanced_ai_agents/single_agent_apps/research_agent_gemini_interaction_api` —— 多阶段研究 + 信息图

### Advanced：多 agent / 团队

- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_competitor_intelligence_agent_team` —— 竞品拆解
- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_finance_agent_team` —— 金融分析团队
- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_game_design_agent_team` —— 游戏概念
- `advanced_ai_agents/multi_agent_apps/agent_teams/ag2_adaptive_research_team` —— AG2 路由 + 兜底
- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_legal_agent_team` —— 法律研究
- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_recruitment_agent_team` —— 招聘流水线
- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_real_estate_agent_team` —— 找房与市场分析
- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_services_agency` —— CrewAI 数字 agency
- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_teaching_agent_team` —— 学习路径
- `advanced_ai_agents/multi_agent_apps/agent_teams/multimodal_coding_agent_team` —— 拍照解题
- `advanced_ai_agents/multi_agent_apps/agent_teams/multimodal_design_agent_team` —— 设计评审
- `advanced_ai_agents/multi_agent_apps/agent_teams/multimodal_uiux_feedback_agent_team` —— 落地页反馈 + 改版
- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_travel_planner_agent_team` —— 行程团队
- `advanced_ai_agents/multi_agent_apps/agent_teams/llm_panel_agent_team` —— 三家模型盲评
- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_sales_intelligence_agent_team` —— 销售战卡
- `advanced_ai_agents/multi_agent_apps/agent_teams/ai_vc_due_diligence_agent_team` —— 投资尽调
- `advanced_ai_agents/multi_agent_apps/ai_home_renovation_agent` —— 照片 → 改造方案
- `advanced_ai_agents/multi_agent_apps/devpulse_ai` —— 技术信号日报
- `advanced_ai_agents/multi_agent_apps/ai_financial_coach_agent` —— 预算/债务/储蓄
- `advanced_ai_agents/multi_agent_apps/product_launch_intelligence_agent` —— 发布情报
- `advanced_ai_agents/multi_agent_apps/ai_mental_wellbeing_agent` —— 心理健康支持
- `advanced_ai_agents/multi_agent_apps/ai_self_evolving_agent` —— EvoAgentX 自改写
- `advanced_ai_agents/multi_agent_apps/ai_news_and_podcast_agents` —— 新闻 + 播客
- `advanced_ai_agents/multi_agent_apps/trust_gated_agent_team` —— 审计链 + 信任门

### Always-on

- `always_on_agents/always_on_hn_briefing_agent` —— HN 每日简报
- `always_on_agents/release_radar_agent` —— 依赖发布雷达

### Voice

- `voice_ai_agents/ai_audio_tour_agent` —— 位置驱动的音频导览
- `voice_ai_agents/customer_support_voice_agent` —— 基于自有文档的语音客服
- `voice_ai_agents/insurance_claim_live_agent_team` —— 实时理赔
- `voice_ai_agents/voice_rag_openaisdk` —— 语音问答 PDF

### Generative UI

- `generative_ui_agents/generative-ui-starter-project` —— 聊天驱动看板
- `generative_ui_agents/ai-financial-coach-agent` —— 财务卡片
- `generative_ui_agents/ai-dashboard-canvas-agent` —— 画布仪表盘
- `generative_ui_agents/ai-mcp-app-builder` —— 描述即 MCP app
- `generative_ui_agents/mcp-apps-generative-ui-showcase` —— 交互式 MCP UI
- `generative_ui_agents/ai-shadcn-component-generator` —— 生成 shadcn 组件
- `generative_ui_agents/ai-deep-research-agent` —— 工具调用渲染成卡片

### MCP

- `mcp_ai_agents/browser_mcp_agent` —— 自然语言开浏览器
- `mcp_ai_agents/github_mcp_agent` —— 用自然语言分析仓库
- `mcp_ai_agents/notion_mcp_agent` —— 与 Notion 对话
- `mcp_ai_agents/ai_travel_planner_mcp_agent_team` —— Airbnb/Google Maps
- `mcp_ai_agents/multi_mcp_agent_router` —— 多 MCP 专家路由
- `mcp_ai_agents/openai_remote_mcp_bridge` —— function calling → 远程 MCP
- `mcp_ai_agents/dependency_upgrade_advisor` —— 升级破坏面分析

### RAG

- `rag_tutorials/local_rag_agent` —— 全本地
- `rag_tutorials/hybrid_search_rag` —— 关键词 + 向量
- `rag_tutorials/agentic_rag_with_reasoning` —— 展示检索推理
- `rag_tutorials/autonomous_rag` —— 本地文档 + 联网兜底
- `rag_tutorials/corrective_rag` —— 自评检索质量并重试
- `rag_tutorials/knowledge_graph_rag_citations` —— 多跳 + 引用
- `rag_tutorials/multimodal_agentic_rag` —— 文本/PDF/图/音/视频
- `rag_tutorials/rag_failure_diagnostics_clinic` —— 诊断 RAG 失败
- `rag_tutorials/vision_rag` —— 图片与 PDF 页问答
- 其余：`rag_tutorials/` 下的 `rag_chain`、`llama3.1_local_rag`、`deepseek_local_rag_agent`、`gemini_agentic_rag`、`contextualai_rag_agent`、`agentic_typed_rag_pydanticai`

### 记忆

- `advanced_llm_apps/llm_apps_with_memory_tutorials/ai_arxiv_agent_memory`
- `advanced_llm_apps/llm_apps_with_memory_tutorials/ai_travel_agent_memory`
- `advanced_llm_apps/llm_apps_with_memory_tutorials/llama3_stateful_chat`
- `advanced_llm_apps/llm_apps_with_memory_tutorials/llm_app_personalized_memory`
- `advanced_llm_apps/llm_apps_with_memory_tutorials/local_chatgpt_with_memory`
- `advanced_llm_apps/llm_apps_with_memory_tutorials/multi_llm_memory`

### 框架课程

- `ai_agent_framework_crash_course/openai_sdk_crash_course` —— 11 课：starter → structured output → tools → sessions → guardrails → handoffs → orchestration → tracing → voice
- `ai_agent_framework_crash_course/google_adk_crash_course` —— ADK：工具、memory、callbacks、plugins、多 agent

## 仓库的共性约定

这些约定值得照抄，因为它们让项目「别人能跑」：

1. **一个模板一个目录**，目录名 kebab-case 或 snake_case，README 第一段说清「是什么 + 用了什么模型/框架」。
2. **`requirements.txt` 必带**；`pip install -r requirements.txt` 是唯一安装步骤。
3. **API key 走环境变量或侧边栏输入**，README 写清在哪申请、变量名叫什么。
4. **一个主入口**：`streamlit run xxx.py`、`python xxx.py` 或 `adk web`；README 的命令要能直接复制。
5. **UI 只做壳**：收集输入、显示中间步骤、给下载按钮；agent 逻辑在独立函数里。
6. **错误可见**：`try/except` 后 `st.error(...)`，不静默吞掉。
7. **示例输入**内置 3 条，降低第一次使用门槛。
8. **Agent Skills 用 `SKILL.md`**：frontmatter（name/description/license/metadata）+ `scripts/` 放确定性逻辑 + `references/` 放按需加载的长文 + `evals/` 放可执行评测。

## 从模板改造的步骤

1. 复制目录到新位置，改名为新项目。
2. 删掉模板特有逻辑（示例数据、特定 API、品牌文案）。
3. 保留：配置读取、错误处理、UI 骨架、README 结构。
4. 按本项目重写 instructions、工具、输出 schema。
5. 换掉 `requirements.txt` 里用不到的依赖。
6. 跑 `check_agent.py`，把模板遗留的 TODO 和硬编码清干净。
