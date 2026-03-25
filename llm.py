"""LLM client: configuration, path generation, trend insights."""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from collections.abc import Callable
from datetime import datetime

import streamlit as st
from openai import OpenAI

from config import PROVIDER_PRESETS, SYSTEM_PROMPT
from logging_config import get_logger

_log = get_logger("llm")

_PATH_TIMEOUT = 25  # seconds – hard cap for path generation API call
_TOTAL_TIME_LIMIT = 90  # seconds – absolute wall-clock cap for streaming


def _strip_thinking(text: str) -> str:
    """Remove <think>…</think> blocks that Qwen-3 thinking mode may emit."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _sanitize_text(text: str) -> str:
    """Remove surrogates and NUL that break protobuf / Streamlit encoding."""
    return re.sub(r"[\ud800-\udfff\x00]", "", text)


def get_llm_config() -> tuple[str, str, str]:
    """Return (api_key, base_url, model) from session/secrets/env."""
    api_key = (
        st.session_state.get("settings_api_key", "")
        or st.secrets.get("DASHSCOPE_API_KEY", "")
        or os.environ.get("DASHSCOPE_API_KEY", "")
    )
    provider = st.session_state.get("settings_provider", "DashScope (阿里云百炼)")
    preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["DashScope (阿里云百炼)"])
    if provider == "自定义":
        base_url = (
            st.session_state.get("settings_base_url", "")
            or st.secrets.get("API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        )
        model = (
            st.session_state.get("settings_model_text", "")
            or st.secrets.get("MODEL", "qwen3.5-plus")
        )
    else:
        base_url = preset["base_url"]
        model_key = f"settings_model_{provider}"
        model = st.session_state.get(model_key, preset["models"][0]) or preset["models"][0]
    return api_key, base_url, model


def _compact_resources(resources: list[dict[str, object]]) -> str:
    """Compact resource list to minimal token footprint."""
    lines = []
    for r in resources:
        topics = ",".join(r["topics"][:2])
        focus = r.get("focus", "both")
        focus_tag = "" if focus == "both" else f"|{focus}"
        lines.append(
            f"{r['id']}|{r['title']}|{r['type']}|{r['level']}|{r['duration_hours']}h{focus_tag}|{topics}"
        )
    return "\n".join(lines)


def _path_cache_key(profile: dict[str, object], resources: list[dict[str, object]]) -> str:
    """Deterministic cache key from profile + resource ids."""
    raw = json.dumps(
        {"p": profile, "r": [r["id"] for r in resources]},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def generate_path(
    profile: dict[str, object],
    resources: list[dict[str, object]],
    *,
    on_progress: Callable[[int], None] | None = None,
) -> dict[str, object]:
    """Call LLM to generate a personalized learning path (streaming).

    Parameters
    ----------
    on_progress:
        Optional callback invoked with accumulated character count during
        streaming so the caller can show progress.
    """
    # ── cache hit → instant return ──────────────────────────────────────
    cache_key = _path_cache_key(profile, resources)
    path_cache: dict[str, dict[str, object]] = st.session_state.setdefault("_path_cache", {})
    if cache_key in path_cache:
        _log.info("generate_path cache hit key=%s", cache_key)
        return path_cache[cache_key]

    # ── LLM call ────────────────────────────────────────────────────────
    api_key, base_url, model = get_llm_config()
    if not api_key:
        raise ValueError("请配置 DASHSCOPE_API_KEY")

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=_PATH_TIMEOUT)

    compact = _compact_resources(resources)

    user_msg = f"""用户信息：
- 当前水平：{profile['level']}
- 目标方向：{profile.get('direction', '通用AI方向')}
- 学习目标：{profile['goal']}
- 当前技能/项目经历：{profile.get('skills_background') or '（未填写）'}
- 学习重心：{profile.get('focus', 'both')}
- 每周可投入时间：{profile['hours_per_week']} 小时
- 偏好学习方式：{profile['preference']}
- 语言偏好：{profile['language']}

可用资源（{len(resources)}条，格式: id|标题|类型|难度|时长|话题）：
{compact}

请生成个性化学习路径。"""

    _log.info("generate_path model=%s resources=%d direction=%s", model, len(resources), profile.get('direction', ''))

    t0 = time.monotonic()
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.15,
        max_tokens=1500,
        stream=True,
        extra_body={"enable_thinking": False},
    )
    chunks: list[str] = []
    char_count = 0
    for chunk in stream:
        if time.monotonic() - t0 > _TOTAL_TIME_LIMIT:
            _log.warning("generate_path aborted: exceeded %ds wall-clock", _TOTAL_TIME_LIMIT)
            break
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            chunks.append(delta.content)
            char_count += len(delta.content)
            if on_progress is not None:
                on_progress(char_count)
    full = _strip_thinking("".join(chunks))
    result = json.loads(full)
    path_cache[cache_key] = result
    elapsed = time.monotonic() - t0
    _log.info("generate_path completed weeks=%d chars=%d elapsed=%.1fs", len(result.get('weeks', [])), char_count, elapsed)
    return result


# ─── 趋势洞察 ─────────────────────────────────────────────────────────────────

INSIGHTS_CACHE_PATH = os.path.join(os.path.dirname(__file__), "insights_cache.json")

TREND_INSIGHT_PROMPT = """你是一位资深 AI 行业分析师。基于以下 AI 信息源列表和你对当前 AI 领域的最新认知，生成今日 AI 趋势洞察报告。

