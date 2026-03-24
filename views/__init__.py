"""View rendering functions for AI Pathfinder."""

import streamlit as st


def _lang():
    """Return current UI language (shared across all views)."""
    return st.session_state.get("ui_lang", "zh")
