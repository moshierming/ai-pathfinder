"""Tests for core app functions (profile encoding, resource filtering, exports)."""

import sys, os, json, base64
from unittest.mock import MagicMock, patch

# Mock streamlit before importing app
sys.modules["streamlit"] = MagicMock()
sys.modules["openai"] = MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app


# ─── Sample data ──────────────────────────────────────────────────────────────

SAMPLE_RESOURCES = [
    {
        "id": "r001", "title": "Python Basics", "url": "https://example.com/py",
        "type": "course", "topics": ["python"], "domain": ["general"],
        "level": "beginner", "duration_hours": 10, "description": "Intro to Python",
        "language": "en", "free": True, "focus": "foundational",
    },
    {
        "id": "r002", "title": "LangChain实战", "url": "https://example.com/lc",
        "type": "repo", "topics": ["langchain", "llm", "rag"], "domain": ["llm-app"],
        "level": "intermediate", "duration_hours": 15, "description": "LangChain hands-on",
        "language": "zh", "free": True, "focus": "applied",
    },
    {
        "id": "r003", "title": "ML Math", "url": "https://example.com/ml",
        "type": "article", "topics": ["math", "ml"], "domain": ["data-science"],
        "level": "intermediate", "duration_hours": 8, "description": "ML math foundations",
        "language": "en", "free": True, "focus": "foundational",
    },
    {
        "id": "r004", "title": "Agent Dev", "url": "https://example.com/agent",
        "type": "course", "topics": ["agent", "langchain"], "domain": ["ai-agent", "llm-app"],
        "level": "advanced", "duration_hours": 20, "description": "Build agents",
        "language": "en", "free": True, "focus": "applied",
    },
    {
        "id": "r005", "title": "AI Newsletter", "url": "https://example.com/news",
        "type": "channel", "topics": ["ai", "trends"], "domain": ["general"],
        "level": "beginner", "duration_hours": 1, "description": "Weekly AI news",
        "language": "en", "free": True, "focus": "both",
    },
]

SAMPLE_PROFILE = {
    "level": "📗 会Python，了解基本ML概念",
    "goal": "学会RAG问答系统",
    "hours_per_week": 8,
    "preference": "⚖️ 均衡搭配",
    "language": "🇨🇳 优先中文资源",
    "direction": "💬 LLM 应用开发 / RAG",
    "focus": "⚖️ 理论+实战均衡",
}

SAMPLE_PATH = {
    "summary": "从Python基础到RAG实战",
    "estimated_weeks": 4,
    "weeks": [
        {"week": 1, "goal": "Python基础", "tip": "多动手", "resources": ["r001"]},
        {"week": 2, "goal": "LangChain入门", "resources": ["r002"]},
        {"week": 3, "goal": "ML数学", "resources": ["r003"]},
        {"week": 4, "goal": "Agent实战", "resources": ["r004", "r005"]},
    ],
}


# ─── Profile Encoding ────────────────────────────────────────────────────────


class TestEncodeProfile:
    def test_roundtrip(self):
        encoded = app.encode_profile(SAMPLE_PROFILE)
        decoded = app.decode_profile(encoded)
        assert decoded == SAMPLE_PROFILE

    def test_encode_returns_base64_string(self):
        encoded = app.encode_profile({"level": "beginner"})
        assert isinstance(encoded, str)
        # Should be valid base64
        raw = base64.urlsafe_b64decode(encoded.encode()).decode()
        assert json.loads(raw) == {"level": "beginner"}

    def test_decode_invalid_returns_none(self):
        assert app.decode_profile("not-valid-base64!!!") is None

    def test_decode_non_json_returns_none(self):
        encoded = base64.urlsafe_b64encode(b"not json").decode()
        assert app.decode_profile(encoded) is None

    def test_empty_profile(self):
        encoded = app.encode_profile({})
        decoded = app.decode_profile(encoded)
        assert decoded == {}

    def test_unicode_profile(self):
        profile = {"goal": "学习AI的数学基础 📊"}
        encoded = app.encode_profile(profile)
        decoded = app.decode_profile(encoded)
        assert decoded == profile


# ─── Resource Filtering ──────────────────────────────────────────────────────


