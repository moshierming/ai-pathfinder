# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

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
