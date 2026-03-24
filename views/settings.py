"""API settings panel view."""

import streamlit as st

from config import PROVIDER_PRESETS
from i18n import t
from views import _lang


def render_settings():
    """侧边栏 API 设置面板"""
    L = _lang()
    with st.expander(t("settings_title", L), expanded=False):
        provider = st.selectbox(
            t("settings_provider", L),
            list(PROVIDER_PRESETS.keys()),
            key="settings_provider",
        )
        preset = PROVIDER_PRESETS[provider]

        if provider == "自定义":
            st.text_input(
                t("settings_custom_url", L),
                placeholder="https://your-api.com/v1",
                key="settings_base_url",
            )
            st.text_input(
                t("settings_custom_model", L),
                placeholder="your-model-name",
                key="settings_model_text",
            )
        else:
            model_key = f"settings_model_{provider}"
            if st.session_state.get(model_key, preset["models"][0]) not in preset["models"]:
                st.session_state[model_key] = preset["models"][0]
            st.selectbox(t("settings_model", L), preset["models"], key=model_key)

        st.text_input(
            t("settings_key", L),
            type="password",
            key="settings_api_key",
            placeholder="sk-...",
        )
        if st.session_state.get("settings_api_key"):
            st.caption("✅ " + ("将使用你的 API Key" if L == "zh" else "Using your API Key"))
        else:
            st.caption("ℹ️ " + ("使用服务器 Key（共享，可能限流）" if L == "zh" else "Using shared server key (may be rate-limited)"))
