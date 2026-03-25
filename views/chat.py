"""Chat view."""
from __future__ import annotations

import streamlit as st
from openai import OpenAI

from config import CHAT_SYSTEM_PROMPT, FOCUS_EMOJI
from i18n import t
from llm import get_llm_config, _sanitize_text, _strip_thinking
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
        st.caption(f"{t('chat_current_profile', L)}：{p.get('level','')} · {p.get('direction','')} · {FOCUS_EMOJI.get(p.get('focus',''), '')}")
    else:
        st.caption(t("chat_no_profile", L))

    st.divider()

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Suggested questions when chat is empty
    if not st.session_state.chat_messages:
        direction = st.session_state.get("profile", {}).get("direction", "")
        suggestions_zh = [
            "我应该从哪里开始学习？",
            "有哪些大牛值得关注？",
            f"学习{direction}需要哪些前置知识？" if direction else "学习AI需要哪些前置知识？",
            "帮我推荐适合练手的项目",
        ]
        suggestions_en = [
            "Where should I start learning?",
            "Who are the key people to follow?",
            f"What prerequisites do I need for {direction}?" if direction else "What prerequisites do I need?",
            "Suggest a hands-on project for practice",
        ]
        suggestions = suggestions_zh if L == "zh" else suggestions_en
        row1 = st.columns(2)
        row2 = st.columns(2)
        cols = row1 + row2
        for i, s in enumerate(suggestions):
            if cols[i].button(s, key=f"suggest_{i}", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": s})
                st.rerun()

    for msg in st.session_state.chat_messages[-50:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input(t("chat_input", L))
    if user_input:
        # Trim excessively long input
        if len(user_input) > 2000:
            user_input = user_input[:2000]
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        # Prune old messages to prevent unbounded growth
        if len(st.session_state.chat_messages) > 100:
            st.session_state.chat_messages = st.session_state.chat_messages[-60:]
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
            try:
                client = OpenAI(api_key=api_key, base_url=base_url)
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.5,
                    max_tokens=2000,
                    stream=True,
                    extra_body={"enable_thinking": False},
                )
                reply = st.write_stream(
                    _sanitize_text(c.choices[0].delta.content or "")
                    for c in stream
                    if c.choices and c.choices[0].delta and c.choices[0].delta.content
                )
                # Post-process: strip any <think> blocks that slipped through
                reply = _strip_thinking(reply) if reply else ""
                st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                _log.error("chat_error: %s", e)
                st.error(f"{t('chat_error', L)}{e}")

    if st.session_state.chat_messages:
        st.divider()
        btn_cols = st.columns(2)
        with btn_cols[0]:
            if st.button(t("chat_clear", L), use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
        with btn_cols[1]:
            md_lines = []
            for m in st.session_state.chat_messages:
                role = "**You**" if m["role"] == "user" else "**AI**"
                md_lines.append(f"{role}: {m['content']}\n")
            chat_md = "\n---\n\n".join(md_lines)
            st.download_button(
                t("chat_export", L),
                data=chat_md,
                file_name="ai-pathfinder-chat.md",
                mime="text/markdown",
                use_container_width=True,
            )
        if st.button(t("chat_clear", L), use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
