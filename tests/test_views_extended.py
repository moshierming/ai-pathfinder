"""Extended views tests — render calls don't crash + deeper logic tests."""

import sys, os, json
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

mock_st = sys.modules.get("streamlit") or MagicMock()
if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = mock_st


class _AttrDict(dict):
    """Dict that supports attribute access (like st.session_state)."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
    def __setattr__(self, name, value):
        self[name] = value
    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)


mock_st.session_state = _AttrDict()
mock_st.secrets = MagicMock()
mock_st.secrets.get = MagicMock(return_value="")
mock_st.cache_data = lambda **kw: (lambda fn: fn)

if "openai" not in sys.modules:
    sys.modules["openai"] = MagicMock()


SAMPLE_RESOURCES = [
    {"id": "r01", "title": "Python入门", "url": "https://ex.com/py",
     "type": "course", "topics": ["python"], "domain": ["general"],
     "level": "beginner", "duration_hours": 10, "description": "基础课程",
     "language": "zh", "free": True, "focus": "foundational"},
    {"id": "r02", "title": "LangChain实战", "url": "https://ex.com/lc",
     "type": "repo", "topics": ["langchain", "llm"], "domain": ["llm-app"],
     "level": "intermediate", "duration_hours": 15, "description": "动手做",
     "language": "en", "free": True, "focus": "applied"},
    {"id": "r03", "title": "AI Newsletter", "url": "https://ex.com/news",
     "type": "channel", "topics": ["ai"], "domain": ["general"],
     "level": "beginner", "duration_hours": 1, "description": "每周AI新闻",
     "language": "en", "free": True, "focus": "both"},
    {"id": "b01", "title": "Test Builder", "url": "https://x.com/test",
     "type": "builder", "topics": ["agent", "llm"], "domain": ["ai-agent", "llm-app"],
     "level": "intermediate", "description": "测试大牛",
     "language": "en", "role": "founder",
     "links": {"x": "https://x.com/test", "github": "https://github.com/test"}},
]

SAMPLE_PATH = {
    "summary": "从零到LLM实战",
    "estimated_weeks": 3,
    "weeks": [
        {"week": 1, "goal": "Python基础", "tip": "多练习", "resources": ["r01"]},
        {"week": 2, "goal": "LLM开发", "resources": ["r02"]},
        {"week": 3, "goal": "持续学习", "resources": ["r03"]},
    ],
}


class TestPathRenderSmoke:
    """Verify render_path doesn't crash with various inputs."""

    def setup_method(self):
        mock_st.session_state = _AttrDict()
        mock_st.reset_mock()
        # st.columns needs to return iterable of mocks
        mock_st.columns = MagicMock(side_effect=lambda n, **kw: [MagicMock() for _ in range(n if isinstance(n, int) else len(n))])
        mock_st.tabs = MagicMock(side_effect=lambda labels: [MagicMock() for _ in labels])

    def test_render_path_basic(self):
        from views.path import render_path
        render_path(SAMPLE_PATH, SAMPLE_RESOURCES)
        # Should have called st.markdown, st.expander, etc.
        assert mock_st.markdown.called or mock_st.divider.called

    def test_render_path_empty_weeks(self):
        from views.path import render_path
        render_path({"summary": "Empty", "estimated_weeks": 0, "weeks": []}, SAMPLE_RESOURCES)

    def test_render_path_missing_resource(self):
        """Weeks referencing non-existent resource IDs should not crash."""
        from views.path import render_path
        path = {
            "summary": "test",
            "estimated_weeks": 1,
            "weeks": [{"week": 1, "goal": "g", "resources": ["nonexistent_id"]}],
        }
        render_path(path, SAMPLE_RESOURCES)

    def test_render_path_analytics_basic(self):
        from views.path import render_path_analytics
        render_path_analytics(SAMPLE_PATH, SAMPLE_RESOURCES)

    def test_render_path_analytics_empty(self):
        from views.path import render_path_analytics
        # No weeks → should return early
        render_path_analytics({"weeks": []}, SAMPLE_RESOURCES)

    def test_render_path_analytics_no_matching_resources(self):
        from views.path import render_path_analytics
        path = {"weeks": [{"week": 1, "goal": "g", "resources": ["xxx"]}]}
        render_path_analytics(path, SAMPLE_RESOURCES)


class TestBrowserRenderSmoke:
    def setup_method(self):
        mock_st.session_state = _AttrDict()
        mock_st.reset_mock()
        mock_st.text_input = MagicMock(return_value="")
        mock_st.multiselect = MagicMock(return_value=[])

    def test_render_browser_basic(self):
        from views.browser import render_resource_browser
        render_resource_browser(SAMPLE_RESOURCES)

    def test_render_browser_empty(self):
        from views.browser import render_resource_browser
        render_resource_browser([])


