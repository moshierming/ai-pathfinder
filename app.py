import base64
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

import streamlit as st
import yaml
from openai import OpenAI

st.set_page_config(
    page_title="AI 学习路径规划",
    page_icon="🧭",
    layout="wide",
    menu_items={"About": "开源免费的AI学习路径规划工具"},
)

# ─── 资源库 ──────────────────────────────────────────────────────────────────


@st.cache_data
def load_resources():
    path = os.path.join(os.path.dirname(__file__), "resources.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["resources"]


def encode_profile(profile: dict) -> str:
    raw = json.dumps(profile, ensure_ascii=False, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_profile(s: str) -> dict | None:
    try:
        raw = base64.urlsafe_b64decode(s.encode()).decode()
        return json.loads(raw)
    except Exception:
        return None


# ─── LLM 客户端 ──────────────────────────────────────────────────────────────

PROVIDER_PRESETS = {
    "DashScope (阿里云百炼)": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"],
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "models": ["deepseek-chat", "deepseek-reasoner"],
    },
    "自定义": {
        "base_url": "",
        "models": [],
    },
}


def get_llm_config():
    # 优先级：用户在侧边栏填写的 Key > secrets.toml > 环境变量
    api_key = (
        st.session_state.get("settings_api_key", "")
        or st.secrets.get("DASHSCOPE_API_KEY", "")
        or os.environ.get("DASHSCOPE_API_KEY", "")
    )
    provider = st.session_state.get("settings_provider", "DashScope (阿里云百炼)")
    preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["DashScope (阿里云百炼)"])
    if provider == "自定义":
        base_url = (
            st.session_state.get("settings_base_url", "")
            or st.secrets.get("API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        )
        model = (
            st.session_state.get("settings_model_text", "")
            or st.secrets.get("MODEL", "qwen-plus")
        )
    else:
        base_url = preset["base_url"]
        model_key = f"settings_model_{provider}"
        model = st.session_state.get(model_key, preset["models"][0]) or preset["models"][0]
    return api_key, base_url, model


SYSTEM_PROMPT = """你是一位专业的AI学习路径规划师。根据用户的背景和目标，从给定的资源库中，为用户规划个性化学习路径。

规则：
1. 只用资源库中的资源（用 id 字段引用）
2. 按周分组，每周2-4个资源，总时长不超出用户时间预算
3. 难度循序渐进
4. 每周给一句学习目标和一句小提示
5. 资源含 domain 字段时，优先选取 domain 与用户目标方向匹配的资源
6. 若用户填写了'当前技能/项目经历'，充分利用此信息：跳过用户已熟悉的基础内容，从技能空白处切入；优先推荐能与已有工程经验衔接的资源（如有软件测试背景则优先软测+Agent资源）
7. 优先推荐 type 为 repo 的实战项目资源（与课程/文章搭配），每2-3周安排至少1个可动手运行的项目
8. 根据用户的 focus 偏好调整资源选取：
   - foundational（打基础）：侧重 focus=foundational 的理论/数学/论文类资源
   - applied（重实战）：侧重 focus=applied 的项目/部署/工具类资源
   - both（均衡）：两者均衡搭配
9. type=channel 的资源是持续学习信息源（博客、公众号、播客等），不要放在前几周，在学习路径后半段安排2-3个作为"持续跟踪"推荐（不占每周时间预算）
10. 输出纯 JSON，不要有其他文字

输出格式：
{
  "summary": "整体路径说明（1-2句）",
  "estimated_weeks": 8,
  "weeks": [
    {
      "week": 1,
      "goal": "掌握Python数据处理基础",
      "tip": "建议边看边敲，不要只看不动手",
      "resources": ["r001", "r003"]
    }
  ]
}"""


def generate_path(profile: dict, resources: list) -> dict:
    api_key, base_url, model = get_llm_config()
    if not api_key:
        raise ValueError("请配置 DASHSCOPE_API_KEY")

    client = OpenAI(api_key=api_key, base_url=base_url)

    resource_summary = [
        {
            "id": r["id"],
            "title": r["title"],
            "level": r["level"],
            "topics": r["topics"],
            "domain": r.get("domain", ["general"]),
            "duration_hours": r["duration_hours"],
            "type": r["type"],            "focus": r.get("focus", "both"),        }
        for r in resources
    ]

    user_msg = f"""用户信息：
- 当前水平：{profile['level']}
- 目标方向：{profile.get('direction', '通用AI方向')}
- 学习目标：{profile['goal']}
- 当前技能/项目经历：{profile.get('skills_background') or '（未填写）'}
- 学习重心：{profile.get('focus', 'both')}
- 每周可投入时间：{profile['hours_per_week']} 小时
- 偏好学习方式：{profile['preference']}
- 语言偏好：{profile['language']}

可用资源库（{len(resource_summary)} 条）：
{json.dumps(resource_summary, ensure_ascii=False, indent=2)}

请生成个性化学习路径。"""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=3000,
    )
    return json.loads(resp.choices[0].message.content)


# ─── 渲染路径 ────────────────────────────────────────────────────────────────

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
}
FOCUS_EMOJI = {
    "foundational": "🧱 打基础",
    "applied": "🔧 重实战",
    "both": "⚖️ 理论+实战",
}


