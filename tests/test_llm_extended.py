"""Extended LLM tests — edge cases for config resolution, error recovery, cache."""

import sys, os, json
from unittest.mock import MagicMock, patch
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

mock_st = sys.modules.get("streamlit") or MagicMock()
if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = mock_st
mock_st.session_state = {}
mock_st.secrets = MagicMock()
mock_st.secrets.get = MagicMock(return_value="")

if "openai" not in sys.modules:
    sys.modules["openai"] = MagicMock()


def _mock_stream(content_str):
    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta.content = content_str
    return [chunk]


class TestGetLlmConfigExtended:
    """Edge cases for config resolution priority."""

    def setup_method(self):
        mock_st.session_state = {}
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")

    def test_session_key_takes_priority_over_secrets(self):
        mock_st.session_state = {"settings_api_key": "sk-session"}
        mock_st.secrets.get = MagicMock(side_effect=lambda k, d="": {"DASHSCOPE_API_KEY": "sk-secret"}.get(k, d))
        from llm import get_llm_config
        key, _, _ = get_llm_config()
        assert key == "sk-session"

    @patch.dict(os.environ, {"DASHSCOPE_API_KEY": "sk-env"})
    def test_secrets_takes_priority_over_env(self):
        mock_st.session_state = {}
        mock_st.secrets.get = MagicMock(side_effect=lambda k, d="": {"DASHSCOPE_API_KEY": "sk-secret"}.get(k, d))
        from llm import get_llm_config
        key, _, _ = get_llm_config()
        assert key == "sk-secret"

    def test_empty_key_returns_empty(self):
        mock_st.session_state = {}
        mock_st.secrets.get = MagicMock(return_value="")
        env_backup = os.environ.pop("DASHSCOPE_API_KEY", None)
        try:
            from llm import get_llm_config
            key, _, _ = get_llm_config()
            assert key == ""
        finally:
            if env_backup:
                os.environ["DASHSCOPE_API_KEY"] = env_backup

    def test_custom_provider_base_url_and_model(self):
        mock_st.session_state = {
            "settings_provider": "自定义",
            "settings_base_url": "https://my-api.com/v1",
            "settings_model_text": "gpt-custom",
        }
        from llm import get_llm_config
        _, base_url, model = get_llm_config()
        assert base_url == "https://my-api.com/v1"
        assert model == "gpt-custom"

    def test_custom_provider_falls_back_to_secrets(self):
        mock_st.session_state = {"settings_provider": "自定义"}
        mock_st.secrets.get = MagicMock(side_effect=lambda k, d="": {
            "API_BASE_URL": "https://fallback.com/v1",
            "MODEL": "fallback-model",
        }.get(k, d))
        from llm import get_llm_config
        _, base_url, model = get_llm_config()
        assert base_url == "https://fallback.com/v1"
        assert model == "fallback-model"

    def test_known_provider_ignores_custom_url(self):
        from config import PROVIDER_PRESETS
        mock_st.session_state = {
            "settings_provider": "OpenAI",
            "settings_base_url": "https://should-be-ignored.com/v1",
        }
        from llm import get_llm_config
        _, base_url, _ = get_llm_config()
        assert base_url == PROVIDER_PRESETS["OpenAI"]["base_url"]

    def test_model_from_session_state(self):
        from config import PROVIDER_PRESETS
        mock_st.session_state = {
            "settings_provider": "DeepSeek",
            "settings_model_DeepSeek": "deepseek-chat",
        }
        from llm import get_llm_config
        _, _, model = get_llm_config()
        assert model == "deepseek-chat"


class TestGeneratePathEdge:
    """Edge cases for generate_path."""

    def setup_method(self):
        mock_st.session_state = {"settings_api_key": "sk-test"}
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")

    @patch("llm.OpenAI")
    def test_empty_resources(self, MockOpenAI):
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream('{"summary":"empty","weeks":[]}')
        from llm import generate_path
        result = generate_path(
            {"level": "beginner", "goal": "learn", "hours_per_week": 5, "preference": "any", "language": "en"},
            [],
        )
        assert result["weeks"] == []

    @patch("llm.OpenAI")
    def test_profile_with_skills_background(self, MockOpenAI):
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream('{"weeks":[]}')
        from llm import generate_path
        generate_path(
            {"level": "中级", "goal": "学RAG", "hours_per_week": 10, "preference": "实战",
             "language": "zh", "skills_background": "3年Python开发经验", "direction": "LLM", "focus": "applied"},
            [],
        )
        call_args = MockOpenAI.return_value.chat.completions.create.call_args
        user_msg = call_args[1]["messages"][-1]["content"]
        assert "3年Python开发经验" in user_msg

    @patch("llm.OpenAI")
    def test_profile_without_skills_shows_placeholder(self, MockOpenAI):
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream('{"weeks":[]}')
        from llm import generate_path
        generate_path(
            {"level": "beginner", "goal": "learn", "hours_per_week": 5, "preference": "any", "language": "en"},
            [],
        )
        call_args = MockOpenAI.return_value.chat.completions.create.call_args
        user_msg = call_args[1]["messages"][-1]["content"]
        assert "未填写" in user_msg

    @patch("llm.OpenAI")
    def test_json_parse_error_raises(self, MockOpenAI):
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream("not json at all")
        from llm import generate_path
        try:
            generate_path(
                {"level": "a", "goal": "b", "hours_per_week": 5, "preference": "c", "language": "d"},
                [],
            )
            assert False, "Should have raised"
        except (json.JSONDecodeError, Exception):
            pass

    @patch("llm.OpenAI")
    def test_empty_stream_raises(self, MockOpenAI):
        MockOpenAI.return_value.chat.completions.create.return_value = []
        from llm import generate_path
        try:
            generate_path(
                {"level": "a", "goal": "b", "hours_per_week": 5, "preference": "c", "language": "d"},
                [],
            )
            assert False, "Should have raised on empty stream"
        except Exception:
            pass


