"""Path display and analytics views."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from html import escape as html_escape

import streamlit as st

from config import FOCUS_EMOJI, LEVEL_EMOJI, LEVEL_ORDER, TYPE_EMOJI
from i18n import t
from utils import export_plan_json, export_plan_markdown
from views import _lang
from views.progress import render_progress_save


def render_path(path_data: dict[str, object], resources: list[dict[str, object]]) -> None:
    L = _lang()
    ridx = {r["id"]: r for r in resources}

    est_weeks = path_data.get('estimated_weeks', '?')
    finish_tag = ""
    if isinstance(est_weeks, (int, float)) and est_weeks > 0:
        finish_date = (datetime.now() + timedelta(weeks=int(est_weeks))).strftime("%Y-%m-%d")
        finish_label = "预计完成" if L == "zh" else "Target"
        finish_tag = f" · {finish_label} {finish_date}"

    st.markdown(
        f"<div style='padding:20px 24px;background:linear-gradient(135deg,#eef2ff 0%,#e0e7ff 100%);"
        f"border-radius:14px;margin-bottom:16px;'>"
        f"<div style='font-size:1.1rem;font-weight:600;color:#3730a3;'>🧭 {html_escape(str(path_data.get('summary', '')))}</div>"
        f"<div style='font-size:0.85rem;color:#4338ca;margin-top:6px;'>"
        f"{t('path_weeks', L)} <b>{html_escape(str(est_weeks))}</b> {t('path_weeks_unit', L)}{finish_tag}</div></div>",
        unsafe_allow_html=True,
    )
    st.divider()

    total_resources = 0
    done_count = 0
    hours_budget = st.session_state.get("profile", {}).get("hours_per_week")

    for week in path_data.get("weeks", []):
        expanded = week["week"] <= 2
        # Calculate weekly hours for header
        w_res = [ridx.get(rid) for rid in week.get("resources", []) if ridx.get(rid)]
        w_hours = sum(r.get("duration_hours", 0) for r in w_res if r.get("type") not in ("channel", "builder"))
        hours_tag = ""
        if w_hours > 0:
            if hours_budget and hours_budget > 0:
                ratio = w_hours / hours_budget
                indicator = "\u2705" if ratio <= 1.1 else "\u26a0\ufe0f"
                hours_tag = f"  ({w_hours}h/{hours_budget}h {indicator})"
            else:
                hours_tag = f"  ({w_hours}h)"

        with st.expander(
            t("path_week", L, n=week['week']) + week['goal'] + hours_tag, expanded=expanded
        ):
            if week.get("tip"):
                st.info(f"💡 {week['tip']}")

            week_rids = week.get("resources", [])
            missing_count = sum(1 for rid in week_rids if rid not in ridx)
            if missing_count and not w_res:
                st.warning(t("path_week_no_resources", L) if L == "zh" else "No matching resources found for this week.")

            for rid in week.get("resources", []):
                r = ridx.get(rid)
                if not r:
                    continue

                total_resources += 1
                lvl_emoji = LEVEL_EMOJI.get(r["level"], "⚪")
                typ_emoji = TYPE_EMOJI.get(r["type"], "🔗")
                lang_tag = "🇨🇳 中文" if r.get("language") == "zh" else "🇬🇧 EN"
                is_channel = r.get("type") == "channel"

                cols = st.columns([5, 2, 2, 1])
                title_text = f"{typ_emoji} **[{r['title']}]({r['url']})**"
                if is_channel:
                    title_text += f"  `{t('path_ongoing', L)}`"
                cols[0].markdown(title_text)
                cols[0].caption(r.get("description", ""))
                cols[1].caption(f"{lvl_emoji} {r['level']}")
                hours = r.get("duration_hours")
                if hours:
                    unit = "wk" if L == "en" else "周"
                    duration_label = f"⏱ ~{hours}h/{unit}" if is_channel else f"⏱ {hours}h"
                else:
                    duration_label = ""
                cols[2].caption(f"{duration_label} · {lang_tag}" if duration_label else lang_tag)
                done_key = f"done_{rid}_{week['week']}"
                checked = cols[3].checkbox("✓", key=done_key, label_visibility="collapsed")
                if checked:
                    done_count += 1

            # Recommended builders for this week
            week_builders = week.get("builders", [])
            if week_builders:
                builder_names = []
                for bid in week_builders:
                    b = ridx.get(bid)
                    if b:
                        builder_names.append(
                            f"[{b['title']}]({b['url']})"
                        )
                if builder_names:
                    names_str = " · ".join(builder_names)
                    follow_label = "推荐关注" if L == "zh" else "Follow"
                    st.caption(f"👤 {follow_label}: {names_str}")

            st.write("")

    # 进度条
    st.divider()
    if total_resources > 0:
        progress = done_count / total_resources
        st.progress(progress, text=t("path_progress", L, done=done_count, total=total_resources))

    # 保存进度（含勾选状态 + 对话记录）
    render_progress_save()

    # 导出学习计划
    st.divider()
    st.markdown(
        "<div style='padding:16px 20px;background:#f8fafc;border-radius:12px;"
        "border:1px solid #e2e8f0;margin-bottom:12px;'>"
        f"<div style='font-size:1rem;font-weight:600;color:#334155;'>{t('path_save_title', L)}</div>"
        f"<div style='font-size:0.78rem;color:#64748b;margin-top:4px;'>"
        f"{t('path_save_hint', L)}</div></div>",
        unsafe_allow_html=True,
    )
    dl_cols = st.columns(2)
    with dl_cols[0]:
        profile = st.session_state.get("profile", {})
        md_content = export_plan_markdown(path_data, profile, resources)
        st.download_button(
            t("path_export_md", L),
            data=md_content,
            file_name="ai-learning-path.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with dl_cols[1]:
        json_content = export_plan_json(path_data, profile)
        st.download_button(
            t("path_export_json", L),
            data=json_content,
            file_name="ai-learning-path.json",
            mime="application/json",
            use_container_width=True,
        )

    # 学习统计
    render_path_analytics(path_data, resources)


def render_path_analytics(path_data: dict[str, object], resources: list[dict[str, object]]) -> None:
    """渲染学习路径的可视化分析面板。"""
    ridx = {r["id"]: r for r in resources}
    weeks = path_data.get("weeks", [])
    if not weeks:
        return

    path_resources = []
    for w in weeks:
        for rid in w.get("resources", []):
            r = ridx.get(rid)
            if r:
                path_resources.append((w["week"], r))

    if not path_resources:
        return

    st.divider()
    L = _lang()
    st.markdown(
        "<div style='padding:16px 20px;background:linear-gradient(135deg,#f0fdf4 0%,#ecfdf5 100%);"
        "border-radius:12px;border:1px solid #bbf7d0;margin-bottom:16px;'>"
        f"<div style='font-size:1rem;font-weight:600;color:#166534;'>{t('analytics_title', L)}</div>"
        f"<div style='font-size:0.78rem;color:#15803d;margin-top:4px;'>"
        f"{t('analytics_hint', L)}</div></div>",
        unsafe_allow_html=True,
    )

    all_r = [r for _, r in path_resources]
    total_hours = sum(r.get("duration_hours", 0) for r in all_r if r["type"] not in ("channel", "builder"))
    type_counts = Counter(r["type"] for r in all_r)
    focus_counts = Counter(r.get("focus", "both") for r in all_r)
    topic_counts = Counter(tp for r in all_r for tp in r.get("topics", []))
    lang_counts = Counter(r.get("language", "?") for r in all_r)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t("analytics_total", L), len(all_r))
    m2.metric(t("analytics_hours", L), f"{total_hours}h")
    m3.metric(t("analytics_weeks", L), len(weeks))
    lang_label = f"中{lang_counts.get('zh',0)} / 英{lang_counts.get('en',0)}" if L == "zh" else f"ZH {lang_counts.get('zh',0)} / EN {lang_counts.get('en',0)}"
    m4.metric(t("analytics_lang", L), lang_label)

    st.write("")
    tab1, tab2, tab3 = st.tabs([t("analytics_tab_dist", L), t("analytics_tab_pace", L), t("analytics_tab_topics", L)])

    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(t("analytics_type_comp", L))
            for typ, cnt in type_counts.most_common():
                emoji = TYPE_EMOJI.get(typ, "🔗")
                pct = cnt / len(all_r) * 100
                bar_width = max(int(pct * 2.5), 10)
                st.markdown(
                    f"<div style='display:flex;align-items:center;margin-bottom:6px;'>"
                    f"<div style='width:100px;font-size:0.82rem;'>{emoji} {typ}</div>"
                    f"<div style='flex:1;background:#f1f5f9;border-radius:6px;height:22px;position:relative;'>"
                    f"<div style='width:{bar_width}%;background:linear-gradient(90deg,#4f46e5,#6d28d9);"
                    f"border-radius:6px;height:100%;'></div>"
                    f"<span style='position:absolute;right:8px;top:2px;font-size:0.72rem;color:#1e293b;'>"
                    f"{cnt} ({pct:.0f}%)</span></div></div>",
                    unsafe_allow_html=True,
                )
        with col_b:
            st.markdown(t("analytics_focus_dist", L))
            focus_colors = {"foundational": "#8b5cf6", "applied": "#ef4444", "both": "#3b82f6"}
            for foc, cnt in focus_counts.most_common():
                label = FOCUS_EMOJI.get(foc, foc)
                pct = cnt / len(all_r) * 100
                color = focus_colors.get(foc, "#64748b")
                bar_width = max(int(pct * 2.5), 10)
                st.markdown(
                    f"<div style='display:flex;align-items:center;margin-bottom:6px;'>"
                    f"<div style='width:120px;font-size:0.82rem;'>{label}</div>"
                    f"<div style='flex:1;background:#f1f5f9;border-radius:6px;height:22px;position:relative;'>"
                    f"<div style='width:{bar_width}%;background:{color};border-radius:6px;height:100%;'></div>"
                    f"<span style='position:absolute;right:8px;top:2px;font-size:0.72rem;color:#334155;'>"
                    f"{cnt} ({pct:.0f}%)</span></div></div>",
                    unsafe_allow_html=True,
                )

    with tab2:
        st.markdown(t("analytics_weekly_pace", L))
        for w in weeks:
            w_resources = [ridx.get(rid) for rid in w.get("resources", []) if ridx.get(rid)]
            w_hours = sum(r.get("duration_hours", 0) for r in w_resources if r["type"] not in ("channel", "builder"))
            w_count = len(w_resources)
            levels = [LEVEL_ORDER.get(r["level"], 3) for r in w_resources]
            avg_level = sum(levels) / len(levels) if levels else 3
            level_labels = (
                {1: "🟢入门", 2: "🟢初级", 3: "🟡中级", 4: "🟡进阶", 5: "🔴高级"}
                if L == "zh" else
                {1: "🟢Beginner", 2: "🟢Elementary", 3: "🟡Intermediate", 4: "🟡Advanced", 5: "🔴Expert"}
            )
            avg_label = level_labels.get(round(avg_level), "🟡中级")
            hour_bar = min(int(w_hours / 0.5), 250)
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;'>"
                f"<div style='width:70px;font-weight:600;font-size:0.82rem;color:#1e293b;'>{'第' + str(w['week']) + '周' if L == 'zh' else 'Wk ' + str(w['week'])}</div>"
                f"<div style='flex:1;background:#f1f5f9;border-radius:6px;height:26px;position:relative;'>"
                f"<div style='width:{hour_bar}px;background:linear-gradient(90deg,#34d399,#059669);"
                f"border-radius:6px;height:100%;'></div>"
                f"<span style='position:absolute;left:8px;top:4px;font-size:0.72rem;color:#0f172a;'>"
                f"{w_hours}h · {w_count} {'资源' if L == 'zh' else 'items'} · {avg_label}</span></div></div>",
                unsafe_allow_html=True,
            )

    with tab3:
        st.markdown(t("analytics_top_topics", L))
        top_topics = topic_counts.most_common(15)
        if top_topics:
            max_count = top_topics[0][1]
            for topic, cnt in top_topics:
                pct = cnt / max_count * 100
                st.markdown(
                    f"<div style='display:flex;align-items:center;margin-bottom:4px;'>"
                    f"<div style='width:130px;font-size:0.8rem;color:#334155;'><code>{topic}</code></div>"
                    f"<div style='flex:1;background:#f1f5f9;border-radius:4px;height:18px;'>"
                    f"<div style='width:{pct:.0f}%;background:linear-gradient(90deg,#fbbf24,#f59e0b);"
                    f"border-radius:4px;height:100%;'></div></div>"
                    f"<div style='width:30px;text-align:right;font-size:0.75rem;color:#475569;'>{cnt}</div></div>",
                    unsafe_allow_html=True,
                )