class TestRadarRenderSmoke:
    def setup_method(self):
        mock_st.session_state = _AttrDict()
        mock_st.reset_mock()

    @patch("views.radar.generate_trend_insights", return_value={})
    def test_render_radar_basic(self, mock_gen):
        from views.radar import render_trend_radar
        render_trend_radar(SAMPLE_RESOURCES)

    @patch("views.radar.generate_trend_insights", return_value={
        "overview": "AI领域快速发展",
        "insights": [
            {"title": "GPT-5来了", "summary": "下一代模型", "action": "关注OpenAI", "tags": ["LLM"]},
        ],
        "date": "2026-01-01",
    })
    def test_render_insights_with_data(self, mock_gen):
        from views.radar import _render_insights_section
        channels = [r for r in SAMPLE_RESOURCES if r["type"] == "channel"]
        _render_insights_section(channels, "zh")

    @patch("views.radar.generate_trend_insights", return_value={
        "insights": [
            {"title": "Valid", "summary": "s", "action": "a", "tags": ["LLM"]},
            "not_a_dict",  # should be skipped
            {"title": "Also valid", "summary": "s2", "action": "a2", "tags": "not_a_list"},
        ],
    })
    def test_render_insights_with_bad_data(self, mock_gen):
        """Non-dict insights and non-list tags should not crash."""
        from views.radar import _render_insights_section
        _render_insights_section([{"title": "c", "language": "en", "description": "d"}], "zh")

    @patch("views.radar.generate_trend_insights", return_value={})
    def test_render_radar_with_profile_direction(self, mock_gen):
        """Radar should pass direction from profile to insights."""
        mock_st.session_state = _AttrDict({
            "profile": {"direction": "🤖 AI Agent / 多智能体系统"},
        })
        from views.radar import render_trend_radar
        render_trend_radar(SAMPLE_RESOURCES)
        call_args = mock_gen.call_args
        assert call_args[1].get("direction") == "🤖 AI Agent / 多智能体系统"

    def test_is_relevant_helper(self):
        from views.radar import _is_relevant
        builder = {"domain": ["ai-agent", "llm-app"]}
        assert _is_relevant(builder, ["ai-agent"]) is True
        assert _is_relevant(builder, ["data-science"]) is False
        assert _is_relevant(builder, []) is False

    @patch("views.radar.generate_trend_insights", return_value={})
    def test_render_radar_shows_builders(self, mock_gen):
        """Radar should not crash when builders are present."""
        from views.radar import render_trend_radar
        render_trend_radar(SAMPLE_RESOURCES)

    def test_render_builder_card_no_crash(self):
        from views.radar import _render_builder_card
        _render_builder_card(SAMPLE_RESOURCES[-1], "zh")


class TestFormRenderSmoke:
    def setup_method(self):
        mock_st.session_state = _AttrDict()
        mock_st.reset_mock()
        mock_st.form_submit_button = MagicMock(return_value=False)

    def test_render_form_basic(self):
        from views.form import render_form
        submitted, profile = render_form()
        assert isinstance(submitted, MagicMock) or submitted is False
        assert isinstance(profile, dict)


class TestSettingsRenderSmoke:
    def setup_method(self):
        mock_st.session_state = _AttrDict()
        mock_st.reset_mock()
        # selectbox in settings returns the first option by default
        mock_st.selectbox = MagicMock(side_effect=lambda label, options, **kw: options[0] if options else "")
        mock_st.text_input = MagicMock(return_value="")

    def test_render_settings_basic(self):
        from views.settings import render_settings
        render_settings()


class TestImportPlanRenderSmoke:
    def setup_method(self):
        mock_st.session_state = _AttrDict()
        mock_st.reset_mock()

    def test_render_import_basic(self):
        from views.import_plan import render_import_plan
        render_import_plan(SAMPLE_RESOURCES)


class TestChatRenderSmoke:
    def setup_method(self):
        mock_st.session_state = _AttrDict()
        mock_st.reset_mock()

    def test_render_chat_basic(self):
        from views.chat import render_chat
        render_chat(SAMPLE_RESOURCES)


class TestFeedbackExtended:
    """Additional feedback tests."""

    def setup_method(self):
        mock_st.session_state = _AttrDict()
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")

    def test_render_feedback_no_crash(self):
        from views.feedback import render_feedback
        render_feedback()

    @patch("views.feedback.os.makedirs")
    @patch("builtins.open", MagicMock())
    def test_feedback_empty_profile(self, mock_makedirs):
        from views.feedback import submit_feedback
        result = submit_feedback({"rating": "一般", "comment": ""})
        assert result == "local"

    @patch("views.feedback.os.makedirs")
    @patch("builtins.open", MagicMock())
    def test_feedback_minimal_fields(self, mock_makedirs):
        from views.feedback import submit_feedback
        result = submit_feedback({"rating": "太赞了"})
        assert result == "local"


class TestProgressRenderSmoke:
    """Progress render logic tests."""

    def setup_method(self):
        mock_st.session_state = _AttrDict()
        mock_st.reset_mock()

    def test_render_progress_save_no_crash(self):
        from views.progress import render_progress_save
        render_progress_save()

    def test_render_progress_restore_no_crash(self):
        from views.progress import render_progress_restore
        render_progress_restore()