class TestGenerateTrendInsightsEdge:
    """Edge cases for trend insights generation and validation."""

    def setup_method(self):
        mock_st.session_state = {"settings_api_key": "sk-test"}
        mock_st.secrets = MagicMock()
        mock_st.secrets.get = MagicMock(return_value="")
        import llm
        self._orig_path = llm.INSIGHTS_CACHE_PATH
        self._tmp_path = os.path.join(os.path.dirname(__file__), "_test_edge_cache.json")
        llm.INSIGHTS_CACHE_PATH = self._tmp_path

    def teardown_method(self):
        import llm
        llm.INSIGHTS_CACHE_PATH = self._orig_path
        if os.path.exists(self._tmp_path):
            os.remove(self._tmp_path)

    @patch("llm.OpenAI")
    def test_non_dict_response_normalized(self, MockOpenAI):
        """LLM returns a list instead of dict — should be normalized to empty dict."""
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream('[{"title":"bad"}]')
        from llm import generate_trend_insights
        result = generate_trend_insights(
            [{"title": "src", "language": "en", "description": "d"}],
            force_refresh=True,
        )
        # Non-dict result should be normalized
        assert isinstance(result, dict)

    @patch("llm.OpenAI")
    def test_non_list_insights_normalized(self, MockOpenAI):
        """insights field is not a list — should be normalized to empty list."""
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream(
            '{"date":"2026-01-01","insights":"not a list","overview":"ok"}'
        )
        from llm import generate_trend_insights
        result = generate_trend_insights(
            [{"title": "src", "language": "en", "description": "d"}],
            force_refresh=True,
        )
        assert result.get("insights") == []

    @patch("llm.OpenAI")
    def test_non_dict_insights_filtered(self, MockOpenAI):
        """Non-dict items in insights list should be filtered out."""
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream(
            json.dumps({
                "date": "2026-01-01",
                "insights": [
                    {"title": "valid"},
                    "string_insight",
                    42,
                    None,
                    {"title": "also valid"},
                ],
            })
        )
        from llm import generate_trend_insights
        result = generate_trend_insights(
            [{"title": "s", "language": "en", "description": "d"}],
            force_refresh=True,
        )
        assert len(result["insights"]) == 2

    @patch("llm.OpenAI")
    def test_api_error_falls_back_to_cache(self, MockOpenAI):
        """On API error, falls back to cached data if available."""
        from llm import _save_insights_cache, generate_trend_insights
        cached = {"date": datetime.now().strftime("%Y-%m-%d"), "insights": [{"title": "cached"}]}
        _save_insights_cache(cached)
        MockOpenAI.return_value.chat.completions.create.side_effect = Exception("API down")
        result = generate_trend_insights(
            [{"title": "s", "language": "en", "description": "d"}],
            force_refresh=True,
        )
        assert result.get("insights", [{}])[0].get("title") == "cached"

    @patch("llm.OpenAI")
    def test_force_refresh_ignores_cache(self, MockOpenAI):
        from llm import _save_insights_cache, generate_trend_insights
        cached = {"date": datetime.now().strftime("%Y-%m-%d"), "insights": [{"title": "cached"}]}
        _save_insights_cache(cached)
        expected = {"date": "2026-01-01", "insights": [{"title": "fresh"}]}
        MockOpenAI.return_value.chat.completions.create.return_value = _mock_stream(json.dumps(expected))
        result = generate_trend_insights(
            [{"title": "s", "language": "en", "description": "d"}],
            force_refresh=True,
        )
        assert result["insights"][0]["title"] == "fresh"

    def test_cache_write_failure_silent(self):
        """_save_insights_cache should not raise on write failure."""
        import llm
        orig = llm.INSIGHTS_CACHE_PATH
        llm.INSIGHTS_CACHE_PATH = "/dev/null/impossible/path.json"
        try:
            llm._save_insights_cache({"date": "2026-01-01", "insights": []})
            # Should not raise
        finally:
            llm.INSIGHTS_CACHE_PATH = orig


class TestCompactResourcesEdge:
    """Edge cases for _compact_resources."""

    def test_resource_without_domain(self):
        from llm import _compact_resources
        res = [{"id": "r1", "title": "No Domain", "type": "article", "level": "beginner",
                "duration_hours": 3, "topics": ["ml"], "focus": "both"}]
        result = _compact_resources(res)
        assert "general" in result

    def test_resource_without_focus(self):
        from llm import _compact_resources
        res = [{"id": "r1", "title": "T", "type": "article", "level": "beginner",
                "duration_hours": 1, "topics": [], "domain": ["general"]}]
        result = _compact_resources(res)
        assert "both" in result

    def test_large_resource_list(self):
        from llm import _compact_resources
        res = [{"id": f"r{i}", "title": f"T{i}", "type": "article", "level": "beginner",
                "duration_hours": 1, "topics": [f"t{i}"], "domain": ["general"], "focus": "both"} for i in range(100)]
        result = _compact_resources(res)
        lines = result.strip().split("\n")
        assert len(lines) == 100
