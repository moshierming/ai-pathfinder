# 📚 内容质量管理策略

> 本文件定义 AI Pathfinder 内容（resources.yaml）的质量管理机制。  
> AI Agent 在每轮进化中必须执行内容质量审计。

---

## 核心理念

AI Pathfinder 是一个**内容驱动型平台**，资源质量直接决定用户体验和学习效果。内容质量管理不是一次性任务，而是持续优化的闭环。

---

## 质量维度

### 1. 完整性（Completeness）
每条资源必须填写所有必要字段：

| 字段 | 学习资源（r*） | Builders（b*） | 说明 |
|------|:---:|:---:|------|
| id | ✅ | ✅ | 唯一标识 |
| title | ✅ | ✅ | 标题 |
| url | ✅ | ✅ | 主链接 |
| type | ✅ | ✅ | 资源类型 |
| topics | ✅ | ✅ | 话题标签数组 |
| domain | ✅ | ✅ | 领域标签 |
| level | ✅ | ✅ | 难度级别 |
| description | ✅ | ✅ | 描述（≥10字） |
| language | ✅ | ✅ | 语言 |
| free | ✅ | ✅ | 是否免费 |
| focus | ✅ | — | foundational/applied/both |
| duration_hours | ✅ | — | 预计学时（>0） |
| role | — | ✅ | 角色分类 |
| links | — | ✅ | 社交链接（≥1） |

### 2. 新鲜度（Freshness）
- 每条资源附带 `verified_date`（最后人工/AI验证日期）
- **新鲜度标准**：
  - 🟢 6个月内验证过 — 新鲜
  - 🟡 6-12个月未验证 — 待检查
  - 🔴 超过12个月未验证 — 过期，优先审查
- AI Agent 每轮进化时对过期资源执行链接检查和内容审查

### 3. 准确性（Accuracy）
- URL 必须可达（HTTP 200）
- 描述必须准确反映资源内容
- 难度级别分配要合理
- topics 和 domain 标签要精准
- duration_hours 估计要合理（不夸张、不缩水）

### 4. 覆盖度（Coverage）
每轮审计检查以下维度的覆盖缺口：

| 维度 | 最低线 | 当前状态 |
|------|--------|----------|
| 初学者资源（beginner） | ≥20% | ~13%（偏低⚠️） |
| 高级资源（advanced） | ≥8% | ~4%（偏低⚠️） |
| 中文资源 | ≥25% | ~21% |
| 每个 domain 至少 | 5条 | ✅ |
| 每个热门 topic 至少 | 3条 | ✅ |

### 5. 去重（Deduplication）
- 同一 URL 不可出现在多条资源中（除非一条已标记 `deprecated: true`）
- 高度相似的资源（同作者、同系列、重叠内容 >80%）应合并或标记区别

### 6. 描述质量（Description Quality）
- 最低10个字符
- 推荐15-50个字符
- 包含关键信息：内容概述、亮点、适合谁
- 优秀描述示例：
  - ✅ `"Anthropic官方实践报告，定义Agent架构的五大核心模式（必读）"`
  - ✅ `"100+ 可直接运行的LLM应用示例（RAG、Agent、多模态），配套代码和教程"`
  - ❌ `"Web自动化测试经典框架"` — 过于简短，缺少亮点

---

## 审计流程

### 自动化审计

运行审计脚本：

```bash
python scripts/audit_content.py
```

脚本检查项：
1. **字段完整性** — 缺失必要字段
2. **URL 重复** — 同一 URL 多条记录
3. **描述长度** — 过短（<10字符）或过长（>100字符）
4. **覆盖度分析** — 各维度分布统计
5. **链接有效性** — HTTP 可达性检测（可选，使用 `--check-links`）
6. **新鲜度检查** — 基于 `verified_date` 的时效性分析

### 输出格式

```
=== AI Pathfinder 内容质量审计报告 ===

📊 总览
  资源总数: 123（学习: 99, Builders: 24）
  
🔍 问题发现
  ❌ [HIGH] r062: URL重复（与r011相同URL）
  ⚠️ [MED]  r043: 描述过短（5字）
  ℹ️ [LOW]  beginner资源占比13%（建议≥20%）

📈 覆盖度
  ...分布图表...
  
✅ 审计通过 / ❌ 发现N个问题
```

---

## AI Agent 内容质量职责

### 每轮进化必做

1. 运行 `python scripts/audit_content.py`
2. 修复所有 HIGH 级别问题
3. 记录 MED/LOW 问题到 GitHub Issues（label: `content-quality`）
4. 更新 `verified_date`（已检查过的资源）

### 新增资源规范

添加新资源时必须：
- [ ] 填写所有必要字段
- [ ] 描述 ≥15 个字符，包含亮点
- [ ] URL 手动验证可达
- [ ] 检查无重复（同 URL 或高度相似）
- [ ] 设定 `verified_date` 为今天
- [ ] 合理评估 `level` 和 `duration_hours`
- [ ] 确认 `topics` 和 `domain` 标签精准

### 主动内容发现

AI Agent 应主动发现高质量新资源：
1. 跟踪热门 AI 课程平台（Coursera, fast.ai, HuggingFace, DeepLearning.AI）
2. 关注顶级 AI repo（GitHub trending, Papers With Code）
3. 监测知名 AI 教育者的新内容
4. 响应社区推荐（GitHub Issues label: `resource`）

---

## 内容淘汰机制

根据 EVOLUTION.md 的"资源只增不删"原则：
- 过期/失效资源添加 `deprecated: true` 字段
- 被弃用资源不会出现在 LLM 路径推荐中
- 被弃用资源在资源浏览器中显示 `⚠️ 已过期` 标记
- 每季度审查一次弃用资源是否可移除（需用户审批）

---

## 版本记录

| 日期 | 变更 | 决策者 |
|------|------|--------|
| 2026-04-06 | 初始版本，确立内容质量六维度管理策略 | AI Agent + @daqie |
