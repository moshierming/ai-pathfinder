"""Trend radar view — personalised insights + sources + builders."""
from __future__ import annotations

from html import escape as html_escape

import streamlit as st

from config import DIRECTION_TO_DOMAIN
from i18n import t
from llm import generate_trend_insights, _sanitize_text
from views import _lang


# ─── Helpers ──────────────────────────────────────────────────────────────────

_PLATFORM_ICON: dict[str, str] = {
    "x": "\U0001d54f",  # 𝕏
    "github": "\U0001f4bb",  # 💻
    "youtube": "\u25b6\ufe0f",  # ▶️
    "bilibili": "\U0001f4fa",  # 📺
    "website": "\U0001f310",  # 🌐
    "zhihu": "\U0001f4d6",  # 📖
    "scholar": "\U0001f393",  # 🎓
}

_ROLE_KEY: dict[str, str] = {
    "researcher": "radar_role_researcher",
    "engineer": "radar_role_engineer",
    "founder": "radar_role_founder",
    "educator": "radar_role_educator",
}


def _get_user_direction() -> str:
    """Return the user's learning direction from session state, or ''."""
    profile = st.session_state.get("profile")
    if profile and isinstance(profile, dict):
        return profile.get("direction", "") or ""
    return ""


def _direction_domains(direction: str) -> list[str]:
    """Map a direction label to domain tags for filtering."""
    return DIRECTION_TO_DOMAIN.get(direction, [])


def _is_relevant(resource: dict[str, object], domains: list[str]) -> bool:
    """Check whether a resource matches the given domain tags."""
    if not domains:
        return False
    rd = resource.get("domain", [])
    if isinstance(rd, str):
        rd = [rd]
    return any(d in rd for d in domains)


# ─── Insights section ────────────────────────────────────────────────────────

def _render_insights_section(
    channels: list[dict[str, object]],
    L: str,
    direction: str = "",
) -> None:
    """Render AI trend insights panel with LLM-generated daily analysis."""

    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.subheader(t("radar_insights_title", L))
    with col_btn:
        st.write("")
        force = st.button(t("radar_insights_refresh", L), key="insights_refresh")

    if force or "insights_data" not in st.session_state:
        with st.status(t("radar_insights_loading", L), expanded=True) as status:
            try:
                data = generate_trend_insights(
                    channels, force_refresh=force, direction=direction,
                )
                st.session_state["insights_data"] = data
                status.update(label=t("radar_insights_title", L), state="complete")
            except Exception:
                data = {}
                st.session_state["insights_data"] = data
                status.update(label=t("radar_insights_title", L), state="error")
    else:
        data = st.session_state.get("insights_data", {})

    if not data or not data.get("insights"):
        st.info(t("radar_insights_empty", L))
        return

    # Overview
    overview = data.get("overview", "")
    if overview and isinstance(overview, str):
        overview = _sanitize_text(overview)
        st.markdown(
            f"<div style='padding:14px 18px;background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);"
            f"border-radius:12px;margin-bottom:16px;border-left:4px solid #f59e0b;'>"
            f"<div style='font-weight:600;color:#92400e;font-size:0.95rem;'>"
            f"\U0001f31f {t('radar_insights_overview', L)}</div>"
            f"<div style='color:#78350f;font-size:0.88rem;margin-top:6px;'>"
            f"{html_escape(overview)}</div></div>",
            unsafe_allow_html=True,
        )

    # Insight cards
    for ins in data.get("insights", []):
        if not isinstance(ins, dict):
            continue
        tags = ins.get("tags", [])
        if not isinstance(tags, list):
            tags = []
        tags_html = " ".join(
            f"<span style='background:#e0e7ff;color:#4338ca;font-size:0.7rem;"
            f"padding:2px 8px;border-radius:10px;'>{html_escape(_sanitize_text(str(tag)))}</span>"
            for tag in tags
        )
        title = _sanitize_text(str(ins.get('title', '')))
        summary = _sanitize_text(str(ins.get('summary', '')))
        action = _sanitize_text(str(ins.get('action', '')))
        st.markdown(
            f"<div style='padding:14px 18px;background:#f8fafc;border-radius:10px;"
            f"border:1px solid #e2e8f0;margin-bottom:10px;'>"
            f"<div style='font-weight:600;color:#1e293b;font-size:0.92rem;'>"
            f"\U0001f4a1 {html_escape(title)}</div>"
            f"<div style='color:#334155;font-size:0.84rem;margin-top:5px;'>"
            f"{html_escape(summary)}</div>"
            f"<div style='color:#047857;font-size:0.82rem;margin-top:5px;font-weight:500;'>"
            f"\u2705 {html_escape(action)}</div>"
            f"<div style='margin-top:6px;display:flex;gap:4px;'>{tags_html}</div></div>",
            unsafe_allow_html=True,
        )

    date_str = data.get("date", "")
    if date_str:
        st.caption(t("radar_insights_date", L, date=date_str))


