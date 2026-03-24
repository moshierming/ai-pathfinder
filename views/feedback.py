"""Feedback collection view."""

import json
import os
import urllib.request
from datetime import datetime, timezone

import streamlit as st

from i18n import t
from logging_config import get_logger

from views import _lang

_log = get_logger("feedback")


def submit_feedback(feedback: dict) -> str:
    """Save feedback: local file (always try) + GitHub Issues (if token). Returns 'github' or 'local'."""
    try:
        feedback_dir = os.path.join(os.path.dirname(__file__), "..", "feedback")
        os.makedirs(feedback_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        with open(os.path.join(feedback_dir, f"fb_{ts}.json"), "w", encoding="utf-8") as f:
            json.dump(feedback, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    token = st.secrets.get("GITHUB_TOKEN", "") or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return "local"

    L = _lang()
    profile = feedback.get("profile", {})
    body = (
        f"**评分**: {feedback['rating']}\n\n"
        f"**意见**: {feedback.get('comment') or '（无）'}\n\n"
        f"**方向**: {profile.get('direction', '-')}\n"
        f"**水平**: {profile.get('level', '-')}\n"
        f"**时间**: {profile.get('hours_per_week', '-')}h/{'wk' if L == 'en' else '周'}\n"
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
        _log.info("feedback_github_submitted")
        return "github"
    except Exception as e:
        _log.warning("feedback_github_failed: %s", e)
        return "local"


def render_feedback():
    L = _lang()
    st.divider()
    st.subheader(t("fb_title", L))
    st.caption(t("fb_hint", L))

    with st.form("feedback_form"):
        rating = st.select_slider(
            t("fb_rating", L),
            options=["完全没用", "一般", "有点帮助", "很有帮助", "太赞了"] if L == "zh"
            else ["Not helpful", "Okay", "Somewhat helpful", "Very helpful", "Amazing"],
            value="有点帮助" if L == "zh" else "Somewhat helpful",
        )
        comment = st.text_area(
            t("fb_comment", L),
            placeholder=t("fb_comment_placeholder", L),
            height=80,
        )
        submitted = st.form_submit_button(t("fb_submit", L))

    if submitted:
        feedback = {
            "rating": rating,
            "comment": comment,
            "profile": st.session_state.get("profile", {}),
        }
        result = submit_feedback(feedback)
        if result == "github":
            st.success(t("fb_thanks_github", L))
        else:
            st.success(t("fb_thanks_local", L))
