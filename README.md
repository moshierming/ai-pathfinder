<div align="center">

# 🧭 AI Pathfinder

**个性化AI学习路径规划工具 — 开源免费**

告诉我你现在的水平和目标，我帮你从 40+ 条精选免费资源中规划最短最有效的学习路径。

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-pathfinder.streamlit.app)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## 为什么需要这个？

| 现状 | 问题 |
|------|------|
| 资源太多 | Coursera、YouTube、HuggingFace、B站、论文... 不知道从哪开始 |
| 难度错配 | 初学者看了进阶内容浪费时间，有基础的人重复学入门 |
| 路径断裂 | 学了 Python 不知道下一步学什么，学了 sklearn 不知道怎么过渡到 LLM |
| 信息过时 | 2024 的教程推荐 2022 的框架 |

**AI Pathfinder** 根据你的**水平 + 目标 + 时间**，从精选资源库中编排一条刚好合适的学习路径。

---

## 工作原理

```
用户填写画像（水平/目标/时间/偏好）
        ↓
LLM 从 40+ 精选资源中编排个性化周计划
        ↓
输出带进度追踪的学习路径
        ↓
用户反馈 → 更新画像 → 持续优化
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
| `DASHSCOPE_API_KEY` | 阿里云 DashScope Key | 必填 |
| `API_BASE_URL` | API 地址 | DashScope |
| `MODEL` | 模型名称 | `qwen-plus` |

---

## 部署到 Streamlit Cloud

1. Fork 本仓库
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 新建 App → 选择本仓库 → 主文件 `app.py`
4. Advanced Settings → Secrets → 填入 `DASHSCOPE_API_KEY`

---

## 资源库

当前收录 **40 条精选免费资源**，覆盖：

- 🐍 Python & 数学基础
- 🤖 机器学习（吴恩达、sklearn、StatQuest）
- 🧠 深度学习（fast.ai、d2l.ai、Karpathy）
- 📝 NLP & Transformers（HuggingFace、Stanford CS224n）
- 💬 LLM 应用（Prompt Engineering、LangChain）
- 🔍 RAG（LlamaIndex、向量数据库）
- 🤖 Agent（LangGraph、HuggingFace Agents）
- 🔧 微调（LoRA、PEFT、Unsloth）
- 🚀 部署（FastAPI、Docker、Streamlit）
- 📊 MLOps（W&B、实验追踪）

---

## 贡献资源

欢迎在 `resources.yaml` 中添加高质量免费学习资源：

```yaml
- id: r041
  title: "资源标题"
  url: "https://..."
  type: course  # course/video/article/repo/book
  topics: [llm, rag]
  level: intermediate  # beginner/intermediate/advanced
  duration_hours: 10
  description: "一句话描述"
  language: en  # en/zh
  free: true
```

---

## License

MIT
