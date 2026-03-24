"""Trend radar view — insights + sources."""
from __future__ import annotations

from html import escape as html_escape

import streamlit as st

from i18n import t
from llm import generate_trend_insights
from views import _lang


def _render_insights_section(channels: list[dict], L: str) -> None:
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
                data = generate_trend_insights(channels, force_refresh=force)
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
        st.markdown(
            f"<div style='padding:14px 18px;background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);"
            f"border-radius:12px;margin-bottom:16px;border-left:4px solid #f59e0b;'>"
            f"<div style='font-weight:600;color:#92400e;font-size:0.95rem;'>"
            f"\ud83c\udf1f {t('radar_insights_overview', L)}</div>"
            f"<div style='color:#78350f;font-size:0.88rem;margin-top:6px;'>"
            f"{html_escape(overview)}</div></div>",
            unsafe_allow_html=True,
        )

    # Insight cards
    for i, ins in enumerate(data.get("insights", [])):
        if not isinstance(ins, dict):
            continue
        tags = ins.get("tags", [])
        if not isinstance(tags, list):
            tags = []
        tags_html = " ".join(
            f"<span style='background:#e0e7ff;color:#4338ca;font-size:0.7rem;"
            f"padding:2px 8px;border-radius:10px;'>{html_escape(str(tag))}</span>"
            for tag in tags
        )
        st.markdown(
            f"<div style='padding:14px 18px;background:#f8fafc;border-radius:10px;"
            f"border:1px solid #e2e8f0;margin-bottom:10px;'>"
            f"<div style='font-weight:600;color:#1e293b;font-size:0.92rem;'>"
            f"\ud83d\udca1 {html_escape(str(ins.get('title', '')))}</div>"
            f"<div style='color:#334155;font-size:0.84rem;margin-top:5px;'>"
            f"{html_escape(str(ins.get('summary', '')))}</div>"
            f"<div style='color:#047857;font-size:0.82rem;margin-top:5px;font-weight:500;'>"
            f"\u2705 {html_escape(str(ins.get('action', '')))}</div>"
            f"<div style='margin-top:6px;display:flex;gap:4px;'>{tags_html}</div></div>",
            unsafe_allow_html=True,
        )

    date_str = data.get("date", "")
    if date_str:
        st.caption(t("radar_insights_date", L, date=date_str))


def render_trend_radar(resources: list[dict]) -> None:
    L = _lang()
    st.title(t("radar_title", L))
    st.markdown(t("radar_subtitle", L))
    st.divider()

    # 0. AI 趋势洞察（LLM 生成，每日缓存）
    channels = [r for r in resources if r["type"] == "channel"]
    _render_insights_section(channels, L)

    st.divider()

    # 1. 信息源推荐
    st.subheader(t("radar_sources", L))
    st.caption(t("radar_sources_hint", L))

    zh_channels = [r for r in channels if r.get("language") == "zh"]
    en_channels = [r for r in channels if r.get("language") == "en"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(t("radar_zh_sources", L))
        for r in zh_channels:
            st.markdown(
                f"<div style='padding:10px 14px;border-left:3px solid #f59e0b;background:#fffbeb;"
                f"border-radius:0 8px 8px 0;margin-bottom:8px;'>"
                f"<a href=\"{r['url']}\" target=\"_blank\" style='text-decoration:none;font-weight:600;"
                f"color:#92400e;'>📡 {r['title']}</a>"
                f"<div style='font-size:0.78rem;color:#57534e;margin-top:3px;'>{r.get('description', '')}</div>"
                f"</div>", unsafe_allow_html=True,
            )
    with col2:
        st.markdown(t("radar_en_sources", L))
        for r in en_channels:
            st.markdown(
                f"<div style='padding:10px 14px;border-left:3px solid #6366f1;background:#eef2ff;"
                f"border-radius:0 8px 8px 0;margin-bottom:8px;'>"
                f"<a href=\"{r['url']}\" target=\"_blank\" style='text-decoration:none;font-weight:600;"
                f"color:#4338ca;'>📡 {r['title']}</a>"
                f"<div style='font-size:0.78rem;color:#57534e;margin-top:3px;'>{r.get('description', '')}</div>"
                f"</div>", unsafe_allow_html=True,
            )

    st.divider()

    # 2. 新手引导
    st.subheader(t("radar_newbie", L))
    if L == "zh":
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
    else:
        st.markdown("""
**Not sure where to start? Pick a path based on your level:**

| Your situation | Suggested starting point | Recommended preset |
|---------|---------|-------------|
| Complete beginner | Learn Python first, then follow a path | ← Go to **Path Planner** |
| Know Python, want AI apps | Jump into LLM API + RAG | **💬 LLM App Basics** |
| Dev experience, pivot to AI testing | AI-assisted testing + Agent | **💻 QA → AI Pivot** |
| Want ML theory | Math → ML → DL → Papers | **📊 ML / Data Science** |
| Want to build AI Agents | LangChain/LangGraph hands-on | **🤖 AI Agent Dev** |
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
