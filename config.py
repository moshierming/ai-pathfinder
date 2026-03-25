"""Constants and configuration for AI Pathfinder."""
from __future__ import annotations

PROVIDER_PRESETS = {
    "DashScope (阿里云百炼)": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen3.5-plus"],
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "models": ["deepseek-chat", "deepseek-reasoner"],
    },
    "Google Gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
    },
    "SiliconFlow (硅基流动)": {
        "base_url": "https://api.siliconflow.cn/v1",
        "models": ["Qwen/Qwen2.5-72B-Instruct", "deepseek-ai/DeepSeek-V3", "THUDM/glm-4-9b-chat"],
    },
    "Moonshot (月之暗面)": {
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    },
    "ZhipuAI (智谱)": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": ["glm-4-flash", "glm-4-plus", "glm-4"],
    },
    "Ollama (本地模型)": {
        "base_url": "http://localhost:11434/v1",
        "models": ["qwen2.5", "llama3.1", "deepseek-r1"],
    },
    "自定义": {
        "base_url": "",
        "models": [],
    },
}

LEVEL_EMOJI = {
    "beginner": "🟢",
    "intermediate": "🟡",
    "advanced": "🔴",
    "beginner-to-intermediate": "🟢",
    "intermediate-to-advanced": "🟡",
}

TYPE_EMOJI = {
    "course": "🎓",
    "video": "🎬",
    "article": "📄",
    "repo": "💻",
    "book": "📚",
    "channel": "📡",
    "builder": "👤",
}

FOCUS_EMOJI = {
    "foundational": "🧱 打基础",
    "applied": "🔧 重实战",
    "both": "⚖️ 理论+实战",
}

LEVEL_ORDER = {
    "beginner": 1, "beginner-to-intermediate": 2, "intermediate": 3,
    "intermediate-to-advanced": 4, "advanced": 5,
}

LEVELS = [
    "🔰 完全零基础（不会Python）",
    "📗 会Python，了解基本ML概念",
    "📘 能跑通基础模型（sklearn/transformers）",
    "📙 能独立完成小型AI项目",
    "🚀 已在工作中用AI/ML，想深入某方向",
]

PREFERENCES = ["🎬 视频课程为主", "📄 文档/教程为主", "💻 项目实战为主", "⚖️ 均衡搭配"]

LANGUAGES = ["🇨🇳 优先中文资源", "🇬🇧 优先英文资源", "🌍 不限语言"]

FOCUS_OPTIONS = ["⚖️ 理论+实战均衡", "🧱 侧重打基础（数学/原理/论文）", "🔧 侧重实战（项目/部署/工具）"]

FOCUS_MAP = {
    "⚖️ 理论+实战均衡": "both",
    "🧱 侧重打基础（数学/原理/论文）": "foundational",
    "🔧 侧重实战（项目/部署/工具）": "applied",
}

DIRECTIONS = [
    "🤖 AI Agent / 多智能体系统",
    "🧪 AI 辅助软件测试 / 质量保障",
    "💬 LLM 应用开发 / RAG",
    "📊 机器学习 / 数据科学",
    "🎨 AIGC / 多模态生成",
    "🔧 MLOps / AI 系统工程",
    "🔬 AI 研究 / 论文方向",
    "🌐 其他 / 尚未确定",
]

DIRECTION_TO_DOMAIN = {
    "🤖 AI Agent / 多智能体系统": ["ai-agent", "llm-app"],
    "🧪 AI 辅助软件测试 / 质量保障": ["software-testing", "llm-app"],
    "💬 LLM 应用开发 / RAG": ["llm-app", "ai-agent"],
    "📊 机器学习 / 数据科学": ["data-science"],
    "🎨 AIGC / 多模态生成": ["aigc", "data-science"],
    "🔧 MLOps / AI 系统工程": ["mlops", "llm-app"],
    "🔬 AI 研究 / 论文方向": ["research", "data-science"],
    "🌐 其他 / 尚未确定": [],
}