# ─── Builders section ────────────────────────────────────────────────────────

def _render_builder_card(builder: dict[str, object], L: str) -> None:
    """Render a single builder card with social links."""
    title = html_escape(_sanitize_text(str(builder.get("title", ""))))
    desc = html_escape(_sanitize_text(str(builder.get("description", ""))))
    role = builder.get("role", "")
    role_label = t(_ROLE_KEY.get(role, "radar_role_engineer"), L) if role else ""

    links = builder.get("links", {})
    if not isinstance(links, dict):
        links = {}
    link_default = "\U0001f517"
    link_parts: list[str] = []
    for platform, url in links.items():
        if url and isinstance(url, str):
            icon = _PLATFORM_ICON.get(platform, link_default)
            link_parts.append(
                f"<a href='{html_escape(str(url))}' target='_blank' "
                f"style='text-decoration:none;font-size:0.85rem;margin-right:6px;' "
                f"title='{html_escape(platform)}'>"
                f"{icon}</a>"
            )
    links_html = " ".join(link_parts)

    st.markdown(
        f"<div style='padding:12px 16px;background:#fafafa;border-radius:10px;"
        f"border:1px solid #e5e7eb;margin-bottom:8px;'>"
        f"<div style='display:flex;align-items:center;gap:8px;'>"
        f"<span style='font-weight:600;color:#1e293b;font-size:0.9rem;'>"
        f"\U0001f464 {title}</span>"
        f"<span style='background:#dbeafe;color:#1d4ed8;font-size:0.7rem;"
        f"padding:1px 8px;border-radius:10px;'>{html_escape(role_label)}</span>"
        f"</div>"
        f"<div style='color:#4b5563;font-size:0.82rem;margin-top:4px;'>{desc}</div>"
        f"<div style='margin-top:6px;'>{links_html}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _render_builders_section(
    builders: list[dict[str, object]],
    L: str,
    domains: list[str],
) -> None:
    """Render the Builders section, optionally filtered by domain."""
    st.subheader(t("radar_builders_title", L))
    st.markdown(t("radar_builders_hint", L))

    if domains:
        recommended = [b for b in builders if _is_relevant(b, domains)]
        others = [b for b in builders if not _is_relevant(b, domains)]
    else:
        recommended = []
        others = builders

    if recommended:
        st.markdown(f"**{t('radar_for_you', L)}**")
        for b in recommended:
            _render_builder_card(b, L)
        if others:
            with st.expander(t("radar_all_builders", L)):
                for b in others:
                    _render_builder_card(b, L)
    else:
        for b in builders:
            _render_builder_card(b, L)


# ─── Sources section ─────────────────────────────────────────────────────────

