"""View rendering functions for AI Pathfinder."""
from __future__ import annotations

import streamlit as st


def _lang() -> str:
    """Return current UI language (shared across all views)."""
    return st.session_state.get("ui_lang", "zh")