PRESET_PROFILES = {
    "💻 软测 → AI 转型": {
        "level": "📗 会Python，了解基本ML概念",
        "goal": "3-6个月内学会用AI工具提升测试效率，包括AI辅助用例生成、智能回归测试和基础Agent搭建",
        "hours_per_week": 8,
        "preference": "⚖️ 均衡搭配",
        "language": "🇨🇳 优先中文资源",
        "direction": "🧪 AI 辅助软件测试 / 质量保障",
        "focus": "⚖️ 理论+实战均衡",
    },
    "🤖 AI Agent 开发": {
        "level": "📘 能跑通基础模型（sklearn/transformers）",
        "goal": "掌握LangChain/LangGraph等Agent框架，能独立开发多工具调用的AI Agent并部署上线",
        "hours_per_week": 10,
        "preference": "💻 项目实战为主",
        "language": "🌍 不限语言",
        "direction": "🤖 AI Agent / 多智能体系统",
        "focus": "🔧 侧重实战（项目/部署/工具）",
    },
    "💬 LLM 应用入门": {
        "level": "📗 会Python，了解基本ML概念",
        "goal": "能独立开发RAG问答系统，掌握Prompt工程、向量数据库和LLM API调用，完成一个可部署的LLM应用",
        "hours_per_week": 8,
        "preference": "⚖️ 均衡搭配",
        "language": "🌍 不限语言",
        "direction": "💬 LLM 应用开发 / RAG",
        "focus": "⚖️ 理论+实战均衡",
    },
    "📊 ML / 数据科学": {
        "level": "📗 会Python，了解基本ML概念",
        "goal": "系统学习机器学习理论和实践，完成端到端ML项目，掌握数据处理、特征工程和基础模型部署",
        "hours_per_week": 10,
        "preference": "⚖️ 均衡搭配",
        "language": "🌍 不限语言",
        "direction": "📊 机器学习 / 数据科学",
        "focus": "🧱 侧重打基础（数学/原理/论文）",
    },
    "🎨 AIGC / 多模态创作": {
        "level": "📗 会Python，了解基本ML概念",
        "goal": "掌握 Stable Diffusion / ComfyUI 工作流，理解 Diffusion 模型原理，能独立完成从文生图到 LoRA 微调的全流程",
        "hours_per_week": 8,
        "preference": "💻 项目实战为主",
        "language": "🌍 不限语言",
        "direction": "🎨 AIGC / 多模态生成",
        "focus": "🔧 侧重实战（项目/部署/工具）",
    },
    "🔧 MLOps / AI 工程化": {
        "level": "📘 能跑通基础模型（sklearn/transformers）",
        "goal": "学会模型部署、实验管理、数据版本控制和监控，能将 ML 模型从 Notebook 推到生产环境",
        "hours_per_week": 10,
        "preference": "💻 项目实战为主",
        "language": "🌍 不限语言",
        "direction": "🔧 MLOps / AI 系统工程",
        "focus": "🔧 侧重实战（项目/部署/工具）",
    },
    "🔬 AI 研究 / 论文方向": {
        "level": "📘 能跑通基础模型（sklearn/transformers）",
        "goal": "系统阅读经典论文（Attention/GPT/Diffusion），掌握论文复现能力，为发表论文或读研做准备",
        "hours_per_week": 12,
        "preference": "� 文档/教程为主",
        "language": "🌍 不限语言",
        "direction": "🔬 AI 研究 / 论文方向",
        "focus": "🧱 侧重打基础（数学/原理/论文）",
    },
    "🌱 零基础入门 AI": {
        "level": "🔰 完全零基础（不会Python）",
        "goal": "从 Python 基础开始，6 个月内建立 AI 概念框架，能用 sklearn 跑通简单项目",
        "hours_per_week": 6,
        "preference": "🎬 视频课程为主",
        "language": "🇨🇳 优先中文资源",
        "direction": "🌐 其他 / 尚未确定",
        "focus": "🧱 侧重打基础（数学/原理/论文）",
    },
}

PRESET_DESCRIPTIONS = {
    "💻 软测 → AI 转型": "AI 辅助用例生成、智能回归测试、Agent搭建",
    "🤖 AI Agent 开发": "LangChain + LangGraph 多工具 Agent 实战",
    "💬 LLM 应用入门": "Prompt → RAG → 向量数据库 → 部署",
    "📊 ML / 数据科学": "数学基础 → sklearn → 特征工程 → 端到端项目",
    "🎨 AIGC / 多模态创作": "Stable Diffusion + ComfyUI 全流程",
    "🔧 MLOps / AI 工程化": "模型部署/实验管理/生产化",
    "🔬 AI 研究 / 论文方向": "论文阅读 + 复现，读研准备",
    "🌱 零基础入门 AI": "从Python开始，半年建立AI框架",
}

SYSTEM_PROMPT = """你是AI学习路径规划师。根据用户背景和目标，从给定资源库中规划个性化学习路径。

核心规则：
1. 只用资源库中的资源（用id引用），按周分组（每周2-4个），每周总学时应接近用户预算（±20%以内）
2. 难度循序渐进：前1/3基础→中间1/3进阶→后1/3实战+持续学习，确保每周平均难度不低于前一周
3. 若用户填了技能/经历，跳过已熟悉内容，从技能空白处切入
4. type=repo的实战项目优先搭配，每2-3周至少1个可动手项目
5. 根据focus偏好调整：foundational侧重理论，applied侧重实战，both均衡
6. type=channel的信息源放路径后半段作"持续跟踪"推荐（不占时间预算）
7. 资源类型多样化：每周尽量混搭course/video/repo/article（至少2种类型），避免连续3个同类型

教学质量规则：
8. 每周的资源要构成逻辑闭环：概念学习→动手实践→反思巩固
9. 关键概念（如 Transformer、RAG、Agent 架构）安排两次接触：首次粗学+后续深入
10. 如果提供了推荐大牛（builders），在路径相关阶段推荐关注，用 builders 字段引用 id
11. tip 要具体可执行，例如"用 LangChain 实现一个 RAG demo"而非"多练习"
12. 输出纯JSON

输出格式：
{"summary":"路径说明","estimated_weeks":8,"weeks":[{"week":1,"goal":"目标","tip":"提示","resources":["r001"],"builders":["b001"]}]}"""

CHAT_SYSTEM_PROMPT = """你是 AI Pathfinder 的学习助手。用户正在学习 AI 相关知识，你可以帮他解答学习过程中的问题。

规则：
1. 回答简洁、准确、有实操指导性
2. 如果用户的学习画像和路径在下方提供，结合这些信息给出更有针对性的建议
3. 可以推荐用户路径中已有的资源，也可以给出额外的建议
4. 如果用户询问值得关注的人、大牛、行业领袖等，从下方提供的 AI 行业大牛列表中推荐，并说明推荐理由
5. 使用中文回答（除非用户用英文提问）
6. 如果问题超出 AI/ML 学习范畴，友好地引导回学习话题"""
