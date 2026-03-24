"""AI Pathfinder — Streamlit entry point."""

import streamlit as st

from config import FOCUS_EMOJI
from i18n import t
from llm import generate_path
from utils import load_resources as _load_resources_uncached, decode_profile, encode_profile, filter_resources_for_direction
from views.browser import render_resource_browser
from views.chat import render_chat
from views.feedback import render_feedback
from views.form import render_form
from views.import_plan import render_import_plan
from views.path import render_path
from views.progress import render_progress_restore
from views.radar import render_trend_radar
from views.settings import render_settings


@st.cache_data(show_spinner=False, ttl=3600)
def load_resources():
    """Cached wrapper — YAML is parsed once, refreshed every hour."""
    return _load_resources_uncached()


def _lang():
    return st.session_state.get("ui_lang", "zh")


st.set_page_config(
    page_title="AI 学习路径规划",
    page_icon="🧭",
    layout="wide",
    menu_items={"About": "开源免费的AI学习路径规划工具"},
)

# ─── 全局样式 ─────────────────────────────────────────────────────────────────

st.markdown("""<style>
h1 {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 12px; padding: 12px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.6rem; font-weight: 700; color: #4a5568;
}
[data-testid="stExpander"] {
    border: 1px solid #e2e8f0; border-radius: 12px;
    margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border: none; border-radius: 8px; font-weight: 600;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    background: none; -webkit-text-fill-color: #e2e8f0;
}
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 8px;
}
[data-testid="stChatMessage"] { border-radius: 12px; margin-bottom: 4px; }
.stDownloadButton > button {
    border-radius: 8px; border: 1px solid #e2e8f0; transition: all 0.2s;
}
.stDownloadButton > button:hover {
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); transform: translateY(-1px);
}
</style>""", unsafe_allow_html=True)


# ─── 侧边栏 ──────────────────────────────────────────────────────────────────


def render_sidebar():
    with st.sidebar:
        lang_col1, lang_col2 = st.columns([3, 1])
        with lang_col1:
            st.title(t("sidebar_title", _lang()))
        with lang_col2:
            st.write("")
            if st.button("🌐", key="lang_toggle", help="中文 / English"):
                st.session_state.ui_lang = "en" if _lang() == "zh" else "zh"
                st.rerun()
        st.caption(t("sidebar_caption", _lang()))
        st.divider()

        L = _lang()
        page = st.radio(
            "导航",
            [t("nav_path", L), t("nav_chat", L), t("nav_browser", L), t("nav_radar", L), t("nav_import", L)],
            label_visibility="collapsed",
        )

        if st.session_state.get("path"):
            st.divider()
            p = st.session_state.profile
            st.subheader(t("sidebar_profile", L))
            st.write(f"{t('sidebar_level', L)}: {p['level']}")
            if p.get("direction"):
                st.write(f"{t('sidebar_direction', L)}: {p['direction']}")
            if p.get("focus"):
                st.write(f"{t('sidebar_focus', L)}: {FOCUS_EMOJI.get(p['focus'], p['focus'])}")
            goal_display = p["goal"][:50] + ("..." if len(p["goal"]) > 50 else "")
            st.write(f"{t('sidebar_goal', L)}: {goal_display}")
            st.write(f"{t('sidebar_time', L)}: {p['hours_per_week']}h/{'周' if L == 'zh' else 'wk'}")
            st.caption(t("sidebar_share_hint", L))
            st.divider()
            if st.button(t("sidebar_replan", L), use_container_width=True):
                st.session_state.path = None
                st.session_state.profile = None
                st.query_params.clear()
                st.rerun()

        if not st.session_state.get("path"):
            render_progress_restore()

        st.divider()
        render_settings()
        st.divider()
        st.caption(t("sidebar_footer", L))
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

    # 从分享链接恢复画像
    if "url_param_loaded" not in st.session_state:
        st.session_state.url_param_loaded = True
        param = st.query_params.get("p", "")
        if param and not st.session_state.get("preset_profile"):
            restored = decode_profile(param)
            if restored:
                st.session_state.preset_profile = restored
                st.session_state.from_shared_url = True

    page = render_sidebar()

    if "Chat" in page or "对话" in page:
        render_chat(resources)
        return
    if "Resources" in page or "资源" in page:
        render_resource_browser(resources)
        return
    if "Radar" in page or "雷达" in page:
        render_trend_radar(resources)
        return
    if "Import" in page or "导入" in page:
        render_import_plan(resources)
        return

    # 路径规划页面
    L = _lang()
    if st.session_state.path is None:
        submitted, profile = render_form()
        if submitted:
            if not profile["goal"].strip():
                st.error(t("form_empty_goal", L))
                return
            with st.spinner(t("form_generating", L)):
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
                    st.error(f"{t('error_generate', L)}{err}")
                    if "api_key" in err.lower() or "apikey" in err.lower() or "请配置" in err:
                        st.info(t("error_api_hint", L))
                    elif "404" in err:
                        st.info(t("error_model_hint", L))
    else:
        render_path(st.session_state.path, resources)
        render_feedback()


if __name__ == "__main__":
    main()
