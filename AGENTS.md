# AI Pathfinder — Agent 操作手册

> 本文件是 AI Agent 操作本项目的完整指南。包含日常交互规则和自进化协议。

---

## 基本规则

### 任务完成后续跟进
每次任务完成之后，必须使用 `vscode_askQuestions` 弹出对话框，询问用户是否还有其他需求。选项：**"有，继续新的改进"** 和 **"没有，结束"**。用户选择"没有，结束"之前不得停止。

### 必读文件
每次开始工作前，必须先读取以下文件：
- `EVOLUTION.md` — 进化宪法，定义不可变原则和变更分级
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
3. 🔍 主动审视代码（lint、测试覆盖、性能、UX、安全）
4. 💡 参考优秀开源项目，发现改进灵感
5. 📊 综合评估，按优先级排序
6. 🔧 执行改进：
   - 🟢 Safe → 直接修改 + 更新 CHANGELOG + 关闭相关 Issue
   - 🟡 Moderate → 描述方案 + 创建 PR + 等待 review
   - 🔴 Dangerous → 写分析报告到 Issue 评论 + 等待用户决策
7. ✅ 运行全部测试（pytest tests/），确保无回归
8. 📝 汇报进化成果
```

### 安全分级判定标准

**参考 `EVOLUTION.md` 中的分级定义**，核心判定逻辑：

| 变更涉及的文件/区域 | 分级 |
|---------------------|------|
| `*.md`、CSS、测试文件、i18n 翻译 | 🟢 Safe |
| `views/*.py`（UI 逻辑）、`utils.py`、`resources.yaml` | 🟡 Moderate |
| `config.py` 中的 Prompt、`llm.py` 的调用参数、`EVOLUTION.md` | 🔴 Dangerous |
| `app.py` 路由逻辑 | 🟡 Moderate |
| `app.py` 架构重组 | 🔴 Dangerous |

### 改进来源优先级

1. **用户/社区 GitHub Issues**（已标记的反馈和 bug）
2. **代码质量问题**（lint 警告、类型错误、测试覆盖盲区）
3. **UX 优化**（交互体验、视觉改进、无障碍）
4. **性能瓶颈**（加载速度、LLM 调用效率）
5. **开源项目灵感**（同类项目的优秀实践）

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
- [ ] 没有引入新的安全漏洞
- [ ] CHANGELOG.md 已更新
- [ ] 单次变更聚焦单一目标

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