def _render_channel_card(
    r: dict[str, object],
    border_color: str,
    bg_color: str,
    text_color: str,
) -> None:
    """Render a single channel card."""
    title = html_escape(_sanitize_text(str(r.get("title", ""))))
    desc = html_escape(_sanitize_text(str(r.get("description", ""))))
    url = html_escape(str(r.get("url", "")))
    st.markdown(
        f"<div style='padding:10px 14px;border-left:3px solid {border_color};"
        f"background:{bg_color};border-radius:0 8px 8px 0;margin-bottom:8px;'>"
        f"<a href=\"{url}\" target=\"_blank\" style='text-decoration:none;"
        f"font-weight:600;color:{text_color};'>\U0001f4e1 {title}</a>"
        f"<div style='font-size:0.78rem;color:#57534e;margin-top:3px;'>{desc}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _render_sources_section(
    channels: list[dict[str, object]],
    L: str,
    domains: list[str],
) -> None:
    """Render recommended sources, with personalised 'for-you' section."""
    st.subheader(t("radar_sources", L))
    st.caption(t("radar_sources_hint", L))

    if domains:
        recommended = [c for c in channels if _is_relevant(c, domains)]
        others = [c for c in channels if not _is_relevant(c, domains)]
        if recommended:
            st.markdown(f"**{t('radar_for_you', L)}**")
            for r in recommended:
                border = "#10b981"
                bg = "#ecfdf5"
                txt = "#065f46"
                _render_channel_card(r, border, bg, txt)
    else:
        recommended = []
        others = channels

    zh_channels = [r for r in others if r.get("language") == "zh"]
    en_channels = [r for r in others if r.get("language") == "en"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(t("radar_zh_sources", L))
        for r in zh_channels:
            _render_channel_card(r, "#f59e0b", "#fffbeb", "#92400e")
    with col2:
        st.markdown(t("radar_en_sources", L))
        for r in en_channels:
            _render_channel_card(r, "#6366f1", "#eef2ff", "#4338ca")


# ─── Main entry ───────────────────────────────────────────────────────────────

def render_trend_radar(resources: list[dict[str, object]]) -> None:
    L = _lang()
    st.title(t("radar_title", L))
    st.markdown(t("radar_subtitle", L))

    direction = _get_user_direction()
    domains = _direction_domains(direction)

    # Personalised hint
    if direction:
        st.info(t("radar_for_you_hint", L, direction=direction))

    st.divider()

    # 0. AI 趋势洞察（LLM 生成，个性化）
    channels = [r for r in resources if r["type"] == "channel"]
    _render_insights_section(channels, L, direction=direction)

    st.divider()

    # 1. 行业大牛 / Builders
    builders = [r for r in resources if r.get("type") == "builder"]
    if builders:
        _render_builders_section(builders, L, domains)
        st.divider()

    # 2. 信息源推荐
    _render_sources_section(channels, L, domains)

    st.divider()

    # 3. 新手引导
    st.subheader(t("radar_newbie", L))
    if L == "zh":
        st.markdown("""
**不知道从哪里学？按你的情况选一条路：**

| 你的状态 | 建议起点 | 推荐预设模板 |
|---------|---------|-------------|
| 完全零基础 | 先学 Python，再按路径走 | \u2190 选 **路径规划** 页 |
| 会 Python，想做 AI 应用 | 直接上手 LLM API + RAG | **\U0001f4ac LLM 应用入门** |
| 有开发经验，想转 AI 测试 | AI 辅助测试 + Agent | **\U0001f4bb 软测 \u2192 AI 转型** |
| 想系统学 ML 理论 | 数学基础 \u2192 ML \u2192 DL \u2192 论文 | **\U0001f4ca ML / 数据科学** |
| 想做 AI Agent | LangChain/LangGraph 实战 | **\U0001f916 AI Agent 开发** |
    """)
    else:
        st.markdown("""
**Not sure where to start? Pick a path based on your level:**

| Your situation | Suggested starting point | Recommended preset |
|---------|---------|-------------|
| Complete beginner | Learn Python first, then follow a path | \u2190 Go to **Path Planner** |
| Know Python, want AI apps | Jump into LLM API + RAG | **\U0001f4ac LLM App Basics** |
| Dev experience, pivot to AI testing | AI-assisted testing + Agent | **\U0001f4bb QA \u2192 AI Pivot** |
| Want ML theory | Math \u2192 ML \u2192 DL \u2192 Papers | **\U0001f4ca ML / Data Science** |
| Want to build AI Agents | LangChain/LangGraph hands-on | **\U0001f916 AI Agent Dev** |
    """)

    st.divider()

    # 3. 快速跳转
    st.subheader(t("radar_links", L))
    links = [
        ("🔥 GitHub Trending", "https://github.com/trending/python?since=weekly",
         "本周最热 Python 项目" if L == "zh" else "Top Python repos this week", "#dcfce7", "#166534"),
        ("🔥 Hacker News AI", "https://hn.algolia.com/?q=AI+LLM+agent&type=story&sort=byPopularity&dateRange=pastMonth",
         "技术社区 AI 热帖" if L == "zh" else "AI hot posts", "#dbeafe", "#1e40af"),
        ("🔥 Product Hunt AI", "https://www.producthunt.com/topics/artificial-intelligence",
         "最新 AI 产品" if L == "zh" else "Latest AI products", "#ffe4e6", "#9f1239"),
        ("🔥 Papers With Code", "https://paperswithcode.com/trending",
         "热门论文 + 代码" if L == "zh" else "Trending papers + code", "#f3e8ff", "#6b21a8"),
        ("🔥 HF Daily Papers", "https://huggingface.co/papers",
         "每日论文精选" if L == "zh" else "Daily paper picks", "#fef3c7", "#92400e"),
    ]
    link_html = "<div style='display:flex;gap:10px;flex-wrap:wrap;'>"
    for label, url, desc, bg, fg in links:
        link_html += (
            f"<a href='{url}' target='_blank' style='text-decoration:none;flex:1;min-width:160px;"
            f"padding:14px 16px;background:{bg};border-radius:10px;'>"
            f"<div style='font-weight:600;color:{fg};font-size:0.9rem;'>{label}</div>"
            f"<div style='font-size:0.78rem;color:#334155;margin-top:3px;'>{desc}</div></a>"
        )
    link_html += "</div>"
    st.markdown(link_html, unsafe_allow_html=True)
