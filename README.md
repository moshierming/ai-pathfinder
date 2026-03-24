<div align="center">

# 🧭 AI Pathfinder

**个性化AI学习路径规划工具 — 开源免费**

告诉我你现在的水平和目标，我帮你从 **70 条精选免费资源**中规划最短最有效的学习路径。

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-pathfinder.streamlit.app)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Resources](https://img.shields.io/badge/resources-70条-orange)

</div>

---

## 为什么需要这个？

| 现状 | 问题 |
|------|------|
| 资源太多 | Coursera、YouTube、HuggingFace、B站、论文... 不知道从哪开始 |
| 难度错配 | 初学者看了进阶内容浪费时间，有基础的人重复学入门 |
| 路径断裂 | 学了 Python 不知道下一步学什么，学了 sklearn 不知道怎么过渡到 LLM |
| 冷启动门槛 | 不知道该填什么目标，不知道自己在哪个水平 |

**AI Pathfinder** 根据你的**水平 + 目标 + 时间 + 方向**，从精选资源库中编排一条刚好合适的学习路径。

---

## 核心功能

### ⚡ 预设模板快速开始
不知道填什么？点击一个最接近你的方向，自动填入全部表单字段：
- 💻 **软测 → AI 转型**：AI 辅助测试效率提升
- 🤖 **AI Agent 开发**：LangChain/LangGraph 多工具 Agent
- 💬 **LLM 应用入门**：RAG 问答系统从零到部署
- 📊 **ML / 数据科学**：端到端机器学习项目

### 🔗 分享与书签
生成学习路径后，地址栏自动更新为携带参数的 URL（如 `?p=eyJ...`），直接复制分享给朋友或保存为书签，下次打开即可恢复画像重新生成。

### 🎯 方向智能匹配
选择目标方向后，LLM 收到的资源列表自动预筛选（≤40 条），优先推送与方向匹配的资源（ai-agent / software-testing / llm-app 等），减少 token 消耗，提升推荐相关性。

### ⚙️ 多供应商 API 支持
在侧边栏直接切换：
- **DashScope（阿里云百炼）**：qwen-plus / qwen-turbo / qwen-max
- **OpenAI**：gpt-4o-mini / gpt-4o
- **DeepSeek**：deepseek-chat / deepseek-reasoner
- **自定义**：任意兼容 OpenAI 格式的 API

### 📝 反馈收集
用户提交反馈时：本地开发直接写入 JSON 文件；Streamlit Cloud 部署时若配置了 `GITHUB_TOKEN`，自动创建 GitHub Issues 记录（避免无状态环境数据丢失）。

---

## 工作原理

```
用户填写画像（水平/目标/时间/偏好/方向）
        ↓
按方向预筛选资源（≤40 条，语言偏好排序）
        ↓
LLM 从精选资源中编排个性化周计划
        ↓
输出带进度追踪的学习路径 + URL 分享码
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

当前收录 **70 条精选免费资源**，覆盖 8 个方向，中英文兼顾：

| 方向 | 资源数 | 代表资源 |
|------|--------|---------|
| 🤖 AI Agent / 多智能体 | 24 | LangGraph, AutoGen, Qwen-Agent |
| 💬 LLM 应用 / RAG | 26 | LangChain, LlamaIndex, InternLM实战营 |
| 🧪 AI 辅助软件测试 | 11 | AI测试实战、智能测试框架 |
| 📊 机器学习 / 数据科学 | 11 | 吴恩达ML、d2l.ai、南瓜书 |
| 🔬 AI 研究 / 论文方向 | 7 | CS224n、李沐精读论文、MiniMind |
| 🔧 MLOps / AI 系统工程 | 6 | W&B、Self-LLM、Docker部署 |
| 🎨 AIGC / 多模态 | 1 | Diffusion Models From Scratch |
| 🌐 通用基础 | 4 | Python、数学基础 |

中文资源单独标注 🇨🇳，优先中文语言偏好时自动排前。

---

## 贡献资源

欢迎在 `resources.yaml` 中添加高质量免费学习资源：

```yaml
- id: r071
  title: "资源标题"
  url: "https://..."
  type: course  # course/video/article/repo/book
  topics: [llm, rag]
  domain: [llm-app]  # general/data-science/llm-app/ai-agent/software-testing/mlops/aigc/research
  level: intermediate  # beginner/intermediate/advanced（及中间级别）
  duration_hours: 10
  description: "一句话描述（中文）"
  language: en  # en/zh
  free: true
```

---

## License

MIT

