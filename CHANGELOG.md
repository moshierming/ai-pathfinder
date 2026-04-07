# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [1.9.0] — 2026-04-07

### Added
- **新增 5 个高质量资源**：
  - r106: Anthropic Prompt Engineering 官方指南（高级提示工程技巧）
  - r107: DSPy 编程式 Prompt 优化框架（Stanford NLP）
  - r108: OpenAI Structured Outputs 指南（JSON Schema 约束输出）
  - r110: Simon Willison's Weblog（工程师视角的 LLM 工具链跟踪）
  - r112: AI Engineering 路线图（Chip Huyen 对 AI 工程角色的定义）
- **新增 2 个 Builders**：
  - b025: Simon Willison（Django 联合创始人，LLM 工具链深度跟踪者）
  - b026: Chip Huyen（《AI 工程》作者，AI Engineering 角色定义者）

### Changed
- **内容策略对齐（"前沿跟踪+工程实践"定位）**：
  - r037（吃瓜教程）、r067（南瓜书）、r103（李航统计学习方法）标记 `priority: supplementary`
  - r034（Kaggle Learn）标记 `priority: supplementary`（传统 ML 入门）
  - r077（The Batch）话题更新：overview → industry-trends/ai-news
  - r086（Latent Space）话题更新：overview → ai-engineering/industry-trends
  - r010（d2l.ai）合并 r061 的更好描述，扩展 topics，时长 60→80h
- **全库标签审计**：验证 128 条活跃资源的 focus/priority 准确性

### Fixed
- r061 标记 `deprecated: true`（与 r010 URL 重复：zh.d2l.ai）
- r109、r111 标记 `deprecated: true`（与 r086、r077 URL 重复）

> 🤖 由 AI Agent 自动维护（关联 Issue #28 后续）

## [1.8.0] — 2026-04-06

### Changed
- **System Prompt 重构**（关联 Issue #28）：
  - 移除"前1/3基础"固定分配规则，改为根据用户水平动态选择起点
  - 新增"内容优先级规则"：`priority=supplementary` 资源仅推荐给零基础用户
  - 非零基础用户路径以 AI 核心技能为主线（LLM→Prompt→RAG/Agent→部署）
  - 基础补充限制在总路径 15% 以内
- **resources.yaml 内容策略调整**：
  - r037（吃瓜教程）、r067（南瓜书）focus 从 `foundational` 改为 `both`（中高级 ML 理论不应被视为"可跳过的基础"）
  - r001-r007（Python/数学/传统ML入门）新增 `priority: supplementary` 字段，标记为补充性资源

> 🤖 由 AI Agent 自动维护

## [1.7.3] — 2026-04-06

### Fixed
- **E2E 测试环境隔离**：`tests/e2e/conftest.py` 启动 Streamlit 子进程时剥离 `GITHUB_TOKEN`，防止 Playwright 测试通过 feedback 表单创建真实 GitHub Issues
  - 根因：`gh` CLI 注入的 GITHUB_TOKEN 被 `os.environ.copy()` 继承，导致 E2E 跑 feedback 流程时产生垃圾 Issues（#5-#16, #29-#33）

### Changed
- **AGENTS.md 经验固化**：
  - 新增"E2E 测试环境隔离"规范章节（含必须剥离的变量清单和教训来源）
  - Issue 关闭机制新增"逐个检查"强制规则（教训：曾误关用户真实反馈 Issue #28）
  - 反馈驱动策略反思表新增"测试产生真实副作用"信号行

> 🤖 由 AI Agent 自动维护

## [1.7.2] — 2026-04-06

### Added
- **产品愿景文档**（`VISION.md`）：系统化定义产品信念、核心用户画像、差异化定位、设计原则（6 条）、成功指标（短中长期）、架构哲学、文档体系
- **内容质量管理机制**：
  - `CONTENT_QUALITY.md`：内容质量管理策略（六维度：完整性、新鲜度、准确性、覆盖度、去重、描述质量）
  - `scripts/audit_content.py`：自动化内容审计脚本，支持字段完整性、URL 去重、描述质量、覆盖度分析、链接检测（`--check-links`）、新鲜度跟踪
  - `resources.yaml` 新增 `deprecated` 字段支持：弃用资源不再出现在推荐中
  - `resources.yaml` 新增 `verified_date` 字段支持：追踪资源验证时效性
  - 进化流程新增内容审计步骤（AGENTS.md 第3步）
  - EVOLUTION.md 新增"内容质量红线"章节

