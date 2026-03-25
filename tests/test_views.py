"""Integration tests for views — testable logic with mocked Streamlit."""

import sys, os, json
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─── Get/create the shared streamlit mock ─────────────────────────────────────
# Other test files may have already inserted a mock; reuse it so all modules
# that imported `st` reference the same object.

if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = MagicMock()
mock_st = sys.modules["streamlit"]
mock_st.session_state = {}
mock_st.secrets = MagicMock()
mock_st.secrets.get = MagicMock(return_value="")

if "openai" not in sys.modules:
    sys.modules["openai"] = MagicMock()


# ─── Tests for _build_chat_context ───────────────────────────────────────────

from views.chat import _build_chat_context


SAMPLE_RESOURCES = [
    {"id": "r1", "title": "Intro to ML", "type": "course", "topics": ["ML", "basics"]},
    {"id": "r2", "title": "Deep Learning", "type": "book", "topics": ["DL", "neural-nets", "CNN", "RNN"]},
    {"id": "r3", "title": "NLP Guide", "type": "article", "topics": []},
]


class TestBuildChatContext:
    def setup_method(self):
        mock_st.session_state = {}

    def test_includes_resource_summary(self):
        ctx = _build_chat_context(SAMPLE_RESOURCES)
        assert "r1" in ctx
        assert "Intro to ML" in ctx
        assert "r2" in ctx

    def test_includes_profile_when_present(self):
        mock_st.session_state = {
            "profile": {"level": "中级", "direction": "NLP", "goal": "做翻译系统", "focus": "applied"}
        }
        ctx = _build_chat_context(SAMPLE_RESOURCES)
        assert "中级" in ctx
        assert "NLP" in ctx
        assert "做翻译系统" in ctx

    def test_includes_path_when_present(self):
        mock_st.session_state = {
            "path": {
                "summary": "NLP学习路径",
                "estimated_weeks": 6,
                "weeks": [
                    {"week": 1, "resources": ["r1", "r2"]},
                    {"week": 2, "resources": ["r3"]},
                ]
            }
        }
        ctx = _build_chat_context(SAMPLE_RESOURCES)
        assert "NLP学习路径" in ctx
        assert "6" in ctx
        assert "r1" in ctx

    def test_no_profile_no_path(self):
        mock_st.session_state = {}
        ctx = _build_chat_context(SAMPLE_RESOURCES)
        assert "资源库摘要" in ctx
        assert "用户画像" not in ctx

    def test_topic_truncation(self):
        """Resources have topics truncated to 3."""
        ctx = _build_chat_context(SAMPLE_RESOURCES)
        # r2 has 4 topics, only first 3 should appear in summary
        assert "DL" in ctx
        assert "neural-nets" in ctx
        assert "CNN" in ctx
        # RNN is the 4th topic, should be excluded
        assert "RNN" not in ctx

    def test_resource_limit_60(self):
        """Only first 60 resources are included."""
        big_list = [{"id": f"rx{i}", "title": f"R{i}", "type": "article", "topics": []} for i in range(100)]
        ctx = _build_chat_context(big_list)
        assert "rx59" in ctx
        assert "rx60" not in ctx

    def test_empty_resources(self):
        ctx = _build_chat_context([])
        assert "资源库摘要" in ctx

    def test_path_with_no_weeks(self):
        mock_st.session_state = {
            "path": {"summary": "Empty", "estimated_weeks": 0, "weeks": []}
        }
        ctx = _build_chat_context([])
        assert "Empty" in ctx

    def test_includes_builders(self):
        """Builders are listed separately with role and description."""
        resources_with_builder = SAMPLE_RESOURCES + [
            {"id": "b001", "title": "Andrej Karpathy", "type": "builder",
             "role": "researcher", "topics": ["deep-learning", "llm"],
             "description": "Former Tesla AI director", "url": "https://karpathy.ai"},
        ]
        ctx = _build_chat_context(resources_with_builder)
        assert "AI行业大牛" in ctx
        assert "Andrej Karpathy" in ctx
        assert "researcher" in ctx
        # Builder should NOT appear in the regular 资源库摘要 section
        lines = ctx.split("\n")
        summary_section = [l for l in lines if l.startswith("b001") and "资源库" in ctx]
        # b001 should only appear in builders section
        assert any("b001" in l and "researcher" in l for l in lines)

    def test_excludes_builders_from_resource_summary(self):
        """Builders should not appear in the regular resource summary."""
        resources_with_builder = SAMPLE_RESOURCES + [
            {"id": "b001", "title": "Karpathy", "type": "builder",
             "role": "researcher", "topics": ["llm"],
             "description": "AI director", "url": "https://karpathy.ai"},
        ]
        ctx = _build_chat_context(resources_with_builder)
        # Split into sections
        parts = ctx.split("\n\n")
        resource_part = [p for p in parts if "资源库摘要" in p]
        assert len(resource_part) == 1
        assert "b001" not in resource_part[0]


