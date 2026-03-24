<div align="center">

# 🧭 AI Pathfinder

**个性化AI学习路径规划工具 — 开源免费**

告诉我你现在的水平和目标，我帮你从 **105 条精选资源 · 15 个持续信息源**中规划最短最有效的学习路径。

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-pathfinder.streamlit.app)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Resources](https://img.shields.io/badge/resources-105条-orange)

</div>

---

## 为什么需要这个？

| 现状 | 问题 |
|------|------|
| 资源太多 | Coursera、YouTube、HuggingFace、B站、论文... 不知道从哪开始 |
| 难度错配 | 初学者看了进阶内容浪费时间，有基础的人重复学入门 |
| 路径断裂 | 学了 Python 不知道下一步学什么，学了 sklearn 不知道怎么过渡到 LLM |
| 冷启动门槛 | 不知道该填什么目标，不知道自己在哪个水平 |
| 缺少持续来源 | 学完课程后不知道去哪里跟踪 AI 前沿动态 |
| 基础 vs 实战模糊 | 想直接上手做项目，却被推了一堆理论课 |

**AI Pathfinder** 根据你的**水平 + 目标 + 时间 + 方向 + 学习侧重**，从精选资源库中编排一条刚好合适的学习路径。

---

## 核心功能

### 🗺️ 个性化路径规划
填写学习画像（水平、目标、时间、方向、侧重），LLM 从 105 条资源中编排专属周计划，支持进度追踪。

### ⚡ 预设模板快速开始
不知道填什么？点击一个最接近你的方向，自动填入全部表单字段：
- 💻 **软测 → AI 转型**：AI 辅助测试效率提升
- 🤖 **AI Agent 开发**：LangChain/LangGraph 多工具 Agent
- 💬 **LLM 应用入门**：RAG 问答系统从零到部署
- 📊 **ML / 数据科学**：端到端机器学习项目
- 🎨 **AIGC / 多模态创作**：Stable Diffusion + ComfyUI 全流程
- 🔧 **MLOps / AI 工程化**：模型部署/实验管理/生产化
- 🔬 **AI 研究 / 论文方向**：论文阅读 + 复现，读研准备
- 🌱 **零基础入门 AI**：从 Python 开始，半年建立 AI 框架

### 🧱 基础 vs 实战 侧重选择
新增 `focus` 维度（打基础 / 重实战 / 理论+实战），LLM 会据此优先推荐匹配的资源。想直接做项目？选「重实战」；想夯实理论？选「打基础」。

### 📡 持续信息源（Channel）
15 个精选持续学习渠道：博客、Newsletter、播客、公众号、B站频道 — 学完课程后持续跟踪 AI 前沿。

### 🔥 趋势雷达
独立页面汇聚中英文 AI 信息源推荐、新手快速入门指南、一键直达 GitHub Trending / Hacker News / Product Hunt / Papers With Code 等前沿阵地。

### 📤 导出 & 导入学习计划
- **导出**：将生成的学习路径导出为 Markdown（可读）或 JSON（可还原）
- **导入**：上传之前导出的 JSON 文件，恢复完整学习计划继续跟踪

### 🔗 分享与书签
生成学习路径后，地址栏自动更新为携带参数的 URL（如 `?p=eyJ...`），直接复制分享给朋友或保存为书签，下次打开即可恢复画像重新生成。

### 📚 资源浏览器
独立页面浏览全部 105 条资源，支持 5 维筛选（话题/类型/难度/方向/侧重）+ 关键词搜索 + 统计概览。

### ⚙️ 多供应商 API 支持
在侧边栏直接切换：
- **DashScope（阿里云百炼）**：qwen-plus / qwen-turbo / qwen-max
- **OpenAI**：gpt-4o-mini / gpt-4o
- **DeepSeek**：deepseek-chat / deepseek-reasoner
- **自定义**：任意兼容 OpenAI 格式的 API

### 📝 反馈收集
用户提交反馈时：本地开发直接写入 JSON 文件；Streamlit Cloud 部署时若配置了 `GITHUB_TOKEN`，自动创建 GitHub Issues 记录（避免无状态环境数据丢失）。

### 🧠 智能对话
学习过程中遇到问题？随时在「AI Chat」页面提问。聊天助手自动感知你的学习画像和当前路径，提供有针对性的解答，保持最近 20 轮对话上下文。

### 📊 学习路径可视化分析
生成路径后自动展示三维度分析图表：
- **资源分布**：类型构成 + 学习侧重分布（渐变条形图）
- **每周节奏**：每周学时、资源数、平均难度
- **话题覆盖**：路径中 Top 15 话题标签可视化

### 🌐 中英文双语界面
侧边栏 🌐 按钮一键切换中文 / English，全部 5 个页面 + 设置面板 + 反馈表单完整翻译，170+ 条翻译条目。

### 🎨 UI 主题美化
渐变色标题、卡片阴影、信息源卡片、统计面板配色、聊天气泡圆角 — 全部通过 CSS 实现，零额外依赖。

---

## 工作原理

```
用户填写画像（水平/目标/时间/偏好/方向/侧重）
        ↓
按方向 + 侧重预筛选资源（≤50 条，语言偏好排序）
        ↓
LLM 从精选资源中编排个性化周计划（信息源安排在后半段）
        ↓
输出带进度追踪的学习路径 + URL 分享码 + 导出按钮 + 可视化分析
        ↓
学习过程中随时通过 AI Chat 提问
        ↓
用户反馈 → GitHub Issues 持久化记录
```

---

## 快速开始

### 本地运行

```bash
git clone https://github.com/moshierming/ai-pathfinder.git
cd ai-pathfinder
pip install -r requirements.txt

# 配置 API Key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# 编辑 secrets.toml，填入 DASHSCOPE_API_KEY

streamlit run app.py
```

### 配置

在 `.streamlit/secrets.toml` 中：

| 变量 | 说明 | 默认值 |
|------|------|-------|
| `DASHSCOPE_API_KEY` | 阿里云 DashScope Key（默认供应商） | — |
| `API_BASE_URL` | 自定义 API 地址 | DashScope |
| `MODEL` | 模型名称 | `qwen-plus` |
| `GITHUB_TOKEN` | 反馈写入 GitHub Issues | 可选 |

---

### Docker 部署

```bash
# 方式一：docker-compose（推荐）
export DASHSCOPE_API_KEY="sk-..."
docker compose up -d

# 方式二：直接 docker run
docker build -t ai-pathfinder .
docker run -d -p 8501:8501 -e DASHSCOPE_API_KEY="sk-..." ai-pathfinder
```

访问 http://localhost:8501 即可使用。

---

## 部署到 Streamlit Cloud

1. Fork 本仓库
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 新建 App → 选择本仓库 → 主文件 `app.py`
4. Advanced Settings → Secrets → 填入：

```toml
DASHSCOPE_API_KEY = "sk-..."
GITHUB_TOKEN = "ghp_..."   # 可选，用于反馈收集
```

---

## 资源库

当前收录 **105 条精选资源**（90 条学习资源 + 15 个持续信息源），覆盖 8 个方向，中英文兼顾：

| 类型 | 数量 | 说明 |
|------|------|------|
| 📖 课程 (course) | 26 | 系统化教程和实战营 |
| 📝 文章 (article) | 33 | 技术博客、教程、指南 |
| 🎬 视频 (video) | 10 | YouTube / B站视频系列 |
| 📚 书籍 (book) | 7 | 经典教材 |
| 💻 仓库 (repo) | 14 | GitHub 开源项目和工具 |
| 📡 信息源 (channel) | 15 | 博客/公众号/Newsletter/播客 |

### 侧重分布

| 侧重 | 数量 | 说明 |
|------|------|------|
| 🧱 打基础 (foundational) | 27 | 理论、数学、基础概念 |
| ⚖️ 理论+实战 (both) | 34 | 兼顾原理与实践 |
| 🔧 重实战 (applied) | 44 | 项目驱动、动手为主 |

### 方向覆盖

| 方向 | 代表资源 |
|------|---------|
| 🤖 AI Agent / 多智能体 | LangGraph, AutoGen, Qwen-Agent |
| 💬 LLM 应用 / RAG | LangChain, LlamaIndex, InternLM实战营 |
| 🧪 AI 辅助软件测试 | AI测试实战、智能测试框架 |
| 📊 机器学习 / 数据科学 | 吴恩达ML、d2l.ai、南瓜书 |
| 🔬 AI 研究 / 论文方向 | CS224n、李沐精读论文、MiniMind |
| 🔧 MLOps / AI 系统工程 | W&B、Self-LLM、Docker部署 |
| 🎨 AIGC / 多模态 | Stable Diffusion, ComfyUI, Diffusers, DALL·E |
| 🌐 通用基础 | Python、数学基础 |

中文资源 26 条（含 6 个中文信息源），优先中文语言偏好时自动排前。

---

## 贡献资源

欢迎在 `resources.yaml` 中添加高质量免费学习资源：

```yaml
- id: r091
  title: "资源标题"
  url: "https://..."
  type: course  # course/video/article/repo/book/channel
  topics: [llm, rag]
  domain: [llm-app]  # general/data-science/llm-app/ai-agent/software-testing/mlops/aigc/research
  level: intermediate  # beginner/beginner-to-intermediate/intermediate/intermediate-to-advanced/advanced
  duration_hours: 10   # channel 类型填每周推荐投入小时数
  description: "一句话描述（中文）"
  language: en  # en/zh
  free: true
  focus: applied  # foundational/applied/both
```

---

## 项目架构

```
ai-pathfinder/
├── app.py              # 入口：CSS + 侧边栏 + 页面路由（196行）
├── config.py           # 常量/预设：Provider、Emoji、方向、模板
├── llm.py              # LLM 客户端：配置获取 + 路径生成
├── utils.py            # 工具函数：资源加载/编码/筛选/导出
├── i18n.py             # 国际化：中英文 170+ 翻译条目
├── resources.yaml      # 资源库：90 条精选学习资源
├── views/              # 视图模块（8 个独立文件）
│   ├── path.py         #   路径展示 + 可视化分析
│   ├── form.py         #   学习画像表单
│   ├── browser.py      #   资源浏览器
│   ├── radar.py        #   趋势雷达
│   ├── chat.py         #   AI 对话
│   ├── feedback.py     #   反馈收集
│   ├── import_plan.py  #   导入学习计划
│   └── settings.py     #   API 供应商设置
└── tests/              # 测试套件（113 个测试）
    ├── test_app.py         # 核心功能：编码/筛选/导出/常量
    ├── test_config.py      # 配置完整性：Presets/Emoji/方向映射
    ├── test_i18n.py        # 国际化：翻译覆盖/格式化/回退
    ├── test_llm.py         # LLM 客户端：API Key/Provider/Mock调用
    ├── test_utils_extended.py  # 工具边界：编码/筛选/导出边界用例
    └── test_views.py       # 视图逻辑：Chat上下文/反馈/模块导入
```

## 运行测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行全部 113 个测试
python -m pytest tests/ -v

# 运行单个测试文件
python -m pytest tests/test_config.py -v
```

---

## License

MIT

