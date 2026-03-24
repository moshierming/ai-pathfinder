"""Tests for llm.py — mocked Streamlit and OpenAI client."""

import sys, os, json
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ─── Mock Streamlit before importing llm ──────────────────────────────────────

mock_st = MagicMock()
mock_st.session_state = {}
mock_st.secrets = {}
sys.modules.setdefault("streamlit", mock_st)

from config import PROVIDER_PRESETS


class TestGetLlmConfig:
    """Test get_llm_config() with various session_state / secrets / env combos."""

    def setup_method(self):
        mock_st.session_state = {}
        mock_st.secrets = {}

    def test_api_key_from_session_state(self):
        mock_st.session_state = {"settings_api_key": "sk-session"}
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")
        from llm import get_llm_config
        key, _, _ = get_llm_config()
        assert key == "sk-session"

    def test_api_key_from_secrets(self):
        mock_st.session_state = {}
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(side_effect=lambda k, d="": {"DASHSCOPE_API_KEY": "sk-secret"}.get(k, d))
        from llm import get_llm_config
        key, _, _ = get_llm_config()
        assert key == "sk-secret"

    @patch.dict(os.environ, {"DASHSCOPE_API_KEY": "sk-env"})
    def test_api_key_from_env(self):
        mock_st.session_state = {}
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")
        from llm import get_llm_config
        key, _, _ = get_llm_config()
        assert key == "sk-env"

    def test_default_provider(self):
        mock_st.session_state = {}
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")
        from llm import get_llm_config
        _, base_url, model = get_llm_config()
        preset = PROVIDER_PRESETS["DashScope (阿里云百炼)"]
        assert base_url == preset["base_url"]
        assert model == preset["models"][0]

    def test_custom_provider(self):
        mock_st.session_state = {
            "settings_provider": "自定义",
            "settings_base_url": "https://custom.api/v1",
            "settings_model_text": "my-model",
        }
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")
        from llm import get_llm_config
        _, base_url, model = get_llm_config()
        assert base_url == "https://custom.api/v1"
        assert model == "my-model"

    def test_known_provider_uses_preset_url(self):
        for name, preset in PROVIDER_PRESETS.items():
            if name == "自定义":
                continue
            mock_st.session_state = {"settings_provider": name}
            mock_st.secrets = MagicMock()
            mock_st.secrets.get = MagicMock(return_value="")
            from llm import get_llm_config
            _, base_url, model = get_llm_config()
            assert base_url == preset["base_url"], f"Provider {name} base_url mismatch"
            assert model in preset["models"], f"Provider {name} model {model} not in presets"


def _mock_stream(content_str):
    """Create a mock streaming response from a content string."""
    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta.content = content_str
    return [chunk]


class TestGeneratePath:
    """Test generate_path() with mocked OpenAI client."""

    def setup_method(self):
        mock_st.session_state = {"settings_api_key": "sk-test"}
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")

    def test_raises_without_api_key(self):
        mock_st.session_state = {}
        from llm import generate_path
        try:
            generate_path({"level": "a", "goal": "b", "hours_per_week": 5, "preference": "c", "language": "d"}, [])
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "DASHSCOPE_API_KEY" in str(e)

    @patch("llm.OpenAI")
    def test_returns_parsed_json(self, MockOpenAI):
        expected = {"summary": "Test Path", "estimated_weeks": 4, "weeks": []}
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream(json.dumps(expected))

        from llm import generate_path
        result = generate_path(
            {"level": "beginner", "goal": "learn AI", "hours_per_week": 10,
             "preference": "balanced", "language": "en", "direction": "LLM",
             "focus": "both"},
            [{"id": "r1", "title": "T", "level": "beginner", "topics": ["ML"],
              "domain": ["general"], "duration_hours": 5, "type": "article", "focus": "both"}],
        )
        assert result == expected
        MockOpenAI.assert_called_once()

    @patch("llm.OpenAI")
    def test_passes_correct_model(self, MockOpenAI):
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream('{"weeks":[]}')

        mock_st.session_state = {
            "settings_api_key": "sk-test",
            "settings_provider": "DashScope (阿里云百炼)",
        }

        from llm import generate_path
        generate_path({"level": "a", "goal": "b", "hours_per_week": 5, "preference": "c", "language": "d"}, [])

        call_args = MockOpenAI.return_value.chat.completions.create.call_args
        assert call_args[1]["model"] == PROVIDER_PRESETS["DashScope (阿里云百炼)"]["models"][0]

    @patch("llm.OpenAI")
    def test_user_message_contains_profile(self, MockOpenAI):
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream('{"weeks":[]}')

        from llm import generate_path
        generate_path(
            {"level": "高级", "goal": "学深度学习", "hours_per_week": 15,
             "preference": "视频", "language": "中文", "focus": "foundational"},
            [],
        )
        call_args = MockOpenAI.return_value.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        user_msg = messages[-1]["content"]
        assert "高级" in user_msg
        assert "学深度学习" in user_msg
        assert "15" in user_msg