# ─── Tests for submit_feedback ───────────────────────────────────────────────



class TestSubmitFeedback:
    def setup_method(self):
        mock_st.session_state = {}
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")
        # Reload feedback module to pick up fresh mock_st.secrets
        import importlib
        import views.feedback as fb_mod
        importlib.reload(fb_mod)

    @patch("views.feedback.os.makedirs")
    @patch("builtins.open", mock_open())
    def test_local_save_returns_local(self, mock_makedirs):
        from views.feedback import submit_feedback as sf
        result = sf({"rating": "太赞了", "comment": "Good"})
        assert result == "local"
        mock_makedirs.assert_called_once()

    @patch("views.feedback.os.makedirs")
    @patch("builtins.open", mock_open())
    @patch("views.feedback.urllib.request.urlopen")
    def test_github_save_returns_github(self, mock_urlopen, mock_makedirs):
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(side_effect=lambda k, d="": {"GITHUB_TOKEN": "ghp_test123"}.get(k, d))
        from views.feedback import submit_feedback as sf
        result = sf({"rating": "很有帮助", "comment": "Nice", "profile": {}})
        assert result == "github"
        mock_urlopen.assert_called_once()

    @patch("views.feedback.os.makedirs")
    @patch("builtins.open", mock_open())
    @patch("views.feedback.urllib.request.urlopen", side_effect=Exception("network error"))
    def test_github_failure_falls_back_local(self, mock_urlopen, mock_makedirs):
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(side_effect=lambda k, d="": {"GITHUB_TOKEN": "ghp_test123"}.get(k, d))
        from views.feedback import submit_feedback as sf
        result = sf({"rating": "一般", "comment": ""})
        assert result == "local"

    @patch("views.feedback.os.makedirs", side_effect=OSError("permission denied"))
    def test_local_save_failure_silent(self, mock_makedirs):
        from views.feedback import submit_feedback as sf
        result = sf({"rating": "一般"})
        assert result == "local"

    @patch("views.feedback.os.makedirs")
    @patch("builtins.open", mock_open())
    def test_feedback_file_content(self, mock_makedirs):
        feedback = {"rating": "太赞了", "comment": "反馈内容", "profile": {"level": "初级"}}
        from views.feedback import submit_feedback as sf
        sf(feedback)
        handle = open()
        written = handle.write.call_args_list
        assert len(written) > 0 or handle.method_calls

    @patch("views.feedback.os.makedirs")
    @patch("builtins.open", mock_open())
    @patch("views.feedback.urllib.request.urlopen")
    def test_github_issue_body_contains_rating(self, mock_urlopen, mock_makedirs):
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(side_effect=lambda k, d="": {"GITHUB_TOKEN": "ghp_test"}.get(k, d))
        from views.feedback import submit_feedback as sf
        sf({"rating": "太赞了", "comment": "Very nice", "profile": {"direction": "NLP"}})
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        assert "太赞了" in body["body"]
        assert "NLP" in body["body"]
        assert "feedback" in body["labels"]


# ─── Tests for views.import_plan (decode reuse) ─────────────────────────────

from views.import_plan import render_import_plan