### Fixed
- **资源去重**：r062 与 r011 URL 完全相同（李沐论文精读系列），r062 标记 `deprecated: true`，r011 合并更完整的描述和标签
- **文档数据同步**：README 资源数量、测试数量、项目结构等信息与实际不符（129→128、105→104、240→244 等多处），统一更新
- **文档信息碎片化**：README 和 CONTRIBUTING.md 缺少对治理体系（EVOLUTION.md / CONTENT_QUALITY.md / AGENTS.md）的交叉引用，已补充
- **CONTRIBUTING.md 过时信息**：资源 schema 缺少 `verified_date` 字段说明、测试数量/视图模块数量不准确，已更新

### Changed
- `app.py` 的 `load_resources()` 自动过滤 `deprecated: true` 的资源
- **README 重构**：从"功能列表优先"改为"Why → Who → What"结构，开头阐述产品信念和用户画像，功能列表后移
- README 新增"项目治理"章节（含 VISION.md），整合治理文档入口
- CONTRIBUTING.md 新增"项目治理"章节，指引贡献者了解约束和质量标准
- AGENTS.md 必读文件新增 `CONTENT_QUALITY.md`
- AGENTS.md 安全分级表明确标注权威来源为 `EVOLUTION.md`
- EVOLUTION.md 添加 VISION.md 交叉引用

> 🤖 由 AI Agent 自动维护

## [1.7.1] — 2026-04-06

### Added
- **自进化基建**：搭建 AI Agent 自主进化体系
  - `EVOLUTION.md`：进化宪法，定义不可变原则、变更安全分级（Safe/Moderate/Dangerous）、质量红线
  - `AGENTS.md` 增强：自进化协议、周期、流程、安全分级判定标准、约束检查清单
  - `.github/ISSUE_TEMPLATE/feedback.md`：通用反馈模板，对接 App 内反馈和社区建议
  - `.github/labels.yml`：标签体系定义（ai-safe/ai-moderate/ai-dangerous/ai-done）