def render_path(path_data: dict, resources: list):
    ridx = {r["id"]: r for r in resources}

    st.success(f"✅ {path_data.get('summary', '')}", icon="🧭")
    st.caption(f"预计完成：约 **{path_data.get('estimated_weeks', '?')}** 周")
    st.divider()

    total_resources = 0
    done_count = 0

    for week in path_data.get("weeks", []):
        expanded = week["week"] <= 2
        with st.expander(
            f"📅 第 {week['week']} 周 — {week['goal']}", expanded=expanded
        ):
            if week.get("tip"):
                st.info(f"💡 {week['tip']}")

            for rid in week.get("resources", []):
                r = ridx.get(rid)
                if not r:
                    continue

                total_resources += 1
                lvl_emoji = LEVEL_EMOJI.get(r["level"], "⚪")
                typ_emoji = TYPE_EMOJI.get(r["type"], "🔗")
                lang_tag = "🇨🇳 中文" if r.get("language") == "zh" else "🇬🇧 英文"
                is_channel = r.get("type") == "channel"

                cols = st.columns([5, 2, 2, 1])
                title_text = f"{typ_emoji} **[{r['title']}]({r['url']})**"
                if is_channel:
                    title_text += "  `持续关注`"
                cols[0].markdown(title_text)
                cols[0].caption(r.get("description", ""))
                cols[1].caption(f"{lvl_emoji} {r['level']}")
                duration_label = f"⏱ ~{r['duration_hours']}h/周" if is_channel else f"⏱ {r['duration_hours']}h"
                cols[2].caption(f"{duration_label} · {lang_tag}")
                done_key = f"done_{rid}_{week['week']}"
                checked = cols[3].checkbox("✓", key=done_key, label_visibility="collapsed")
                if checked:
                    done_count += 1

            st.write("")

    # 进度条
    st.divider()
    if total_resources > 0:
        progress = done_count / total_resources
        st.progress(progress, text=f"学习进度：{done_count}/{total_resources} 个资源已完成")
        if done_count > 0:
            st.caption("⚠️ 进度仅在当前会话有效，刷新页面后重置。建议使用下方「导出」保存学习计划。")
    else:
        st.caption("暂无可追踪的资源")

    # 导出学习计划
    st.divider()
    st.subheader("💾 保存学习计划")
    st.caption("导出后可离线查看、打印、或下次导入恢复")
    dl_cols = st.columns(2)
    with dl_cols[0]:
        profile = st.session_state.get("profile", {})
        md_content = export_plan_markdown(path_data, profile, resources)
        st.download_button(
            "📄 导出为 Markdown",
            data=md_content,
            file_name="ai-learning-path.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with dl_cols[1]:
        json_content = export_plan_json(path_data, profile)
        st.download_button(
            "📦 导出为 JSON（可导入）",
            data=json_content,
            file_name="ai-learning-path.json",
            mime="application/json",
            use_container_width=True,
        )


# ─── 反馈收集 ────────────────────────────────────────────────────────────────


def submit_feedback(feedback: dict) -> str:
    """保存反馈：本地文件（始终尝试）+ GitHub Issues（有 token 时）。返回 'github' 或 'local'。"""
    # 1. 尝试本地文件（本地开发有效；Streamlit Cloud 为临时文件系统，数据会丢失）
    try:
        feedback_dir = os.path.join(os.path.dirname(__file__), "feedback")
        os.makedirs(feedback_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        with open(os.path.join(feedback_dir, f"fb_{ts}.json"), "w", encoding="utf-8") as f:
            json.dump(feedback, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    # 2. 尝试 GitHub Issues（需在 Streamlit Cloud secrets 里配置 GITHUB_TOKEN）
    token = st.secrets.get("GITHUB_TOKEN", "") or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return "local"

    profile = feedback.get("profile", {})
    body = (
        f"**评分**: {feedback['rating']}\n\n"
        f"**意见**: {feedback.get('comment') or '（无）'}\n\n"
        f"**方向**: {profile.get('direction', '-')}\n"
        f"**水平**: {profile.get('level', '-')}\n"
        f"**时间**: {profile.get('hours_per_week', '-')}h/周\n"
        f"**语言**: {profile.get('language', '-')}\n\n"
        f"**目标**:\n> {profile.get('goal', '-')}"
    )
    payload = json.dumps({
        "title": f"用户反馈 {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "body": body,
        "labels": ["feedback"],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/repos/moshierming/ai-pathfinder/issues",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        return "github"
    except Exception:
        return "local"


def render_feedback():
    st.divider()
    st.subheader("📝 学习反馈")
    st.caption("你的反馈会帮助我们持续优化推荐质量")

    with st.form("feedback_form"):
        rating = st.select_slider(
            "这次路径推荐对你有帮助吗？",
            options=["完全没用", "一般", "有点帮助", "很有帮助", "太赞了"],
            value="有点帮助",
        )
        comment = st.text_area(
            "有什么建议？（可选）",
            placeholder="比如：缺少某个方向的资源、难度跳跃太大、时间分配不合理...",
            height=80,
        )
        submitted = st.form_submit_button("提交反馈")

    if submitted:
        feedback = {
            "rating": rating,
            "comment": comment,
            "profile": st.session_state.get("profile", {}),
        }
        result = submit_feedback(feedback)
        if result == "github":
            st.success("感谢反馈！已记录到 GitHub Issues 🙏")
        else:
            st.success("感谢反馈！🙏")


# ─── 输入表单 ────────────────────────────────────────────────────────────────

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

DIRECTION_TO_DOMAIN: dict[str, list[str]] = {
    "🤖 AI Agent / 多智能体系统": ["ai-agent", "llm-app"],
    "🧪 AI 辅助软件测试 / 质量保障": ["software-testing", "llm-app"],
    "💬 LLM 应用开发 / RAG": ["llm-app", "ai-agent"],
    "📊 机器学习 / 数据科学": ["data-science"],
    "🎨 AIGC / 多模态生成": ["aigc", "data-science"],
    "🔧 MLOps / AI 系统工程": ["mlops", "llm-app"],
    "🔬 AI 研究 / 论文方向": ["research", "data-science"],
    "🌐 其他 / 尚未确定": [],
}


def filter_resources_for_direction(resources: list, direction: str, language: str, focus: str = "both") -> list:
    """LLM 调用前预筛选：按方向+语言+学习重心排序，限制在 50 条以内。"""
    domains = DIRECTION_TO_DOMAIN.get(direction, [])
    if domains:
        matched = [r for r in resources if any(d in r.get("domain", ["general"]) for d in domains)]
        seen = {r["id"] for r in matched}
        general = [r for r in resources if r["id"] not in seen and r.get("domain", ["general"]) == ["general"]]
        filtered = matched + general
    else:
        filtered = list(resources)

    # focus 排序：匹配的排前面，both 类型作为中间项
    if focus in ("foundational", "applied"):
        preferred = [r for r in filtered if r.get("focus") == focus]
        both_focus = [r for r in filtered if r.get("focus") == "both" and r not in preferred]
        others = [r for r in filtered if r not in preferred and r not in both_focus]
        filtered = preferred + both_focus + others

    if "中文" in language:
        preferred = [r for r in filtered if r.get("language") == "zh"]
        others = [r for r in filtered if r.get("language") != "zh"]
        filtered = preferred + others
    elif "英文" in language:
        preferred = [r for r in filtered if r.get("language") == "en"]
        others = [r for r in filtered if r.get("language") != "en"]
        filtered = preferred + others

    return filtered[:50]


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
}


def render_form():
    st.title("🧭 AI Pathfinder")
    st.markdown(
        "> 告诉我你的**现在**和**目标**，我来帮你规划最短最有效的AI学习路径——完全免费，开源。"
    )
    st.caption("📊 90 条精选资源 · 📡 15 个持续信息源 · 🧱 基础→🔧 实战全覆盖")
    st.divider()

    # ── 预设模板快速填写 ──────────────────────────────────────────────────────
    st.subheader("⚡ 快速开始")
    st.caption("选一个最接近你方向的模板，一键填入表单，之后仍可修改")
    preset_cols = st.columns(len(PRESET_PROFILES))
    for i, (name, preset_data) in enumerate(PRESET_PROFILES.items()):
        with preset_cols[i]:
            if st.button(name, use_container_width=True, key=f"preset_{i}"):
                st.session_state.preset_profile = preset_data
                st.rerun()
    st.divider()

    # 读取预设值（用户点了模板按钮 或 从分享链接恢复）
    p = st.session_state.get("preset_profile", {})
    if st.session_state.pop("from_shared_url", False):
        st.info("📎 已从分享链接恢复用户画像，确认无误后点击下方生成按钮")

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            level_idx = LEVELS.index(p["level"]) if p.get("level") in LEVELS else 0
            level = st.selectbox("📊 当前水平", LEVELS, index=level_idx)
            hours = st.slider("⏰ 每周可投入（小时）", 2, 30, p.get("hours_per_week", 8))

        with c2:
            goal = st.text_area(
                "🎯 你的目标（越具体越好）",
                value=p.get("goal", ""),
                placeholder="例：3个月内能搭建一个RAG问答系统并部署上线，已有Python基础",
                height=100,
            )
            pref_idx = PREFERENCES.index(p["preference"]) if p.get("preference") in PREFERENCES else 0
            preference = st.selectbox("🎨 偏好学习方式", PREFERENCES, index=pref_idx)

        c3, c4 = st.columns(2)
        with c3:
            dir_idx = DIRECTIONS.index(p["direction"]) if p.get("direction") in DIRECTIONS else 0
            direction = st.selectbox("🎯 目标方向", DIRECTIONS, index=dir_idx)
        with c4:
            lang_idx = LANGUAGES.index(p["language"]) if p.get("language") in LANGUAGES else 0
            language = st.selectbox("🌐 语言偏好", LANGUAGES, index=lang_idx)

        c5, c6 = st.columns(2)
        with c5:
            focus_idx = FOCUS_OPTIONS.index(p["focus"]) if p.get("focus") in FOCUS_OPTIONS else 0
            focus = st.selectbox("🎓 学习重心", FOCUS_OPTIONS, index=focus_idx)
        with c6:
            st.caption("")
            st.caption("打基础：侧重数学原理和论文理解\n重实战：侧重项目实操和工具使用")

        skills_background = st.text_area(
            "💼 当前技能/项目经历（可选，填写后推荐更精准）",
            value=p.get("skills_background", ""),
            placeholder="例：做过 3 年 Web 后端开发，用过 Spring Boot 和 Python，写过自动化测试脚本，没接触过机器学习",
            height=80,
        )

        submitted = st.form_submit_button(
            "🚀 生成我的学习路径", type="primary", use_container_width=True
        )

    if submitted:
        st.session_state.pop("preset_profile", None)

    return submitted, {
        "level": level,
        "goal": goal,
        "skills_background": skills_background,
        "hours_per_week": hours,
        "preference": preference,
        "language": language,
        "direction": direction,
        "focus": FOCUS_MAP.get(focus, "both"),
    }


# ─── 资源浏览 ────────────────────────────────────────────────────────────────


def render_resource_browser(resources: list):
    st.title("📚 资源库")

    # 统计概览
    from collections import Counter
    type_counts = Counter(r["type"] for r in resources)
    focus_counts = Counter(r.get("focus", "both") for r in resources)
    lang_counts = Counter(r.get("language", "?") for r in resources)
    stat_cols = st.columns(6)
    stat_cols[0].metric("总资源", len(resources))
    stat_cols[1].metric("🇨🇳 中文", lang_counts.get("zh", 0))
    stat_cols[2].metric("📡 信息源", type_counts.get("channel", 0))
    stat_cols[3].metric("💻 实战项目", type_counts.get("repo", 0))
    stat_cols[4].metric("🧱 打基础", focus_counts.get("foundational", 0))
    stat_cols[5].metric("🔧 重实战", focus_counts.get("applied", 0))
    st.divider()

    # 搜索框
    search_query = st.text_input(
        "🔍 搜索资源",
        placeholder="输入关键词搜索标题、描述或主题（如：RAG、Agent、微调...）",
    )

    # 筛选器
    all_topics = sorted({t for r in resources for t in r["topics"]})
    all_types = sorted({r["type"] for r in resources})
    all_levels = sorted({r["level"] for r in resources})
    all_domains = sorted({d for r in resources for d in r.get("domain", ["general"])})
    all_focuses = sorted({r.get("focus", "both") for r in resources})

    c1, c2, c3 = st.columns(3)
    with c1:
        selected_topics = st.multiselect("主题", all_topics)
    with c2:
        selected_types = st.multiselect("类型", all_types)
    with c3:
        selected_levels = st.multiselect("难度", all_levels)

    c4, c5 = st.columns(2)
    with c4:
        selected_domains = st.multiselect("方向领域", all_domains)
    with c5:
        selected_focuses = st.multiselect("学习重心", all_focuses, format_func=lambda x: FOCUS_EMOJI.get(x, x))

    filtered = resources
    if search_query:
        q = search_query.lower()
        filtered = [
            r for r in filtered
            if q in r["title"].lower()
            or q in r.get("description", "").lower()
            or any(q in t for t in r.get("topics", []))
        ]
    if selected_topics:
        filtered = [r for r in filtered if any(t in r["topics"] for t in selected_topics)]
    if selected_types:
        filtered = [r for r in filtered if r["type"] in selected_types]
    if selected_levels:
        filtered = [r for r in filtered if r["level"] in selected_levels]
    if selected_domains:
        filtered = [r for r in filtered if any(d in r.get("domain", ["general"]) for d in selected_domains)]
    if selected_focuses:
        filtered = [r for r in filtered if r.get("focus", "both") in selected_focuses]

    st.caption(f"显示 {len(filtered)} / {len(resources)} 条")
    st.divider()

    for r in filtered:
        lvl_emoji = LEVEL_EMOJI.get(r["level"], "⚪")
        typ_emoji = TYPE_EMOJI.get(r["type"], "🔗")
        lang_tag = "🇨🇳" if r.get("language") == "zh" else "🇬🇧"
        focus_tag = FOCUS_EMOJI.get(r.get("focus", "both"), "")

        cols = st.columns([5, 2, 2])
        cols[0].markdown(f"{typ_emoji} **[{r['title']}]({r['url']})**")
        cols[0].caption(r.get("description", ""))
        cols[1].caption(f"{lvl_emoji} {r['level']} · {lang_tag}")
        duration_text = f"⏱ {r['duration_hours']}h/周" if r["type"] == "channel" else f"⏱ {r['duration_hours']}h"
        cols[2].caption(f"{duration_text} · {focus_tag}")


# ─── 学习计划导出/导入 ────────────────────────────────────────────────────────


def export_plan_markdown(path_data: dict, profile: dict, resources: list) -> str:
    """将学习路径导出为可读的 Markdown 文件内容。"""
    ridx = {r["id"]: r for r in resources}
    lines = [
        "# 🧭 我的 AI 学习路径",
        "",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 📋 个人画像",
        "",
        f"- **水平**：{profile.get('level', '-')}",
        f"- **方向**：{profile.get('direction', '-')}",
        f"- **学习重心**：{profile.get('focus', 'both')}",
        f"- **目标**：{profile.get('goal', '-')}",
        f"- **每周时间**：{profile.get('hours_per_week', '-')} 小时",
        f"- **语言偏好**：{profile.get('language', '-')}",
        "",
        f"## 📊 路径概览",
        "",
        f"{path_data.get('summary', '')}",
        f"预计 **{path_data.get('estimated_weeks', '?')}** 周完成。",
        "",
    ]

    for week in path_data.get("weeks", []):
        lines.append(f"### 📅 第 {week['week']} 周 — {week['goal']}")
        if week.get("tip"):
            lines.append(f"\n> 💡 {week['tip']}\n")
        for rid in week.get("resources", []):
            r = ridx.get(rid)
            if not r:
                continue
            typ_emoji = TYPE_EMOJI.get(r["type"], "🔗")
            lines.append(f"- [ ] {typ_emoji} [{r['title']}]({r['url']}) — {r['level']}, {r['duration_hours']}h")
        lines.append("")

    lines.extend([
        "---",
        "*由 [AI Pathfinder](https://github.com/moshierming/ai-pathfinder) 生成*",
    ])
    return "\n".join(lines)


def export_plan_json(path_data: dict, profile: dict) -> str:
    """导出学习路径为 JSON（可导入恢复）。"""
    return json.dumps({"profile": profile, "path": path_data}, ensure_ascii=False, indent=2)


# ─── 趋势雷达 ────────────────────────────────────────────────────────────────


def render_trend_radar(resources: list):
    st.title("🔥 趋势雷达")
    st.markdown(
        "> AI 领域变化极快——学完基础后，**持续跟踪趋势**和学完一门课一样重要。"
    )
    st.divider()

    # 1. 信息源推荐（从 channel 类型资源中提取）
    channels = [r for r in resources if r["type"] == "channel"]
    st.subheader("📡 推荐信息源")
    st.caption("这些是经过筛选的高质量持续学习渠道，建议每周花 1-2 小时浏览")

    # 分类展示
    zh_channels = [r for r in channels if r.get("language") == "zh"]
    en_channels = [r for r in channels if r.get("language") == "en"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🇨🇳 中文信息源**")
        for r in zh_channels:
            st.markdown(f"- 📡 [{r['title']}]({r['url']})")
            st.caption(f"  {r.get('description', '')}")
    with col2:
        st.markdown("**🇬🇧 英文信息源**")
        for r in en_channels:
            st.markdown(f"- 📡 [{r['title']}]({r['url']})")
            st.caption(f"  {r.get('description', '')}")

    st.divider()

    # 2. 新手引导
    st.subheader("🧭 新手？从这里开始")
    st.markdown("""
**不知道从哪里学？按你的情况选一条路：**

| 你的状态 | 建议起点 | 推荐预设模板 |
|---------|---------|-------------|
| 完全零基础 | 先学 Python，再按路径走 | ← 选 **路径规划** 页 |
| 会 Python，想做 AI 应用 | 直接上手 LLM API + RAG | **💬 LLM 应用入门** |
| 有开发经验，想转 AI 测试 | AI 辅助测试 + Agent | **💻 软测 → AI 转型** |
| 想系统学 ML 理论 | 数学基础 → ML → DL → 论文 | **📊 ML / 数据科学** |
| 想做 AI Agent | LangChain/LangGraph 实战 | **🤖 AI Agent 开发** |
    """)

    st.divider()

    # 3. 本周值得关注
    st.subheader("🔗 快速跳转")
    st.markdown("""
- 🔥 [GitHub Trending (Python)](https://github.com/trending/python?since=weekly) — 本周最热 Python 项目
- 🔥 [Hacker News AI 热帖](https://hn.algolia.com/?q=AI+LLM+agent&type=story&sort=byPopularity&dateRange=pastMonth) — 技术社区讨论
- 🔥 [Product Hunt AI](https://www.producthunt.com/topics/artificial-intelligence) — 最新 AI 产品
- 🔥 [Papers With Code](https://paperswithcode.com/trending) — 本周热门论文 + 代码
- 🔥 [Hugging Face Daily Papers](https://huggingface.co/papers) — 每日论文精选
    """)


# ─── 导入学习计划 ─────────────────────────────────────────────────────────────


def render_import_plan(resources: list):
    st.title("📤 导入学习计划")
    st.markdown(
        "> 上传之前导出的 JSON 文件，恢复你的学习路径和个人画像。"
    )
    st.divider()

    uploaded = st.file_uploader(
        "选择 JSON 文件",
        type=["json"],
        help="支持通过「导出为 JSON」按钮生成的文件",
    )

    if uploaded is not None:
        try:
            data = json.loads(uploaded.read().decode("utf-8"))
            profile = data.get("profile")
            path_data = data.get("path")
            if not profile or not path_data:
                st.error("文件格式无效：缺少 profile 或 path 字段")
                return

            st.success("✅ 文件解析成功！")

            # 预览
            with st.expander("📋 画像预览", expanded=True):
                st.write(f"**水平**: {profile.get('level', '-')}")
                st.write(f"**方向**: {profile.get('direction', '-')}")
                st.write(f"**学习重心**: {profile.get('focus', '-')}")
                st.write(f"**目标**: {profile.get('goal', '-')}")
                st.write(f"**时间**: {profile.get('hours_per_week', '-')}h/周")

            with st.expander("📊 路径预览"):
                st.write(f"**总结**: {path_data.get('summary', '-')}")
                st.write(f"**周数**: {path_data.get('estimated_weeks', '?')}")
                for week in path_data.get("weeks", [])[:3]:
                    st.caption(f"第 {week['week']} 周: {week['goal']}")

            if st.button("🚀 加载此计划", type="primary", use_container_width=True):
                st.session_state.path = path_data
                st.session_state.profile = profile
                st.query_params["p"] = encode_profile(profile)
                st.rerun()

        except json.JSONDecodeError:
            st.error("文件不是有效的 JSON 格式")
        except Exception as e:
            st.error(f"解析失败：{e}")


# ─── 智能对话 ─────────────────────────────────────────────────────────────────

CHAT_SYSTEM_PROMPT = """你是 AI Pathfinder 的学习助手。用户正在使用一个AI学习路径规划工具，你的职责是回答与 AI/ML 学习相关的问题。

你可以帮助用户：
- 解释学习路径中的概念（如 RAG、Agent、Transformer 等）
- 对比不同资源/框架的优劣
- 给出某个话题的快速入门建议
- 解答学习过程中遇到的技术疑问

规则：
1. 回答简洁实用，避免长篇大论
2. 如果用户有学习画像和路径，结合其水平、方向和进度回答
3. 适当推荐资源库中的资源（用标题和链接）
4. 代码示例用 markdown 代码块
5. 用中文回答，除非用户用英文提问"""


def _build_chat_context(resources: list) -> str:
    """构建聊天上下文：用户画像 + 当前路径 + 可用资源摘要。"""
    parts = []
    profile = st.session_state.get("profile")
    if profile:
        parts.append(f"用户画像：水平={profile.get('level','?')}, 方向={profile.get('direction','?')}, "
                      f"目标={profile.get('goal','?')}, 重心={profile.get('focus','?')}")
    path_data = st.session_state.get("path")
    if path_data:
        parts.append(f"当前学习路径：{path_data.get('summary','(无)')}, 共{path_data.get('estimated_weeks','?')}周")
        week_ids = []
        for w in path_data.get("weeks", []):
            week_ids.extend(w.get("resources", []))
        if week_ids:
            parts.append(f"路径中的资源ID：{', '.join(week_ids)}")

    # 资源摘要（仅标题+类型+话题，控制 token）
    summaries = [f"{r['id']}: {r['title']} ({r['type']}, {','.join(r.get('topics',[])[:3])})"
                 for r in resources[:60]]
    parts.append(f"资源库摘要（前60条）:\n" + "\n".join(summaries))
    return "\n\n".join(parts)


def render_chat(resources: list):
    st.title("🧠 智能对话")
    st.markdown("> 学习过程中遇到问题？随时问我。我了解你的学习画像和路径。")

    if st.session_state.get("profile"):
        p = st.session_state.profile
        st.caption(f"当前画像：{p.get('level','')} · {p.get('direction','')} · {FOCUS_EMOJI.get(p.get('focus',''), '')}")
    else:
        st.caption("💡 还没有生成学习路径？先去「路径规划」生成一个，对话会更有针对性。")

    st.divider()

    # 初始化聊天历史
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # 渲染历史消息
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 用户输入
    if user_input := st.chat_input("输入你的问题，例如「RAG 和 Fine-tuning 有什么区别？」"):
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 调用 LLM
        api_key, base_url, model = get_llm_config()
        if not api_key:
            with st.chat_message("assistant"):
                st.error("请先在左侧边栏配置 API Key")
            return

        context = _build_chat_context(resources)

        messages = [
            {"role": "system", "content": CHAT_SYSTEM_PROMPT + "\n\n" + context},
        ]
        # 保留最近 20 轮对话（避免 token 爆炸）
        recent = st.session_state.chat_messages[-20:]
        messages.extend(recent)

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    client = OpenAI(api_key=api_key, base_url=base_url)
                    resp = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.5,
                        max_tokens=2000,
                    )
                    reply = resp.choices[0].message.content
                    st.markdown(reply)
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"请求失败：{e}")

    # 清空对话按钮
    if st.session_state.chat_messages:
        st.divider()
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()


# ─── API 设置面板 ─────────────────────────────────────────────────────────────


def render_settings():
    """侧边栏 API 设置面板"""
    with st.expander("⚙️ API 设置", expanded=False):
        provider = st.selectbox(
            "模型供应商",
            list(PROVIDER_PRESETS.keys()),
            key="settings_provider",
        )
        preset = PROVIDER_PRESETS[provider]

        if provider == "自定义":
            st.text_input(
                "API Base URL",
                placeholder="https://your-api.com/v1",
                key="settings_base_url",
            )
            st.text_input(
                "模型名称",
                placeholder="your-model-name",
                key="settings_model_text",
            )
        else:
            model_key = f"settings_model_{provider}"
            # 防止切换 provider 后出现 stale value 报错
            if st.session_state.get(model_key, preset["models"][0]) not in preset["models"]:
                st.session_state[model_key] = preset["models"][0]
            st.selectbox("模型", preset["models"], key=model_key)

        st.text_input(
            "API Key",
            type="password",
            key="settings_api_key",
            placeholder="sk-... （留空使用服务器配置）",
        )
        if st.session_state.get("settings_api_key"):
            st.caption("✅ 将使用你的 API Key")
        else:
            st.caption("ℹ️ 使用服务器 Key（共享，可能限流）")


# ─── 侧边栏 ──────────────────────────────────────────────────────────────────


def render_sidebar():
    with st.sidebar:
        st.title("🧭 AI Pathfinder")
        st.caption("个性化AI学习路径规划")
        st.divider()

        page = st.radio(
            "导航",
            ["🗺️ 路径规划", "🧠 智能对话", "📚 资源浏览", "🔥 趋势雷达", "📤 导入计划"],
            label_visibility="collapsed",
        )

        if st.session_state.get("path"):
            st.divider()
            p = st.session_state.profile
            st.subheader("📋 当前画像")
            st.write(f"**水平**: {p['level']}")
            if p.get("direction"):
                st.write(f"**方向**: {p['direction']}")
            if p.get("focus"):
                st.write(f"**重心**: {FOCUS_EMOJI.get(p['focus'], p['focus'])}")
            goal_display = p["goal"][:50] + ("..." if len(p["goal"]) > 50 else "")
            st.write(f"**目标**: {goal_display}")
            st.write(f"**时间**: {p['hours_per_week']}h/周")
            st.caption("🔗 路径已编码到地址栏，可直接复制分享")
            st.divider()
            if st.button("🔄 重新规划", use_container_width=True):
                st.session_state.path = None
                st.session_state.profile = None
                st.query_params.clear()
                st.rerun()

        st.divider()
        render_settings()
        st.divider()
        st.caption("开源免费 · 社区驱动")
        st.markdown("[📦 GitHub](https://github.com/moshierming/ai-pathfinder)")
        st.markdown("[💬 社区讨论](https://github.com/moshierming/ai-pathfinder/discussions)")
        st.markdown("[🐛 反馈问题](https://github.com/moshierming/ai-pathfinder/issues)")

    return page


# ─── 主入口 ──────────────────────────────────────────────────────────────────


def main():
    resources = load_resources()

    if "path" not in st.session_state:
        st.session_state.path = None
    if "profile" not in st.session_state:
        st.session_state.profile = None

    # 从分享链接恢复画像（仅首次加载时读取 URL 参数）
    if "url_param_loaded" not in st.session_state:
        st.session_state.url_param_loaded = True
        param = st.query_params.get("p", "")
        if param and not st.session_state.get("preset_profile"):
            restored = decode_profile(param)
            if restored:
                st.session_state.preset_profile = restored
                st.session_state.from_shared_url = True

    page = render_sidebar()

    if "智能对话" in page:
        render_chat(resources)
        return

    if "资源浏览" in page:
        render_resource_browser(resources)
        return

    if "趋势雷达" in page:
        render_trend_radar(resources)
        return

    if "导入计划" in page:
        render_import_plan(resources)
        return

    # 路径规划页面
    if st.session_state.path is None:
        submitted, profile = render_form()
        if submitted:
            if not profile["goal"].strip():
                st.error("请填写学习目标")
                return
            with st.spinner("🤔 正在为你规划学习路径，约需 10-20 秒..."):
                try:
                    filtered = filter_resources_for_direction(
                        resources, profile.get("direction", ""), profile.get("language", ""),
                        profile.get("focus", "both"),
                    )
                    path_data = generate_path(profile, filtered)
                    st.session_state.path = path_data
                    st.session_state.profile = profile
                    st.query_params["p"] = encode_profile(profile)
                    st.rerun()
                except Exception as e:
                    err = str(e)
                    st.error(f"生成失败：{err}")
                    if "api_key" in err.lower() or "apikey" in err.lower() or "请配置" in err:
                        st.info(
                            "💡 请在左侧边栏的 **⚙️ API 设置** 中输入你的 API Key，"
                            "或在 `.streamlit/secrets.toml` 中配置 `DASHSCOPE_API_KEY`"
                        )
                    elif "404" in err:
                        st.info("💡 模型名称可能有误，请在左侧边栏的 **⚙️ API 设置** 中检查模型名称")
    else:
        render_path(st.session_state.path, resources)
        render_feedback()


if __name__ == "__main__":
    main()