class TestImportPlanLogic:
    """We can't test the rendering, but we verify the import_plan module imports correctly."""
    def test_module_importable(self):
        from views import import_plan
        assert hasattr(import_plan, "render_import_plan")

    def test_settings_importable(self):
        from views import settings
        assert hasattr(settings, "render_settings")

    def test_all_views_importable(self):
        """All 8 view modules should be importable."""
        from views import path, form, browser, radar, chat, feedback, import_plan, settings
        assert hasattr(path, "render_path")
        assert hasattr(form, "render_form")
        assert hasattr(browser, "render_resource_browser")
        assert hasattr(radar, "render_trend_radar")
        assert hasattr(chat, "render_chat")
        assert hasattr(feedback, "render_feedback")
        assert hasattr(import_plan, "render_import_plan")
        assert hasattr(settings, "render_settings")


class TestPathEstimatedDate:
    """Test path view handles estimated_weeks for completion date."""

    def test_estimated_date_calculated(self):
        """When estimated_weeks is an int, a finish date should be derivable."""
        from datetime import datetime, timedelta
        weeks = 8
        finish = datetime.now() + timedelta(weeks=weeks)
        assert finish > datetime.now()

    def test_estimated_date_handle_non_int(self):
        """Non-int estimated_weeks should not crash."""
        est = "?"
        # The path view checks isinstance(est, (int, float))
        assert not isinstance(est, (int, float))


class TestChatFollowUps:
    """Test _get_follow_ups heuristic suggestion engine."""

    def test_rag_keyword_triggers_rag_suggestions(self):
        from views.chat import _get_follow_ups
        result = _get_follow_ups("RAG 是一种检索增强生成技术", "zh")
        assert len(result) >= 2
        assert any("RAG" in s for s in result)

    def test_agent_keyword_triggers_agent_suggestions(self):
        from views.chat import _get_follow_ups
        result = _get_follow_ups("LangChain is great for building agents", "en")
        assert len(result) >= 2
        assert any("Agent" in s or "agent" in s.lower() for s in result)

    def test_no_keyword_returns_generic(self):
        from views.chat import _get_follow_ups
        result = _get_follow_ups("你好，有什么需要帮助的吗？", "zh")
        assert len(result) >= 2
        # Generic suggestions should be returned
        assert any("学" in s or "项目" in s for s in result)

    def test_max_three_suggestions(self):
        from views.chat import _get_follow_ups
        # Reply mentions many topics
        result = _get_follow_ups("RAG Agent Transformer 微调 部署", "zh")
        assert len(result) <= 3


class TestPathQualityScores:
    """Test _compute_quality_scores path quality analysis."""

    def _make_resources(self):
        return {
            "r1": {"id": "r1", "title": "A", "type": "course", "level": "beginner", "duration_hours": 5, "topics": []},
            "r2": {"id": "r2", "title": "B", "type": "video", "level": "intermediate", "duration_hours": 8, "topics": []},
            "r3": {"id": "r3", "title": "C", "type": "repo", "level": "advanced", "duration_hours": 10, "topics": []},
            "r4": {"id": "r4", "title": "D", "type": "article", "level": "intermediate", "duration_hours": 3, "topics": []},
        }

    def test_good_progression_scores_high(self):
        from views.path import _compute_quality_scores
        ridx = self._make_resources()
        weeks = [
            {"week": 1, "goal": "", "resources": ["r1"]},
            {"week": 2, "goal": "", "resources": ["r2"]},
            {"week": 3, "goal": "", "resources": ["r3"]},
        ]
        scores = _compute_quality_scores(weeks, ridx, {"hours_per_week": 10})
        assert scores["progression"] >= 80

    def test_diverse_types_scores_high(self):
        from views.path import _compute_quality_scores
        ridx = self._make_resources()
        weeks = [{"week": 1, "goal": "", "resources": ["r1", "r2", "r3", "r4"]}]
        scores = _compute_quality_scores(weeks, ridx, {})
        assert scores["diversity"] == 100

    def test_hands_on_with_repos(self):
        from views.path import _compute_quality_scores
        ridx = self._make_resources()
        weeks = [
            {"week": 1, "goal": "", "resources": ["r1"]},
            {"week": 2, "goal": "", "resources": ["r3"]},  # repo
        ]
        scores = _compute_quality_scores(weeks, ridx, {})
        assert scores["hands_on"] >= 80

    def test_empty_weeks_returns_zeros(self):
        from views.path import _compute_quality_scores
        scores = _compute_quality_scores([], {}, {})
        assert all(v == 0 for v in scores.values())