### Fixed
- **Chat 重复清空按钮** (#3)：`render_chat()` 底部有两个同名 `chat_clear` 按钮，导致 DuplicateWidgetID 错误，删除重复项
- **Chat 流式响应 AttributeError** (#3)：某些 LLM provider 返回的 delta 无 `content` 属性时，使用 `getattr` 安全访问 + `str()` 防御
- **Chat 页面 None profile 崩溃** (#3, #12)：`st.session_state.profile` 为 `None` 时，`get("profile", {})` 返回 `None` 而非空字典，导致 `.get("direction")` 抛 AttributeError。修复为 `(get("profile") or {})`
- **反馈 Issue 来源标识**：GitHub Issues 自动创建的反馈顶部增加 bot 标识，区分自动反馈和维护者操作
- **路径持久化** (#4)：路径生成后自动保存到本地，下次打开应用自动恢复上次的学习路径和进度
- **路径生成非阻塞** (#13)：路径生成改为后台线程执行，LLM 流式调用期间用户可自由切换到其他页面（对话、资源浏览等），生成完毕后回到路径页即可查看结果
- **secrets.toml 缺失崩溃**：`get_llm_config()` 调用 `st.secrets.get()` 在无 `secrets.toml` 文件时抛 `StreamlitSecretNotFoundError`，改为安全的 `_secret()` 包装函数

### Changed
- **import_plan.py 国际化**：7 处硬编码中文标签迁移到 i18n.py，英文模式下正确显示

> 🤖 由 AI Agent 首轮自进化完成

## [1.7.0] — 2026-03-24

### Added
- **Chat 跟进建议**：每次 AI 回复后显示 2-3 个上下文相关的跟进问题按钮，覆盖 9 类话题 + 通用回退
- **Chat 清除 + 导出**：新增「🗑️ 清空对话」按钮和「📥 导出对话」Markdown 下载
- **资源浏览器"已在路径中"标记**：用户已生成路径时，浏览器中属于路径的资源显示 `📌 已在路径中` 标记

### Changed
- **i18n 内联字符串迁移**：12 个 `if L=="zh" else` 模式统一迁入 i18n.py，含新鲜度/分享/关注/排序/重试等
- **README 更新**：测试徽章 234→240

### Fixed
- **i18n bug：`path_week_no_resources`**：英文模式下绕过 `t()` 函数直接硬编码字符串，已修正为正确的 `t()` 调用

### Tests
- 测试数: 236 → 240 (+4)
- 新增: `TestChatFollowUps`（关键词匹配、通用回退、数量限制）

## [1.6.0] — 2026-03-24

### Added
- **行业大牛追踪 (Builders)**：新增 24 位 AI 领域核心建设者（13 位国际 + 11 位中文），涵盖研究员/工程师/创始人/教育者四种角色，每人附带社交平台链接（X/GitHub/B站/知乎等）
- **个性化趋势洞察**：趋势雷达基于用户学习方向（如 Agent/LLM/研究）生成定制化洞察，LLM Prompt 针对方向深度优化
- **"为你推荐"信息筛选**：信息源和大牛按用户方向智能排序，相关内容优先展示
- **Builders 社交链接卡片**：每位大牛有独立卡片，展示角色标签、简介和多平台快速跳转链接
- **方向感知缓存**：洞察缓存现按方向+日期双维度区分，切换方向时自动刷新
- **路径生成 Prompt 质量深化**：SYSTEM_PROMPT 增加 5 条教学规则（逻辑闭环、双重曝光、Builder 融入、具体 Tips、资源描述摘要）
- **路径 Builder 推荐**：LLM 在每周规划中可选择性推荐相关 builders，路径视图渲染"👤 推荐关注"链接
- **Chat Builder 知识**：聊天上下文独立呈现 builders 段落（含 role + description），CHAT_SYSTEM_PROMPT 新增推荐大牛规则
- **Chat 推荐问题引导**：空聊天时显示 4 个个性化推荐问题按钮
- **Chat 流式响应**：`stream=True` + `st.write_stream()`，文字逐字流出，消除等待黑洞
- **Chat 清除 + 导出**：新增清空对话按钮和 Markdown 导出下载
- **Markdown 导出 Builder 信息**：每周末尾输出 `👤 推荐关注: [name](url)` builder 推荐
- **路径每周时间预算对比**：expander 标题显示时间小计 + 预算比 (✅/⚠️)
- **路径预计完成日期**：根据 `estimated_weeks` 自动计算并显示目标完成日期
- **路径分享链接**：路径顶部显示可复制分享 URL
- **路径 ID 幻觉清洗**：`generate_path()` 后处理移除 LLM 编造的不存在资源/大牛 ID，并记录日志
- **路径资源缺失警告**：当整周资源全部无法匹配时显示友好提示
- **趋势洞察新鲜度指示器**：🟢刚刚/🟢N分钟/🟡N小时/🔴超1天
- **资源浏览器排序**：5 种排序方式（默认/难度↑↓/时长↑↓）
- **资源浏览器 Builder 统计**：统计面板新增"👤 大牛"计数卡片
- **路径 JSON 结构验证**：`_validate_path()` 确保 LLM 返回完整数据结构，自动填充缺失字段
- **LLM JSON 容错**：`_extract_json()` 处理 markdown code block 包裹的 JSON；空响应友好报错
- **路径生成重试按钮**：失败后 🔄 重试，保持用户画像

### Changed
- **趋势雷达页面重构**：页面结构从"洞察→信息源→新手指南"升级为"个性化洞察→大牛推荐→信息源→新手指南"
- **资源过滤器**：`filter_resources_for_direction()` 自动排除 builder 类型
- **PRESET_DESCRIPTIONS 去重**：config.py 作为唯一真实来源，form.py 导入使用
- **侧边栏动态底栏**：资源和大牛数量从实际数据动态计算
- **i18n 内联字符串迁移**：~12 个 `if L == "zh" else` 模式迁入 i18n.py，含新鲜度/分享/关注/排序等
- **`_compact_resources()`**：输出增加 `lang` 和 `desc[:30]` 字段
- **Analytics 防御**：`total_hours` / `w_hours` 排除 builder 类型，使用 `.get(duration_hours, 0)` 防御
- **Export 防御**：Markdown 导出中 `duration_hours` 使用 `.get()` 避免 builder 类型 KeyError

### Fixed
- **i18n bug**：`path_week_no_resources` 在英文模式下绕过 `t()` 函数直接硬编码，已修正
- **Chat `<think>` 标签泄漏**：流式响应后 `_strip_thinking()` 后处理清理 Qwen-3 思考标签
- **Chat 消息防膨胀**：消息列表超 100 条自动裁剪；UI 只渲染最近 50 条；用户输入超 2000 字截断
- **空资源降级**：资源过滤结果为空时降级使用全部资源生成路径
- **CI 资源验证适配 Builder**：验证脚本按 `type` 区分必填字段

### Tests
- 测试数: 209 → 236 (+27)
- 新增：builder 完整性、个性化洞察、方向缓存、radar 渲染、chat builder 集成、export builder、_validate_path、_extract_json、路径 ID 幻觉清洗、路径预计完成日期

## [1.5.0] — 2026-03-24

### Changed
- **路径生成速度优化**：全链路提速，目标 <30s 完成
  - 资源过滤：35 → 20 条 (-43% input tokens)
  - SYSTEM_PROMPT：796 → 396 chars (-50%)，合并冗余规则
  - max_tokens：2500 → 1500 (-40% output tokens)
  - temperature：0.3 → 0.15，更确定性输出
  - compact 格式：去除 domain 字段，topics 3→2，进一步压缩
- **路径缓存**：基于画像+资源 SHA256 哈希的 session 级缓存，相同画像再次生成秒回
- **超时保护**：OpenAI client 25s hard timeout，防止无限等待
- **流式进度反馈**：生成过程中实时显示已接收字符数，改善等待体验

## [1.4.0] — 2026-03-24

### Changed
- **Type Hints 现代化**：全部 16 个源文件、24 个函数签名升级为 `dict[str, object]` / `list[dict[str, object]]` 精确类型注解，替代原有的裸 `dict` / `list[dict]`
- **类型风格统一**：配合 `from __future__ import annotations` 使用 PEP 604 `X | None` 语法，零 `typing` 模块导入

## [1.3.0] — 2026-03-24

### Fixed
- **趋势洞察崩溃防护** (Issue #2)：`generate_trend_insights()` 全函数 try/except 包裹，防止 `get_llm_config()` 异常导致整页崩溃；LLM 返回 JSON 增加 isinstance 类型校验；radar 视图增加异常捕获 + error state
- **UI 颜色对比度** (Issue #1)：h1 渐变色、Metric 值、侧边栏文字等 7 处颜色对比度修复，全部达到 WCAG AA 标准 (4.5:1+)
- **UI 对齐问题** (Issue #1)：预设模板卡片改为固定高度 80px，消除内容长度差异导致的高度不一致

### Changed
- **Python 最低版本**：`requires-python` 从 `>=3.9` 提升到 `>=3.10`，新增 Python 3.13 classifier
- **现代化注解**：全部 16 个源文件添加 `from __future__ import annotations`
- **文字可读性**：小字体从 0.72/0.75rem 提升到 0.78rem，低对比度颜色全部替换为更深色值

## [1.2.0] — 2026-03-24

### Added
- **趋势雷达 AI 洞察**：LLM 生成每日 AI 趋势报告（5-7 条结构化洞察 + 行动建议），本地 JSON 缓存每日刷新，支持手动刷新
- **SECURITY.md**：安全策略文档 — 漏洞报告流程 + 已实施的安全措施
- **FUNDING.yml**：GitHub Sponsors 赞助配置

### Changed
- **路径生成性能优化**：资源格式从 JSON indent=2 切换为管道分隔紧凑格式（token 减少 ~60%），启用 streaming 流式输出，资源上限 50→35
- **README 徽章升级**：新增 CI 状态 / Release 版本 / Docker / 测试数量 / LLM 提供商数量共 6 个徽章
- **README 架构图更新**：补全 logging_config / progress / e2e 等新模块，测试数 113→138
- **进度指示器**：`st.spinner` → `st.status`，显示运行状态

## [1.1.0] — 2025-07-17

### Added
- **LLM 提供商扩展**：从 4 家扩展到 9 家（新增 Google Gemini / SiliconFlow / Moonshot / ZhipuAI / Ollama）
- **监控日志系统**：RotatingFileHandler（5MB×3），关键路径日志覆盖 LLM / Chat / Feedback / Progress
- **E2E 测试框架**：Playwright + 10 个核心流程测试（导航/资源/语言/预设），CI 独立 Job
- **进度持久化**：保存/恢复学习进度（勾选+对话），服务端存储+下载，侧边栏自动恢复

### Changed
- **代码精炼**：`_lang()` 统一到 `views/__init__.py`，消除 10 处重复定义，净减 20 行

### Security
- **XSS 防护**：LLM 输出 `html_escape` 转义
- **输入校验**：目标文本上限 1000 字符，导入文件上限 2MB，Profile 解码上限 50KB

## [1.0.0] — 2025-01-26

### Added
- **模块拆分架构**：app.py 1379→196 行，拆分为 12 个独立模块（config/llm/utils/i18n + 8 个 views）
- **113 个自动化测试**：覆盖 config/utils/llm/views，CI 自动运行
- **Docker 部署**：Dockerfile + docker-compose + .dockerignore
- **资源库 105 条**：新增 AIGC/MLOps/经典书籍/视频（原 90 条）
- **8 个预设模板**：AIGC / MLOps / Research / 零基础（原 4 个）
- **开源规范**：CONTRIBUTING.md + CODE_OF_CONDUCT.md + Issue/PR 模板
- **pyproject.toml 完善**：v1.0.0 元数据 + pytest 配置 + dev 依赖
- **CI/CD**：GitHub Actions 添加 pytest 步骤 + 全模块语法检查
- **README**：项目架构图 + 测试运行说明 + Docker 部署指南

## [0.9.0] — 2025-01-25

### Added
- **中英文双语界面**：侧边栏一键切换，170+ 条翻译条目（i18n.py）
- **学习路径可视化**：类型/侧重/节奏/话题覆盖三维度图表
- **UI/UX 美化**：渐变主题、卡片阴影、统计面板配色
- **35 个单元测试**：i18n/编码/筛选/导出/常量

## [0.8.0] — 2025-01-24

### Added
- **智能对话（AI Chat）**：上下文感知画像和路径的问答助手
- **README 全面更新**：反映智能对话/可视化/双语/美化功能

## [0.7.0] — 2025-01-23

### Added
- **Focus 维度**：打基础 / 重实战 / 均衡，LLM 据此调整资源推荐
- **Channel 信息源**：15 个持续学习渠道（博客/Newsletter/播客/公众号）
- **导出 & 导入**：Markdown + JSON 格式导出，JSON 导入恢复计划
- **趋势雷达**：中英文 AI 信息源 + 前沿快速入口
- **资源库扩充至 90 条**：覆盖 8 个方向

## [0.6.0] — 2025-01-22

### Added
- **用户调研改进**：基于反馈的技能背景字段 + 实战项目搭配
- **SYSTEM_PROMPT 优化**：充分利用技能背景，强制实战项目

## [0.5.0] — 2025-01-21

### Added
- **预设模板**：4 个方向快速填写（软测/Agent/LLM/ML）
- **URL 状态持久化**：可分享/书签
- **10 条中文 AI 资源**（r061-r070）

### Fixed
- **P0 修复**：domain 标签 100% 覆盖 + 反馈→GitHub Issues + 方向预筛选

## [0.4.0] — 2025-01-20

### Added
- **资源库 60 条** + domain 标签 + 目标方向选择 + 自定义 API Key 设置
- **CI 工作流**：Python 3.10-3.12 语法检查 + 资源校验 + 失败告警

### Fixed
- form key 重命名避免 session_state 冲突
- datetime import 移至顶层

## [0.1.0] — 2025-01-19

### Added
- **MVP 初版**：基本画像填写 + LLM 路径生成 + 进度追踪
