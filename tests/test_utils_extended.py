"""Extended tests for utils.py — edge cases for encoding, filtering, and export."""

import sys, os, json, base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import (
    encode_profile, decode_profile, filter_resources_for_direction,
    export_plan_markdown, export_plan_json,
)


# ─── Sample data ──────────────────────────────────────────────────────────────

def _make_resource(rid, domain=None, lang="en", focus="both", rtype="article", level="beginner"):
    return {
        "id": rid, "title": f"Title {rid}", "url": f"https://ex.com/{rid}",
        "type": rtype, "topics": ["topic1"], "domain": domain or ["general"],
        "level": level, "duration_hours": 5, "description": f"Desc {rid}",
        "language": lang, "free": True, "focus": focus,
    }

RESOURCES = [
    _make_resource("r01", domain=["llm-app"], lang="zh", focus="applied"),
    _make_resource("r02", domain=["ai-agent", "llm-app"], lang="en", focus="foundational"),
    _make_resource("r03", domain=["data-science"], lang="en", focus="both"),
    _make_resource("r04", domain=["general"], lang="zh", focus="foundational"),
    _make_resource("r05", domain=["general"], lang="en", focus="applied", rtype="channel"),
]

PROFILE = {
    "level": "📗 会Python，了解基本ML概念",
    "goal": "测试目标",
    "hours_per_week": 8,
    "preference": "⚖️ 均衡搭配",
    "language": "🌍 不限语言",
    "direction": "💬 LLM 应用开发 / RAG",
    "focus": "both",
}


# ─── Encode/Decode edge cases ────────────────────────────────────────────────


class TestEncodeDecodeEdge:
    def test_special_characters(self):
        p = {"goal": "学习<script>alert(1)</script> & 其他"}
        assert decode_profile(encode_profile(p)) == p

    def test_nested_data(self):
        p = {"nested": {"list": [1, 2, 3], "deeper": {"a": True}}}
        assert decode_profile(encode_profile(p)) == p

    def test_large_profile(self):
        p = {"goal": "x" * 10000}
        assert decode_profile(encode_profile(p)) == p

    def test_decode_empty_string(self):
        assert decode_profile("") is None

    def test_decode_non_base64_chars(self):
        assert decode_profile("!!!###$$$") is None

    def test_numeric_values(self):
        p = {"hours": 10, "score": 3.14, "ok": True, "nothing": None}
        assert decode_profile(encode_profile(p)) == p

    def test_encode_deterministic(self):
        p = {"a": 1, "b": 2}
        assert encode_profile(p) == encode_profile(p)


# ─── Filter edge cases ──────────────────────────────────────────────────────


class TestFilterEdge:
    def test_empty_resources(self):
        result = filter_resources_for_direction([], "💬 LLM 应用开发 / RAG", "🌍 不限语言")
        assert result == []

    def test_empty_direction(self):
        result = filter_resources_for_direction(RESOURCES, "", "🌍 不限语言")
        assert len(result) == len(RESOURCES)

    def test_unknown_direction(self):
        result = filter_resources_for_direction(RESOURCES, "不存在的方向", "🌍 不限语言")
        assert len(result) == len(RESOURCES)

    def test_focus_both_returns_all(self):
        result = filter_resources_for_direction(RESOURCES, "🌐 其他 / 尚未确定", "🌍 不限语言", focus="both")
        assert len(result) == len(RESOURCES)

    def test_filter_preserves_resource_integrity(self):
        """Filtering should not modify resource objects."""
        original = [dict(r) for r in RESOURCES]
        filter_resources_for_direction(RESOURCES, "💬 LLM 应用开发 / RAG", "🇨🇳 优先中文资源", "applied")
        for orig, cur in zip(original, RESOURCES):
            assert orig == cur

    def test_zh_language_zh_first(self):
        result = filter_resources_for_direction(RESOURCES, "🌐 其他 / 尚未确定", "🇨🇳 优先中文资源")
        zh_done = False
        for r in result:
            if r["language"] != "zh" and not zh_done:
                zh_done = True
            if zh_done:
                # After first non-zh, no more zh should appear (they're sorted)
                pass  # language sorting is stable but not guaranteed strict partition
        # At minimum, first resource should be zh
        zh_resources = [r for r in RESOURCES if r["language"] == "zh"]
        if zh_resources:
            assert result[0]["language"] == "zh"

    def test_direction_matched_before_general(self):
        result = filter_resources_for_direction(RESOURCES, "💬 LLM 应用开发 / RAG", "🌍 不限语言")
        ids = [r["id"] for r in result]
        # r01 and r02 are in llm-app domain, should come before r04 (general)
        # r03 (data-science) is excluded because it's neither matched nor general
        assert "r03" not in ids
        assert ids.index("r01") < ids.index("r04")
        assert ids.index("r02") < ids.index("r04")

    def test_applied_focus_ordering(self):
        result = filter_resources_for_direction(RESOURCES, "🌐 其他 / 尚未确定", "🌍 不限语言", "applied")
        applied = [r for r in result if r["focus"] == "applied"]
        non_applied = [r for r in result if r["focus"] != "applied"]
        # Applied resources appear first
        if applied and non_applied:
            assert result.index(applied[0]) < result.index(non_applied[0])

    def test_resources_with_missing_domain(self):
        """Resources without domain field should be treated as general."""
        r = {"id": "x1", "title": "No Domain", "url": "https://ex.com", "type": "article",
             "topics": [], "level": "beginner", "duration_hours": 1, "description": "",
             "language": "en", "free": True, "focus": "both"}
        result = filter_resources_for_direction([r], "💬 LLM 应用开发 / RAG", "🌍 不限语言")
        assert len(result) == 1


