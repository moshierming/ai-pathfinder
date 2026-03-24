"""Progress persistence: save / load learning progress across sessions."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import streamlit as st

from i18n import t
from logging_config import get_logger

from views import _lang

_log = get_logger("progress")


# ─── Progress directory ──────────────────────────────────────────────────────

_PROGRESS_DIR = os.path.join(os.path.dirname(__file__), "..", "progress")


def _ensure_dir() -> None:
    os.makedirs(_PROGRESS_DIR, exist_ok=True)


# ─── Collect / Restore ──────────────────────────────────────────────────────


def collect_progress() -> dict[str, object]:
    """Gather all saveable state into a dict."""
    done = {}
    for k, v in st.session_state.items():
        if isinstance(k, str) and k.startswith("done_") and v:
            done[k] = True

    return {
        "version": 1,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "profile": st.session_state.get("profile"),
        "path": st.session_state.get("path"),
        "done": done,
        "chat_messages": st.session_state.get("chat_messages", []),
        "ui_lang": st.session_state.get("ui_lang", "zh"),
    }


def restore_progress(data: dict[str, object]) -> bool:
    """Write saved state back into session_state. Returns True on success."""
    if not isinstance(data, dict):
        return False
    profile = data.get("profile")
    path = data.get("path")
    if not profile or not path:
        return False

    st.session_state["profile"] = profile
    st.session_state["path"] = path
    st.session_state["ui_lang"] = data.get("ui_lang", "zh")

    for k, v in data.get("done", {}).items():
        if isinstance(k, str) and k.startswith("done_"):
            st.session_state[k] = v

    chat = data.get("chat_messages")
    if isinstance(chat, list):
        st.session_state["chat_messages"] = chat

    return True


# ─── Local file persistence ────────────────────────────────────────────────


def save_progress_local() -> str | None:
    """Save current progress to server-side file. Returns filepath or None."""
    data = collect_progress()
    if not data.get("profile") or not data.get("path"):
        return None
    _ensure_dir()
    filepath = os.path.join(_PROGRESS_DIR, "latest.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    _log.info("progress_saved done=%d", len(data.get("done", {})))
    return filepath


def load_progress_local() -> dict[str, object] | None:
    """Load most recent saved progress. Returns dict or None."""
    filepath = os.path.join(_PROGRESS_DIR, "latest.json")
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def progress_to_json(data: dict[str, object] | None = None) -> str:
    """Serialize progress to downloadable JSON string."""
    if data is None:
        data = collect_progress()
    return json.dumps(data, ensure_ascii=False, indent=2)


# ─── UI helpers ─────────────────────────────────────────────────────────────


def render_progress_save() -> None:
    """Render save-progress section (call from path view)."""
    L = _lang()

    st.markdown(
        "<div style='padding:16px 20px;background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);"
        "border-radius:12px;border:1px solid #fbbf24;margin-bottom:12px;'>"
        f"<div style='font-size:1rem;font-weight:600;color:#92400e;'>{t('progress_save_title', L)}</div>"
        f"<div style='font-size:0.78rem;color:#a16207;margin-top:4px;'>"
        f"{t('progress_save_hint', L)}</div></div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    with cols[0]:
        if st.button(t("progress_save_server", L), use_container_width=True):
            path = save_progress_local()
            if path:
                st.success(t("progress_saved_ok", L))
            else:
                st.warning(t("progress_save_empty", L))

    with cols[1]:
        data = collect_progress()
        st.download_button(
            t("progress_download", L),
            data=progress_to_json(data),
            file_name="ai-pathfinder-progress.json",
            mime="application/json",
            use_container_width=True,
        )


def render_progress_restore() -> bool:
    """Render restore section in sidebar. Returns True if user restores."""
    L = _lang()
    saved = load_progress_local()
    if not saved:
        return False

    saved_at = saved.get("saved_at", "")
    if saved_at:
        try:
            dt = datetime.fromisoformat(saved_at)
            display_time = dt.strftime("%m-%d %H:%M")
        except (ValueError, TypeError):
            display_time = saved_at[:16]
    else:
        display_time = "?"

    done_count = len(saved.get("done", {}))
    profile = saved.get("profile", {})
    direction = profile.get("direction", "")

    st.caption(t("progress_found", L, time=display_time, done=done_count, direction=direction))
    if st.button(t("progress_restore", L), use_container_width=True):
        restore_progress(saved)
        from utils import encode_profile
        st.query_params["p"] = encode_profile(saved["profile"])
        st.rerun()

    return True