class TestFilterResources:
    def test_direction_filter_llm_app(self):
        result = app.filter_resources_for_direction(
            SAMPLE_RESOURCES, "💬 LLM 应用开发 / RAG", "🌍 不限语言"
        )
        ids = [r["id"] for r in result]
        # r002 (llm-app) and r004 (ai-agent+llm-app) should come before r003 (data-science)
        assert "r002" in ids
        assert "r004" in ids

    def test_direction_filter_unknown_returns_all(self):
        result = app.filter_resources_for_direction(
            SAMPLE_RESOURCES, "🌐 其他 / 尚未确定", "🌍 不限语言"
        )
        assert len(result) == len(SAMPLE_RESOURCES)

    def test_language_preference_zh(self):
        result = app.filter_resources_for_direction(
            SAMPLE_RESOURCES, "🌐 其他 / 尚未确定", "🇨🇳 优先中文资源"
        )
        # First resource should be zh-language
        assert result[0]["language"] == "zh"

    def test_language_preference_en(self):
        result = app.filter_resources_for_direction(
            SAMPLE_RESOURCES, "🌐 其他 / 尚未确定", "🇬🇧 优先英文资源"
        )
        assert result[0]["language"] == "en"

    def test_focus_foundational(self):
        result = app.filter_resources_for_direction(
            SAMPLE_RESOURCES, "🌐 其他 / 尚未确定", "🌍 不限语言", focus="foundational"
        )
        # Foundational resources should come first
        foundational_ids = {"r001", "r003"}
        for r in result[:2]:
            assert r["id"] in foundational_ids or r.get("focus") == "both"

    def test_focus_applied(self):
        result = app.filter_resources_for_direction(
            SAMPLE_RESOURCES, "🌐 其他 / 尚未确定", "🌍 不限语言", focus="applied"
        )
        # Applied resources first
        assert result[0]["focus"] == "applied"

    def test_max_50_resources(self):
        # Generate 60 resources
        many = [
            {"id": f"r{i:03d}", "title": f"R{i}", "url": f"https://ex.com/{i}",
             "type": "article", "topics": [], "domain": ["general"],
             "level": "beginner", "duration_hours": 1, "description": "",
             "language": "en", "free": True, "focus": "both"}
            for i in range(60)
        ]
        result = app.filter_resources_for_direction(many, "🌐 其他 / 尚未确定", "🌍 不限语言")
        assert len(result) == 50

    def test_direction_includes_general(self):
        """Resources with domain=general should be included even with specific direction."""
        result = app.filter_resources_for_direction(
            SAMPLE_RESOURCES, "📊 机器学习 / 数据科学", "🌍 不限语言"
        )
        ids = [r["id"] for r in result]
        # r003 domain=data-science (matched), r001 domain=general (included), r005 domain=general (included)
        assert "r003" in ids
        assert "r001" in ids
        assert "r005" in ids


# ─── Export Functions ─────────────────────────────────────────────────────────


class TestExportMarkdown:
    def test_contains_profile_info(self):
        md = app.export_plan_markdown(SAMPLE_PATH, SAMPLE_PROFILE, SAMPLE_RESOURCES)
        assert "学会RAG问答系统" in md
        assert "📗 会Python" in md

    def test_contains_week_headers(self):
        md = app.export_plan_markdown(SAMPLE_PATH, SAMPLE_PROFILE, SAMPLE_RESOURCES)
        assert "第 1 周" in md
        assert "第 4 周" in md

    def test_contains_resource_titles(self):
        md = app.export_plan_markdown(SAMPLE_PATH, SAMPLE_PROFILE, SAMPLE_RESOURCES)
        assert "Python Basics" in md
        assert "LangChain实战" in md

    def test_contains_checkbox_format(self):
        md = app.export_plan_markdown(SAMPLE_PATH, SAMPLE_PROFILE, SAMPLE_RESOURCES)
        assert "- [ ]" in md

    def test_missing_resource_skipped(self):
        path = {"summary": "test", "estimated_weeks": 1,
                "weeks": [{"week": 1, "goal": "g", "resources": ["nonexistent"]}]}
        md = app.export_plan_markdown(path, SAMPLE_PROFILE, SAMPLE_RESOURCES)
        assert "nonexistent" not in md


class TestExportJson:
    def test_valid_json(self):
        result = app.export_plan_json(SAMPLE_PATH, SAMPLE_PROFILE)
        data = json.loads(result)
        assert "profile" in data
        assert "path" in data

    def test_roundtrip(self):
        result = app.export_plan_json(SAMPLE_PATH, SAMPLE_PROFILE)
        data = json.loads(result)
        assert data["profile"] == SAMPLE_PROFILE
        assert data["path"] == SAMPLE_PATH

    def test_unicode_preserved(self):
        result = app.export_plan_json(SAMPLE_PATH, SAMPLE_PROFILE)
        assert "学会RAG问答系统" in result  # ensure_ascii=False


# ─── Constants ────────────────────────────────────────────────────────────────


class TestConstants:
    def test_provider_presets_have_required_keys(self):
        for name, preset in app.PROVIDER_PRESETS.items():
            assert "base_url" in preset, f"{name} missing base_url"
            assert "models" in preset, f"{name} missing models"

    def test_direction_domains_are_lists(self):
        for direction, domains in app.DIRECTION_TO_DOMAIN.items():
            assert isinstance(domains, list), f"{direction} domains should be list"

    def test_preset_profiles_have_required_fields(self):
        required = {"level", "goal", "hours_per_week", "preference", "language", "direction", "focus"}
        for name, profile in app.PRESET_PROFILES.items():
            for field in required:
                assert field in profile, f"Preset '{name}' missing field '{field}'"
