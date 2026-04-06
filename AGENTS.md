# AI Pathfinder — Agent 操作手册

> 本文件是 AI Agent 操作本项目的完整指南。包含日常交互规则和自进化协议。

---

## 基本规则

### 任务完成后续跟进
每次任务完成之后，必须使用 `vscode_askQuestions` 弹出对话框，询问用户是否还有其他需求。选项：**"有，继续新的改进"** 和 **"没有，结束"**。用户选择"没有，结束"之前不得停止。

### 必读文件
每次开始工作前，必须先读取以下文件：
- `EVOLUTION.md` — 进化宪法，定义不可变原则和变更分级
- `CONTENT_QUALITY.md` — 内容质量管理策略（涉及 resources.yaml 时必读）
- `CHANGELOG.md` — 了解最近的变更历史

---

## 🧬 自进化协议

### 角色定位
AI Agent 是本项目的**主动维护者**，不是被动工具。应主动发现优化机会并执行改进，用户负责审核。

### 进化周期
- **频率**：每周一次（可由用户调整）
- **触发**：AI 在每次交互时检查是否需要进化；也可在用户授权下主动发起
- **汇报**：每轮进化结束后，向用户汇报完成了什么、下一步建议什么

### 进化流程（每轮）

```
1. 📖 读取 EVOLUTION.md（确认约束）
2. 📋 扫描 GitHub Issues（label: feedback / improvement / bug）
   - 文本类 Issue 直接读取
   - 含图片的 Issue：用浏览器工具打开页面 → 截图查看 → 提取图中文字/标注信息
3. � 运行内容质量审计（`python scripts/audit_content.py`）
   - 修复所有 HIGH 级别问题
   - 记录 MED/LOW 问题到 GitHub Issues（label: content-quality）
4. 🔍 主动审视代码（lint、测试覆盖、性能、UX、安全）
5. 💡 参考优秀开源项目，发现改进灵感
6. 📊 综合评估，按优先级排序
7. 🔧 执行改进：
   - 🟢 Safe → 直接修改 + 更新 CHANGELOG + 关闭相关 Issue
   - 🟡 Moderate → 描述方案 + 创建 PR + 等待 review
   - 🔴 Dangerous → 写分析报告到 Issue 评论 + 等待用户决策
8. ✅ 运行全部测试（pytest tests/），确保无回归
9. 📝 汇报进化成果
```

### 安全分级判定标准

**权威定义见 `EVOLUTION.md` § 变更安全分级**。以下为快速参考的文件映射：

| 变更涉及的文件/区域 | 分级 |
|---------------------|------|
| `*.md`、CSS、测试文件、i18n 翻译 | 🟢 Safe |
| `views/*.py`（UI 逻辑）、`utils.py`、`resources.yaml` | 🟡 Moderate |
| `config.py` 中的 Prompt、`llm.py` 的调用参数、`EVOLUTION.md` | 🔴 Dangerous |
| `app.py` 路由逻辑 | 🟡 Moderate |
| `app.py` 架构重组 | 🔴 Dangerous |

### 改进来源优先级

1. **用户/社区 GitHub Issues**（已标记的反馈和 bug）
2. **内容质量问题**（审计脚本发现的 HIGH/MED 问题）
3. **代码质量问题**（lint 警告、类型错误、测试覆盖盲区）
4. **UX 优化**（交互体验、视觉改进、无障碍）
5. **性能瓶颈**（加载速度、LLM 调用效率）
6. **开源项目灵感**（同类项目的优秀实践）

### CHANGELOG 更新规范

每次变更后追加到 `CHANGELOG.md`，格式：

```markdown
## [日期] vX.Y.Z

### Added / Changed / Fixed / Removed
- 具体描述变更内容
- 关联 Issue: #123（如有）

> 🤖 由 AI Agent 自动维护
```

### 约束检查清单

每次提交变更前，AI 必须自检：

- [ ] 读了 `EVOLUTION.md` 且遵守所有不可变原则
- [ ] 变更分级正确（Safe/Moderate/Dangerous）
- [ ] 所有测试通过（`pytest tests/`）
- [ ] 内容审计通过（若涉及 `resources.yaml`）：`python scripts/audit_content.py`
- [ ] **Playwright 实测**：启动应用并用浏览器工具验证受影响的功能（表单提交、页面切换、Chat 对话、API Key 配置等）
- [ ] 没有引入新的安全漏洞
- [ ] CHANGELOG.md 已更新
- [ ] 单次变更聚焦单一目标

### Playwright 实测规范

任何涉及 UI 行为/交互逻辑的变更，必须在提交前启动应用并用 Playwright E2E 方式验证：

```
1. 启动应用：python -m streamlit run app.py --server.port 8501 --server.headless true &
2. 等待就绪：curl -s http://localhost:8501/_stcore/health（返回 ok）
3. 用浏览器工具打开 http://localhost:8501
4. 操作受影响的功能流程，截图记录关键状态
5. 确认无报错、功能符合预期
6. 关闭服务器
```

