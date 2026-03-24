"""LLM client: configuration, path generation, trend insights."""

import json
import os
from datetime import datetime

import streamlit as st
from openai import OpenAI

from config import PROVIDER_PRESETS, SYSTEM_PROMPT
from logging_config import get_logger

_log = get_logger("llm")


def get_llm_config():
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


def _compact_resources(resources: list) -> str:
    """Compact resource list to minimal token footprint."""
    lines = []
    for r in resources:
        topics = ",".join(r["topics"][:3])
        domain = ",".join(r.get("domain", ["general"])[:2])
        lines.append(
            f"{r['id']}|{r['title']}|{r['type']}|{r['level']}|{r['duration_hours']}h|"
            f"{r.get('focus','both')}|{domain}|{topics}"
        )
    return "\n".join(lines)


def generate_path(profile: dict, resources: list) -> dict:
    """Call LLM to generate a personalized learning path (streaming)."""
    api_key, base_url, model = get_llm_config()
    if not api_key:
        raise ValueError("请配置 DASHSCOPE_API_KEY")

    client = OpenAI(api_key=api_key, base_url=base_url)

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

可用资源（{len(resources)}条，格式: id|标题|类型|难度|时长|侧重|方向|话题）：
{compact}

请生成个性化学习路径。"""

    _log.info("generate_path model=%s resources=%d direction=%s", model, len(resources), profile.get('direction', ''))

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=2500,
        stream=True,
    )
    chunks = []
    for chunk in stream:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            chunks.append(delta.content)
    full = "".join(chunks)
    result = json.loads(full)
    _log.info("generate_path completed weeks=%d", len(result.get('weeks', [])))
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


def _load_insights_cache():
    """Load cached insights if fresh (same date)."""
    if not os.path.exists(INSIGHTS_CACHE_PATH):
        return None
    try:
        with open(INSIGHTS_CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") == datetime.now().strftime("%Y-%m-%d"):
            return data
    except Exception:
        pass
    return None


def _save_insights_cache(data):
    """Save insights to local cache file."""
    try:
        with open(INSIGHTS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        _log.warning("insights_cache_save_failed: %s", e)


def generate_trend_insights(channels: list, force_refresh: bool = False) -> dict:
    """Generate daily AI trend insights via LLM, with local caching."""
    if not force_refresh:
        cached = _load_insights_cache()
        if cached:
            _log.info("trend_insights loaded from cache date=%s", cached.get("date"))
            return cached

    api_key, base_url, model = get_llm_config()
    if not api_key:
        return {}

    client = OpenAI(api_key=api_key, base_url=base_url)

    source_list = "\n".join(
        f"- {ch['title']} ({ch.get('language','')}) — {ch.get('description','')}"
        for ch in channels
    )

    _log.info("generate_trend_insights model=%s sources=%d", model, len(channels))

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": TREND_INSIGHT_PROMPT},
                {"role": "user", "content": f"今天是 {datetime.now().strftime('%Y-%m-%d')}。\n\n参考信息源：\n{source_list}\n\n请生成今日趋势洞察。"},
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
            max_tokens=2000,
            stream=True,
        )
        chunks = []
        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                chunks.append(delta.content)
        result = json.loads("".join(chunks))
        result["date"] = datetime.now().strftime("%Y-%m-%d")
        _save_insights_cache(result)
        _log.info("trend_insights generated insights=%d", len(result.get("insights", [])))
        return result
    except Exception as e:
        _log.error("trend_insights_failed: %s", e)
        return _load_insights_cache() or {}