要求：
1. 生成 5-7 条关键洞察，每条聚焦一个具体趋势
2. 每条洞察包含：标题（简洁有力）、摘要（2-3句话解释趋势意义）、对学员的行动建议
3. 覆盖多个子领域：LLM/Agent/多模态/开源/工程化/研究等
4. 用批判视角：既指出机会也指出风险与泡沫
5. 面向 AI 学习者，语言简洁实用
6. 添加一个"本期总结"字段，用一段话概括整体趋势走向

输出纯 JSON：
{
  "date": "YYYY-MM-DD",
  "overview": "本期总结...",
  "insights": [
    {
      "title": "趋势标题",
      "summary": "趋势说明...",
      "action": "学员应该...",
      "tags": ["LLM", "Agent"]
    }
  ]
}"""

PERSONALIZED_TREND_PROMPT = """你是一位资深 AI 行业分析师。用户正在学习 **{direction}** 方向。
基于以下信息源和你对 AI 领域的最新认知，生成为该方向**量身定制**的趋势洞察。

要求：
1. 生成 5-7 条洞察，其中 **至少 3 条直接与 {direction} 相关**，其余覆盖通用趋势
2. 每条洞察包含：标题、摘要（2-3句话）、针对该方向学习者的行动建议
3. 用批判视角：既指出机会也指出风险与泡沫
4. 行动建议要具体可执行，关联到具体的工具、框架或论文
5. 添加"本期总结"字段，结合 {direction} 方向给出学习建议

输出纯 JSON：
{{
  "date": "YYYY-MM-DD",
  "overview": "本期总结...",
  "direction": "{direction}",
  "insights": [
    {{
      "title": "趋势标题",
      "summary": "趋势说明...",
      "action": "你正在学 {direction}，建议...",
      "tags": ["LLM", "Agent"]
    }}
  ]
}}"""


def _load_insights_cache(direction: str = "") -> dict[str, object] | None:
    """Load cached insights if fresh (same date and direction)."""
    if not os.path.exists(INSIGHTS_CACHE_PATH):
        return None
    try:
        with open(INSIGHTS_CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") == datetime.now().strftime("%Y-%m-%d") and data.get("direction", "") == direction:
            return data
    except Exception:
        pass
    return None


def _save_insights_cache(data: dict[str, object]) -> None:
    """Save insights to local cache file."""
    try:
        with open(INSIGHTS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        _log.warning("insights_cache_save_failed: %s", e)


def generate_trend_insights(
    channels: list[dict[str, object]],
    force_refresh: bool = False,
    direction: str = "",
) -> dict[str, object]:
    """Generate daily AI trend insights via LLM, with local caching.

    When *direction* is provided the prompt is personalised to that
    learning direction so the insights are more actionable for the user.
    """
    if not force_refresh:
        cached = _load_insights_cache(direction)
        if cached:
            _log.info("trend_insights loaded from cache date=%s direction=%s", cached.get("date"), direction)
            return cached

    try:
        api_key, base_url, model = get_llm_config()
        if not api_key:
            return {}

        client = OpenAI(api_key=api_key, base_url=base_url, timeout=_PATH_TIMEOUT)

        source_list = "\n".join(
            f"- {ch['title']} ({ch.get('language','')}) — {ch.get('description','')}"
            for ch in channels
        )

        if direction:
            system_prompt = PERSONALIZED_TREND_PROMPT.format(direction=direction)
        else:
            system_prompt = TREND_INSIGHT_PROMPT

        _log.info("generate_trend_insights model=%s sources=%d direction=%s", model, len(channels), direction or "(generic)")

        t0 = time.monotonic()
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"今天是 {datetime.now().strftime('%Y-%m-%d')}。\n\n参考信息源：\n{source_list}\n\n请生成今日趋势洞察。"},
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
            max_tokens=2000,
            stream=True,
            extra_body={"enable_thinking": False},
        )
        chunks = []
        for chunk in stream:
            if time.monotonic() - t0 > _TOTAL_TIME_LIMIT:
                _log.warning("trend_insights aborted: exceeded %ds wall-clock", _TOTAL_TIME_LIMIT)
                break
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                chunks.append(delta.content)
        result = json.loads(_strip_thinking("".join(chunks)))
        if not isinstance(result, dict):
            result = {}
        if not isinstance(result.get("insights"), list):
            result["insights"] = []
        result["insights"] = [
            ins for ins in result["insights"] if isinstance(ins, dict)
        ]
        result["date"] = datetime.now().strftime("%Y-%m-%d")
        result["direction"] = direction
        _save_insights_cache(result)
        _log.info("trend_insights generated insights=%d", len(result.get("insights", [])))
        return result
    except Exception as e:
        _log.error("trend_insights_failed: %s", e)
        return _load_insights_cache(direction) or {}
