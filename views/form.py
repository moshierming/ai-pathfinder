"""Form view: user profile input."""
from __future__ import annotations

import streamlit as st

from config import (
    DIRECTIONS, FOCUS_MAP, FOCUS_OPTIONS, LANGUAGES, LEVELS, PREFERENCES,
    PRESET_PROFILES,
)
from i18n import t
from views import _lang


def render_form() -> tuple[bool, dict]:
    L = _lang()
    st.title(t("form_title", L))
    st.markdown(t("form_subtitle", L))
    st.caption(t("form_stats", L))
    st.divider()

    # ── 预设模板快速填写 ──
    st.subheader(t("form_quick_start", L))
    st.caption(t("form_quick_hint", L))

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
    preset_items = list(PRESET_PROFILES.items())
    rows = [preset_items[i:i + 4] for i in range(0, len(preset_items), 4)]
    for row in rows:
        preset_cols = st.columns(4)
        for col_idx, (name, preset_data) in enumerate(row):
            with preset_cols[col_idx]:
                st.markdown(
                    f"<div style='text-align:center;padding:10px 8px;border:1px solid #e2e8f0;"
                    f"border-radius:10px;margin-bottom:4px;height:80px;display:flex;"
                    f"flex-direction:column;justify-content:center;'>"
                    f"<div style='font-size:0.85rem;font-weight:600;color:#1e293b;'>{name}</div>"
                    f"<div style='font-size:0.75rem;color:#334155;margin-top:4px;line-height:1.3;'>"
                    f"{PRESET_DESCRIPTIONS.get(name, '')}</div></div>",
                    unsafe_allow_html=True,
                )
                if st.button(t("form_select", L), use_container_width=True, key=f"preset_{name}"):
                    st.session_state.preset_profile = preset_data
                    st.rerun()
    st.divider()

    p = st.session_state.get("preset_profile", {})
    if st.session_state.pop("from_shared_url", False):
        st.info(t("form_restored", L))

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            level_idx = LEVELS.index(p["level"]) if p.get("level") in LEVELS else 0
            level = st.selectbox(t("form_level", L), LEVELS, index=level_idx)
            hours = st.slider(t("form_hours", L), 2, 30, p.get("hours_per_week", 8))

        with c2:
            goal = st.text_area(
                t("form_goal", L),
                value=p.get("goal", ""),
                placeholder=t("form_goal_placeholder", L),
                height=100,
            )
            pref_idx = PREFERENCES.index(p["preference"]) if p.get("preference") in PREFERENCES else 0
            preference = st.selectbox(t("form_preference", L), PREFERENCES, index=pref_idx)

        c3, c4 = st.columns(2)
        with c3:
            dir_idx = DIRECTIONS.index(p["direction"]) if p.get("direction") in DIRECTIONS else 0
            direction = st.selectbox(t("form_direction", L), DIRECTIONS, index=dir_idx)
        with c4:
            lang_idx = LANGUAGES.index(p["language"]) if p.get("language") in LANGUAGES else 0
            language = st.selectbox(t("form_language", L), LANGUAGES, index=lang_idx)

        c5, c6 = st.columns(2)
        with c5:
            focus_idx = FOCUS_OPTIONS.index(p["focus"]) if p.get("focus") in FOCUS_OPTIONS else 0
            focus = st.selectbox(t("form_focus", L), FOCUS_OPTIONS, index=focus_idx)
        with c6:
            st.caption("")
            st.caption(t("form_focus_hint", L))

        skills_background = st.text_area(
            t("form_skills", L),
            value=p.get("skills_background", ""),
            placeholder=t("form_skills_placeholder", L),
            height=80,
        )

        submitted = st.form_submit_button(
            t("form_submit", L), type="primary", use_container_width=True
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
