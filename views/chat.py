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

# ─── Follow-up suggestion engine ─────────────────────────────────────────────

_TOPIC_SUGGESTIONS_ZH: list[tuple[list[str], list[str]]] = [
    (["RAG", "检索增强", "向量"], ["RAG 和 Fine-tuning 哪个更适合我的场景？", "推荐一个 RAG 入门项目"]),
    (["Agent", "智能体", "多工具", "LangChain", "LangGraph"], ["如何选择 Agent 框架？", "Agent 开发有哪些常见坑？"]),
    (["Transformer", "注意力", "Attention"], ["Transformer 论文该怎么读？", "Attention 机制的直觉解释是什么？"]),
    (["微调", "Fine-tun", "LoRA", "PEFT"], ["微调需要多大的数据集？", "LoRA 和全量微调的区别是什么？"]),
    (["部署", "deploy", "API", "生产"], ["模型部署的最佳实践是什么？", "如何监控线上模型性能？"]),
    (["Python", "编程", "代码"], ["Python 学到什么程度够用？", "有什么好的 Python 练手项目？"]),
    (["论文", "paper", "研究"], ["如何高效阅读 AI 论文？", "推荐几篇必读的经典论文"]),
    (["测试", "QA", "质量"], ["AI 怎么辅助自动化测试？", "测试工程师转 AI 的路线建议？"]),
    (["大牛", "关注", "builder", "follow"], ["还有哪些值得关注的大牛？", "这些大牛都在研究什么方向？"]),
]

_TOPIC_SUGGESTIONS_EN: list[tuple[list[str], list[str]]] = [
    (["RAG", "retrieval", "vector"], ["RAG vs fine-tuning — which fits my use case?", "Recommend a RAG starter project"]),
    (["Agent", "multi-tool", "LangChain", "LangGraph"], ["How to choose an Agent framework?", "Common pitfalls in Agent development?"]),
    (["Transformer", "attention"], ["How should I read the Transformer paper?", "Intuitive explanation of attention?"]),
    (["fine-tun", "LoRA", "PEFT"], ["How much data do I need for fine-tuning?", "LoRA vs full fine-tuning?"]),
    (["deploy", "API", "production"], ["Best practices for model deployment?", "How to monitor models in production?"]),
    (["Python", "coding", "code"], ["How much Python is enough?", "Good Python practice projects?"]),
    (["paper", "research"], ["How to read AI papers efficiently?", "Top must-read AI papers?"]),
    (["testing", "QA", "quality"], ["How can AI assist automated testing?", "Career path from QA to AI?"]),
    (["builder", "follow", "expert"], ["Other AI builders worth following?", "What are these builders working on?"]),
]

_GENERIC_ZH = ["下一步我该学什么？", "帮我推荐一个练手项目", "我的学习路径有什么可以优化的？"]
_GENERIC_EN = ["What should I learn next?", "Suggest a hands-on project", "How can I improve my learning path?"]


def _get_follow_ups(reply: str, L: str) -> list[str]:
    """Pick 2-3 follow-up suggestions based on reply keywords."""
    table = _TOPIC_SUGGESTIONS_ZH if L == "zh" else _TOPIC_SUGGESTIONS_EN
    generic = _GENERIC_ZH if L == "zh" else _GENERIC_EN
    reply_lower = reply.lower()
    matched: list[str] = []
    for keywords, suggestions in table:
        if any(kw.lower() in reply_lower for kw in keywords):
            for s in suggestions:
                if s not in matched:
                    matched.append(s)
            if len(matched) >= 3:
                break
    if not matched:
        matched = generic[:3]
    return matched[:3]


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
        direction = (st.session_state.get("profile") or {}).get("direction", "")
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

    # Follow-up suggestion buttons (when last message is from assistant)
    msgs = st.session_state.get("chat_messages", [])
    if msgs and msgs[-1]["role"] == "assistant":
        follow_ups = _get_follow_ups(msgs[-1]["content"], L)
        if follow_ups:
            fu_cols = st.columns(len(follow_ups))
            for i, fu in enumerate(follow_ups):
                if fu_cols[i].button(fu, key=f"followup_{i}", use_container_width=True):
                    st.session_state.chat_messages.append({"role": "user", "content": fu})
                    st.rerun()

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
                    if c.choices and c.choices[0].delta and getattr(c.choices[0].delta, "content", None)
                )
                # Post-process: strip any <think> blocks that slipped through
                reply = _strip_thinking(str(reply)) if reply else ""
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
