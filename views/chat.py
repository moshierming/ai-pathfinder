"""Chat view."""
from __future__ import annotations

import streamlit as st
from openai import OpenAI

from config import CHAT_SYSTEM_PROMPT, FOCUS_EMOJI
from i18n import t
from llm import get_llm_config
from logging_config import get_logger

from views import _lang

_log = get_logger("chat")


def _build_chat_context(resources: list[dict[str, object]]) -> str:
    """Build chat context: user profile + current path + resource & builder summary."""
    parts = []
    profile = st.session_state.get("profile")
    if profile:
        parts.append(f"用户画像：水平={profile.get('level','?')}, 方向={profile.get('direction','?')}, "
                      f"目标={profile.get('goal','?')}, 重心={profile.get('focus','?')}")
    path_data = st.session_state.get("path")
    if path_data:
        parts.append(f"当前学习路径：{path_data.get('summary','(无)')}, 共{path_data.get('estimated_weeks','?')}周")
        week_ids = []
        for w in path_data.get("weeks", []):
            week_ids.extend(w.get("resources", []))
        if week_ids:
            parts.append(f"路径中的资源ID：{', '.join(week_ids)}")

    # Learning resources (exclude builders)
    learning = [r for r in resources if r.get("type") != "builder"]
    summaries = [f"{r['id']}: {r['title']} ({r['type']}, {','.join(r.get('topics',[])[:3])})"
                 for r in learning[:60]]
    parts.append(f"资源库摘要（前60条）:\n" + "\n".join(summaries))

    # Builders
    builders = [r for r in resources if r.get("type") == "builder"]
    if builders:
        builder_lines = [
            f"{b['id']}: {b['title']} ({b.get('role','')}, {','.join(b.get('topics',[])[:3])}) — {b.get('description','')}"
            for b in builders
        ]
        parts.append(f"AI行业大牛（{len(builders)}位）:\n" + "\n".join(builder_lines))

    return "\n\n".join(parts)


def render_chat(resources: list[dict[str, object]]) -> None:
    L = _lang()
    st.title(t("chat_title", L))
    st.markdown(t("chat_subtitle", L))

    if st.session_state.get("profile"):
        p = st.session_state.profile
        st.caption(f"{'当前画像' if L == 'zh' else 'Profile'}：{p.get('level','')} · {p.get('direction','')} · {FOCUS_EMOJI.get(p.get('focus',''), '')}")
    else:
        st.caption(t("chat_no_profile", L))

    st.divider()

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input(t("chat_input", L))
    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        api_key, base_url, model = get_llm_config()
        if not api_key:
            with st.chat_message("assistant"):
                st.error(t("chat_no_key", L))
            return

        context = _build_chat_context(resources)

        messages = [
            {"role": "system", "content": CHAT_SYSTEM_PROMPT + "\n\n" + context},
        ]
        recent = st.session_state.chat_messages[-20:]
        messages.extend(recent)

        with st.chat_message("assistant"):
            with st.spinner(t("chat_thinking", L)):
                try:
                    client = OpenAI(api_key=api_key, base_url=base_url)
                    resp = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.5,
                        max_tokens=2000,
                    )
                    reply = resp.choices[0].message.content
                    st.markdown(reply)
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    _log.error("chat_error: %s", e)
                    st.error(f"{t('chat_error', L)}{e}")

    if st.session_state.chat_messages:
        st.divider()
        if st.button(t("chat_clear", L), use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