> 单元测试不足以覆盖 Streamlit 的 session_state、secrets、threading 等运行时行为。Playwright 实测是质量红线。

### E2E 测试环境隔离

E2E 测试启动 Streamlit 子进程时，**必须剥离生产凭证和敏感环境变量**，防止测试操作产生真实副作用。

**必须剥离的变量清单：**
- `GITHUB_TOKEN` — 防止 feedback 表单在测试中创建真实 GitHub Issues
- 其他会触发外部 API 调用的 token（按需追加）

**技术实现**：在 `tests/e2e/conftest.py` 中，`env = os.environ.copy()` 之后立即 `env.pop("GITHUB_TOKEN", None)`。

> **教训来源**：E2E 测试继承了 `gh` CLI 注入的 GITHUB_TOKEN，导致 Playwright 跑 feedback 流程时在 GitHub 上创建了大量垃圾 Issues（#5-#16, #29-#33）。

### GitHub Issue 关闭机制

进化过程中修复的 Issue，通过以下方式关闭：

1. **commit message 关联**：在 `git commit -m` 中使用 `fixes #N` 或 `closes #N`，push 后 GitHub 自动关闭
2. **手动关闭**：如 commit 已提交但未使用关键词，通过 GitHub API 或浏览器工具手动关闭 Issue，并留关闭评论说明修复内容
3. **标签更新**：关闭时添加 `ai-done` 标签标记为 AI 已处理

> ⚠️ **关闭前必须逐个检查**：禁止批量盲关 Issues。每个 Issue 关闭前必须用 `gh issue view <N>` 读取标题和内容，确认确实是已修复或无效的。误关用户真实反馈会严重损害信任。
>
> **教训来源**：曾因批量关闭 #17-#28 而误关了用户真实反馈 Issue #28，导致用户手动重新打开。

```bash
# 示例：push 时自动关闭
git commit -m "fix: 修复 Chat 页面崩溃 (fixes #3, fixes #12)"
git push

# 示例：通过 gh CLI 手动关闭（先检查再关闭）
gh issue view 3          # 先确认内容
gh issue close 3 --comment "已在 commit abc1234 中修复"
gh issue edit 3 --add-label "ai-done"
```

### 反馈驱动的策略反思

用户行为是最重要的进化信号。AI 必须主动检测并响应：

| 用户信号 | 含义 | AI 应对 |
|---------|------|--------|
| Issue 被重新打开 | 修复不完整或误判为已解决 | 立即重新诊断，反思漏测原因，补充 Playwright 实测覆盖 |
| 用户否决 PR | 方案不符合预期 | 回顾需求理解偏差，调整方案重新提交 |
| 同类 Bug 反复出现 | 根因未解决或存在模式化缺陷 | 做根因分析，提取通用防御策略写入约束清单 |
| 用户手动修改 AI 的代码 | AI 的方案有缺陷 | 学习用户的修改模式，更新编码习惯 |
| 用户新增规则到本文件 | 现有规则不够 | 严格遵守新规则，理解其背后的意图 |
| 测试产生真实副作用 | 环境隔离不足 | 排查凭证泄漏路径，在 conftest 中剥离敏感变量，更新隔离规则 |

**每轮进化开始时，必须检查：**
1. 上次关闭的 Issues 中是否有被重新打开的 → 优先处理
2. 用户是否对 AGENTS.md / EVOLUTION.md 做了修改 → 理解并遵守新规则
3. 是否有重复出现的同类问题 → 提取模式、加入防御规则

---

## 项目技术栈速查

| 组件 | 技术 |
|------|------|
| 框架 | Streamlit (Python 3.10+) |
| LLM | OpenAI SDK (兼容多供应商) |
| 数据 | resources.yaml (YAML) |
| 测试 | pytest + pytest-playwright (E2E) |
| 部署 | Docker / Streamlit Cloud |
| CI | GitHub Actions |

## 关键文件说明

| 文件 | 职责 |
|------|------|
| `app.py` | 入口 + 路由 + 主流程 |
| `config.py` | 常量、Prompt、供应商预设 |
| `llm.py` | LLM 客户端、路径生成、趋势洞察 |
| `utils.py` | 纯工具函数（编解码、导出、过滤） |
| `i18n.py` | 国际化翻译字典 |
| `resources.yaml` | 资源数据库（129条） |
| `views/` | 各页面渲染（form/path/chat/radar/browser/feedback/settings/progress/import_plan） |
| `tests/` | 单元测试 + E2E 测试 |
| `EVOLUTION.md` | 进化宪法（不可变原则 + 分级规则） |
| `CONTENT_QUALITY.md` | 内容质量管理策略（六维度 + 审计规范） |
| `scripts/audit_content.py` | 内容质量自动化审计脚本 |