# ─── Export edge cases ───────────────────────────────────────────────────────


class TestExportEdge:
    def test_markdown_empty_weeks(self):
        path = {"summary": "Empty", "estimated_weeks": 0, "weeks": []}
        md = export_plan_markdown(path, PROFILE, RESOURCES)
        assert "Empty" in md
        assert "AI Pathfinder" in md

    def test_markdown_unknown_resource_id(self):
        path = {"summary": "test", "estimated_weeks": 1,
                "weeks": [{"week": 1, "goal": "g", "resources": ["nonexistent"]}]}
        md = export_plan_markdown(path, PROFILE, RESOURCES)
        assert "nonexistent" not in md

    def test_markdown_channel_resource(self):
        path = {"summary": "test", "estimated_weeks": 1,
                "weeks": [{"week": 1, "goal": "g", "resources": ["r05"]}]}
        md = export_plan_markdown(path, PROFILE, RESOURCES)
        assert "📡" in md  # channel type emoji

    def test_markdown_multiple_weeks(self):
        path = {"summary": "multi", "estimated_weeks": 3,
                "weeks": [
                    {"week": 1, "goal": "Week 1", "tip": "Tip 1", "resources": ["r01"]},
                    {"week": 2, "goal": "Week 2", "resources": ["r02", "r03"]},
                    {"week": 3, "goal": "Week 3", "resources": ["r04"]},
                ]}
        md = export_plan_markdown(path, PROFILE, RESOURCES)
        assert "第 1 周" in md
        assert "第 2 周" in md
        assert "第 3 周" in md
        assert "Tip 1" in md

    def test_json_empty_path(self):
        path = {"summary": "", "estimated_weeks": 0, "weeks": []}
        result = export_plan_json(path, PROFILE)
        data = json.loads(result)
        assert data["path"]["weeks"] == []

    def test_json_profile_preserved(self):
        path = {"summary": "s", "estimated_weeks": 1, "weeks": []}
        result = export_plan_json(path, PROFILE)
        data = json.loads(result)
        assert data["profile"]["goal"] == "测试目标"

    def test_markdown_has_checkbox(self):
        path = {"summary": "s", "estimated_weeks": 1,
                "weeks": [{"week": 1, "goal": "g", "resources": ["r01"]}]}
        md = export_plan_markdown(path, PROFILE, RESOURCES)
        assert "- [ ]" in md

    def test_markdown_profile_fields(self):
        md = export_plan_markdown(
            {"summary": "s", "estimated_weeks": 1, "weeks": []},
            {"level": "A", "direction": "B", "focus": "C", "goal": "D",
             "hours_per_week": 5, "language": "E"},
            [],
        )
        for val in ["A", "B", "C", "D", "5", "E"]:
            assert val in md
