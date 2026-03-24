import json
import os
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
6. 输出纯 JSON，不要有其他文字

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
            "type": r["type"],
        }
        for r in resources
    ]

    user_msg = f"""用户信息：
- 当前水平：{profile['level']}
- 目标方向：{profile.get('direction', '通用AI方向')}
- 学习目标：{profile['goal']}
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

                cols = st.columns([5, 2, 2, 1])
                cols[0].markdown(f"{typ_emoji} **[{r['title']}]({r['url']})**")
                cols[0].caption(r.get("description", ""))
                cols[1].caption(f"{lvl_emoji} {r['level']}")
                cols[2].caption(f"⏱ {r['duration_hours']}h · {lang_tag}")
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
    else:
        st.caption("暂无可追踪的资源")


# ─── 反馈收集 ────────────────────────────────────────────────────────────────


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
        # 将反馈保存到本地 JSON（后续可接 GitHub Issue / 数据库）
        feedback = {
            "rating": rating,
            "comment": comment,
            "profile": st.session_state.get("profile", {}),
        }
        feedback_dir = os.path.join(os.path.dirname(__file__), "feedback")
        os.makedirs(feedback_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        feedback_path = os.path.join(feedback_dir, f"fb_{ts}.json")
        with open(feedback_path, "w", encoding="utf-8") as f:
            json.dump(feedback, f, ensure_ascii=False, indent=2)
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


def render_form():
    st.title("🧭 AI Pathfinder")
    st.markdown(
        "> 告诉我你的**现在**和**目标**，我来帮你规划最短最有效的AI学习路径——完全免费，开源。"
    )
    st.divider()

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            level = st.selectbox("📊 当前水平", LEVELS)
            hours = st.slider("⏰ 每周可投入（小时）", 2, 30, 8)

        with c2:
            goal = st.text_area(
                "🎯 你的目标（越具体越好）",
                placeholder="例：3个月内能搭建一个RAG问答系统并部署上线，已有Python基础",
                height=100,
            )
            preference = st.selectbox("🎨 偏好学习方式", PREFERENCES)

        c3, c4 = st.columns(2)
        with c3:
            direction = st.selectbox("🎯 目标方向", DIRECTIONS)
        with c4:
            language = st.selectbox("🌐 语言偏好", LANGUAGES)

        submitted = st.form_submit_button(
            "🚀 生成我的学习路径", type="primary", use_container_width=True
        )

    return submitted, {
        "level": level,
        "goal": goal,
        "hours_per_week": hours,
        "preference": preference,
        "language": language,
        "direction": direction,
    }


# ─── 资源浏览 ────────────────────────────────────────────────────────────────


def render_resource_browser(resources: list):
    st.title("📚 资源库")
    st.caption(f"共 {len(resources)} 条精选免费AI学习资源")

    # 筛选器
    all_topics = sorted({t for r in resources for t in r["topics"]})
    all_types = sorted({r["type"] for r in resources})
    all_levels = sorted({r["level"] for r in resources})

    c1, c2, c3 = st.columns(3)
    with c1:
        selected_topics = st.multiselect("主题", all_topics)
    with c2:
        selected_types = st.multiselect("类型", all_types)
    with c3:
        selected_levels = st.multiselect("难度", all_levels)

    filtered = resources
    if selected_topics:
        filtered = [r for r in filtered if any(t in r["topics"] for t in selected_topics)]
    if selected_types:
        filtered = [r for r in filtered if r["type"] in selected_types]
    if selected_levels:
        filtered = [r for r in filtered if r["level"] in selected_levels]

    st.caption(f"显示 {len(filtered)} / {len(resources)} 条")
    st.divider()

    for r in filtered:
        lvl_emoji = LEVEL_EMOJI.get(r["level"], "⚪")
        typ_emoji = TYPE_EMOJI.get(r["type"], "🔗")
        lang_tag = "🇨🇳" if r.get("language") == "zh" else "🇬🇧"

        cols = st.columns([5, 2, 2])
        cols[0].markdown(f"{typ_emoji} **[{r['title']}]({r['url']})**")
        cols[0].caption(r.get("description", ""))
        cols[1].caption(f"{lvl_emoji} {r['level']} · {lang_tag}")
        cols[2].caption(f"⏱ {r['duration_hours']}h · {', '.join(r['topics'][:3])}")


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
            ["🗺️ 路径规划", "📚 资源浏览"],
            label_visibility="collapsed",
        )

        if st.session_state.get("path"):
            st.divider()
            p = st.session_state.profile
            st.subheader("📋 当前画像")
            st.write(f"**水平**: {p['level']}")
            if p.get("direction"):
                st.write(f"**方向**: {p['direction']}")
            goal_display = p["goal"][:50] + ("..." if len(p["goal"]) > 50 else "")
            st.write(f"**目标**: {goal_display}")
            st.write(f"**时间**: {p['hours_per_week']}h/周")
            st.divider()
            if st.button("🔄 重新规划", use_container_width=True):
                st.session_state.path = None
                st.session_state.profile = None
                st.rerun()

        st.divider()
        render_settings()
        st.divider()
        st.caption("开源免费 · 社区驱动")
        st.markdown("[📦 GitHub](https://github.com/moshierming/ai-pathfinder)")
        st.markdown("[🐛 反馈问题](https://github.com/moshierming/ai-pathfinder/issues)")

    return page


# ─── 主入口 ──────────────────────────────────────────────────────────────────


def main():
    resources = load_resources()

    if "path" not in st.session_state:
        st.session_state.path = None
    if "profile" not in st.session_state:
        st.session_state.profile = None

    page = render_sidebar()

    if "资源浏览" in page:
        render_resource_browser(resources)
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
                    path_data = generate_path(profile, resources)
                    st.session_state.path = path_data
                    st.session_state.profile = profile
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
