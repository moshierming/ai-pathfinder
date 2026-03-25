"""Resource browser view."""
from __future__ import annotations

from collections import Counter

import streamlit as st

from config import FOCUS_EMOJI, LEVEL_EMOJI, TYPE_EMOJI
from i18n import t
from views import _lang


def render_resource_browser(resources: list[dict[str, object]]) -> None:
    L = _lang()
    st.title(t("browser_title", L))
    st.caption(t("browser_hint", L))

    type_counts = Counter(r["type"] for r in resources)
    focus_counts = Counter(r.get("focus", "both") for r in resources)
    lang_counts = Counter(r.get("language", "?") for r in resources)

    st.markdown(
        "<div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px;'>"
        + "".join(
            f"<div style='flex:1;min-width:110px;text-align:center;padding:14px 8px;"
            f"border-radius:12px;background:{bg};'>"
            f"<div style='font-size:1.4rem;font-weight:700;color:{fg};'>{val}</div>"
            f"<div style='font-size:0.78rem;color:#334155;margin-top:2px;'>{label}</div></div>"
            for label, val, bg, fg in [
                (t("browser_total", L), len(resources), "#eef2ff", "#4338ca"),
                (t("browser_chinese", L), lang_counts.get("zh", 0), "#fef3c7", "#92400e"),
                (t("browser_channels", L), type_counts.get("channel", 0), "#dbeafe", "#1e40af"),
                (t("browser_repos", L), type_counts.get("repo", 0), "#dcfce7", "#166534"),
                (t("browser_foundational", L), focus_counts.get("foundational", 0), "#f3e8ff", "#6b21a8"),
                (t("browser_applied", L), focus_counts.get("applied", 0), "#ffe4e6", "#9f1239"),
            ]
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    search_query = st.text_input(
        t("browser_search", L),
        placeholder=t("browser_search_placeholder", L),
    )

    all_topics = sorted({tp for r in resources for tp in r["topics"]})
    all_types = sorted({r["type"] for r in resources})
    all_levels = sorted({r["level"] for r in resources})
    all_domains = sorted({d for r in resources for d in r.get("domain", ["general"])})
    all_focuses = sorted({r.get("focus", "both") for r in resources})

    c1, c2, c3 = st.columns(3)
    with c1:
        selected_topics = st.multiselect(t("browser_topic", L), all_topics)
    with c2:
        selected_types = st.multiselect(t("browser_type", L), all_types)
    with c3:
        selected_levels = st.multiselect(t("browser_level", L), all_levels)

    c4, c5 = st.columns(2)
    with c4:
        selected_domains = st.multiselect(t("browser_domain", L), all_domains)
    with c5:
        selected_focuses = st.multiselect(t("browser_focus_filter", L), all_focuses, format_func=lambda x: FOCUS_EMOJI.get(x, x))

    filtered = resources
    if search_query:
        q = search_query.lower()
        filtered = [
            r for r in filtered
            if q in r["title"].lower()
            or q in r.get("description", "").lower()
            or any(q in tp for tp in r.get("topics", []))
        ]
    if selected_topics:
        filtered = [r for r in filtered if any(tp in r["topics"] for tp in selected_topics)]
    if selected_types:
        filtered = [r for r in filtered if r["type"] in selected_types]
    if selected_levels:
        filtered = [r for r in filtered if r["level"] in selected_levels]
    if selected_domains:
        filtered = [r for r in filtered if any(d in r.get("domain", ["general"]) for d in selected_domains)]
    if selected_focuses:
        filtered = [r for r in filtered if r.get("focus", "both") in selected_focuses]

    st.caption(t("browser_showing", L, shown=len(filtered), total=len(resources)))
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
        hours = r.get("duration_hours")
        if hours:
            unit = "wk" if L == "en" else "周"
            duration_text = f"⏱ {hours}h/{unit}" if r["type"] == "channel" else f"⏱ {hours}h"
        else:
            duration_text = ""
        cols[2].caption(f"{duration_text} · {focus_tag}" if duration_text else focus_tag)
