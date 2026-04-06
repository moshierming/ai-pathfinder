# 贡献指南

感谢你对 AI Pathfinder 的关注！以下是参与贡献的方式。

## 快速开始

```bash
git clone https://github.com/moshierming/ai-pathfinder.git
cd ai-pathfinder
pip install -r requirements.txt
pip install pytest  # 开发依赖

# 运行测试确认环境正常
python -m pytest tests/ -v

# 启动应用
streamlit run app.py
```

## 贡献方式

### 📚 添加学习资源

在 `resources.yaml` 末尾追加条目：

```yaml
- id: r106  # 递增编号
  title: "资源标题"
  url: "https://..."
  type: course  # course/video/article/repo/book/channel
  topics: [llm, rag]
  domain: [llm-app]  # general/data-science/llm-app/ai-agent/software-testing/mlops/aigc/research
  level: intermediate  # beginner/beginner-to-intermediate/intermediate/intermediate-to-advanced/advanced
  duration_hours: 10
  description: "一句话中文描述（≥15字，包含亮点）"
  language: en  # en/zh
  free: true
  focus: applied  # foundational/applied/both
  verified_date: "2026-04-06"  # 验证日期
```

> Builders（b* 类型）额外需要 `role`（researcher/engineer/founder/educator）和 `links`（社交链接）字段。

添加后运行审计验证：

```bash
python scripts/audit_content.py
```

详细质量标准见 [CONTENT_QUALITY.md](CONTENT_QUALITY.md)。

### 🐛 报告 Bug

请在 [Issues](https://github.com/moshierming/ai-pathfinder/issues) 中描述：
1. 复现步骤
2. 预期行为 vs 实际行为
3. 浏览器 / Python 版本

### 💡 功能建议

欢迎在 Issues 中提出，请说明使用场景和预期效果。

### 🔧 代码贡献

1. Fork 本仓库
2. 创建分支：`git checkout -b feat/your-feature`
3. 编写代码和测试
4. 确保测试通过：`python -m pytest tests/ -v`
5. 提交 PR

## 项目架构

```
app.py          # 入口：CSS + 侧边栏 + 路由
config.py       # 常量和预设配置
llm.py          # LLM 客户端
utils.py        # 工具函数
i18n.py         # 国际化翻译
views/          # 9 个视图模块
tests/          # 244 单元 + 10 E2E 测试
resources.yaml  # 资源库（128 条）
scripts/        # 工具脚本（内容审计等）
```

## 项目治理

本项目遵循 AI Agent 自进化体系，请了解：

- **不可变原则**（开源免费、资源只增不删等）：见 [EVOLUTION.md](EVOLUTION.md)
- **变更安全分级**（Safe / Moderate / Dangerous）：见 [EVOLUTION.md](EVOLUTION.md#变更安全分级)
- **内容质量标准**（六维度管理）：见 [CONTENT_QUALITY.md](CONTENT_QUALITY.md)

新增资源须通过 `python scripts/audit_content.py` 验证。

## 代码规范

- 所有新功能需附带测试
- 中英文翻译条目需同步添加到 `i18n.py`
- 视图模块放在 `views/` 目录下（不要用 `pages/`）
- 每个视图模块内需包含 `_lang()` 辅助函数

## 提交规范

采用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
feat: 新功能描述
fix: 修复描述
docs: 文档更新
test: 测试补充
chore: 杂项维护
refactor: 重构描述
ci: CI/CD 变更
```