class TestCompactResources:
    """Test _compact_resources() formatting."""

    def test_single_resource(self):
        from llm import _compact_resources
        res = [{"id": "r001", "title": "ML课程", "type": "course", "level": "beginner",
                "duration_hours": 10, "topics": ["ml", "python", "data"], "domain": ["data-science"],
                "focus": "both"}]
        result = _compact_resources(res)
        assert "r001" in result
        assert "ML课程" in result
        assert "course" in result
        assert "10h" in result
        # topics truncated to first 3
        assert "ml,python,data" in result

    def test_empty_list(self):
        from llm import _compact_resources
        assert _compact_resources([]) == ""

    def test_topics_truncated(self):
        from llm import _compact_resources
        res = [{"id": "r1", "title": "T", "type": "article", "level": "beginner",
                "duration_hours": 5, "topics": ["alpha", "beta", "gamma", "delta", "epsilon"],
                "domain": ["general"], "focus": "applied"}]
        result = _compact_resources(res)
        assert "alpha,beta,gamma" in result
        assert "delta" not in result

    def test_missing_optional_fields(self):
        from llm import _compact_resources
        res = [{"id": "r1", "title": "T", "type": "article", "level": "beginner",
                "duration_hours": 5, "topics": [], "focus": "both"}]
        result = _compact_resources(res)
        assert "r1" in result
        assert "general" in result  # default domain

    def test_multiple_resources(self):
        from llm import _compact_resources
        res = [
            {"id": "r1", "title": "A", "type": "course", "level": "beginner",
             "duration_hours": 5, "topics": ["ml"], "domain": ["general"], "focus": "both"},
            {"id": "r2", "title": "B", "type": "video", "level": "advanced",
             "duration_hours": 3, "topics": ["llm"], "domain": ["llm-app"], "focus": "applied"},
        ]
        result = _compact_resources(res)
        lines = result.split("\n")
        assert len(lines) == 2
        assert lines[0].startswith("r1|")
        assert lines[1].startswith("r2|")


class TestInsightsCache:
    """Test _load_insights_cache / _save_insights_cache."""

    def setup_method(self):
        import llm
        self._orig_path = llm.INSIGHTS_CACHE_PATH
        self._tmp_path = os.path.join(os.path.dirname(__file__), "_test_cache.json")
        llm.INSIGHTS_CACHE_PATH = self._tmp_path

    def teardown_method(self):
        import llm
        llm.INSIGHTS_CACHE_PATH = self._orig_path
        if os.path.exists(self._tmp_path):
            os.remove(self._tmp_path)

    def test_no_cache_file(self):
        from llm import _load_insights_cache
        assert _load_insights_cache() is None

    def test_save_and_load(self):
        from llm import _save_insights_cache, _load_insights_cache
        from datetime import datetime
        data = {"date": datetime.now().strftime("%Y-%m-%d"), "insights": [{"title": "test"}]}
        _save_insights_cache(data)
        loaded = _load_insights_cache()
        assert loaded is not None
        assert loaded["insights"][0]["title"] == "test"

    def test_stale_cache_returns_none(self):
        from llm import _save_insights_cache, _load_insights_cache
        data = {"date": "2020-01-01", "insights": []}
        _save_insights_cache(data)
        assert _load_insights_cache() is None

    def test_corrupted_cache_returns_none(self):
        from llm import _load_insights_cache
        with open(self._tmp_path, "w") as f:
            f.write("{invalid json")
        assert _load_insights_cache() is None


class TestGenerateTrendInsights:
    """Test generate_trend_insights() with mocking."""

    def setup_method(self):
        mock_st.session_state = {"settings_api_key": "sk-test"}
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")
        import llm
        self._orig_path = llm.INSIGHTS_CACHE_PATH
        self._tmp_path = os.path.join(os.path.dirname(__file__), "_test_insights.json")
        llm.INSIGHTS_CACHE_PATH = self._tmp_path

    def teardown_method(self):
        import llm
        llm.INSIGHTS_CACHE_PATH = self._orig_path
        if os.path.exists(self._tmp_path):
            os.remove(self._tmp_path)

    def test_no_api_key_returns_empty(self):
        mock_st.session_state = {}
        from llm import generate_trend_insights
        result = generate_trend_insights([{"title": "t", "description": "d"}])
        assert result == {}

    def test_empty_channels(self):
        mock_st.session_state = {}
        from llm import generate_trend_insights
        result = generate_trend_insights([])
        assert result == {}

    @patch("llm.OpenAI")
    def test_returns_insights_json(self, MockOpenAI):
        from llm import generate_trend_insights
        expected = {"date": "2026-03-24", "overview": "test", "insights": [{"title": "a"}]}
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream(json.dumps(expected))
        result = generate_trend_insights(
            [{"title": "Source1", "language": "zh", "description": "desc"}],
            force_refresh=True,
        )
        assert "insights" in result
        assert len(result["insights"]) == 1

    @patch("llm.OpenAI")
    def test_uses_cache_when_fresh(self, MockOpenAI):
        from llm import _save_insights_cache, generate_trend_insights
        from datetime import datetime
        cached = {"date": datetime.now().strftime("%Y-%m-%d"), "insights": [{"title": "cached"}]}
        _save_insights_cache(cached)
        result = generate_trend_insights([{"title": "s", "language": "en", "description": "d"}])
        assert result["insights"][0]["title"] == "cached"
        MockOpenAI.return_value.chat.completions.create.assert_not_called()

    @patch("llm.OpenAI")
    def test_api_failure_returns_empty(self, MockOpenAI):
        from llm import generate_trend_insights
        MockOpenAI.return_value.chat.completions.create.side_effect = Exception("API down")
        result = generate_trend_insights(
            [{"title": "s", "language": "en", "description": "d"}],
            force_refresh=True,
        )
        # No cache at all => returns empty dict
        assert result == {}
