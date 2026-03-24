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
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock()]
        mock_resp.choices[0].message.content = json.dumps(expected)
        MockOpenAI.return_value.chat.completions.create.return_value = mock_resp

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
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock()]
        mock_resp.choices[0].message.content = '{"weeks":[]}'
        MockOpenAI.return_value.chat.completions.create.return_value = mock_resp

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
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock()]
        mock_resp.choices[0].message.content = '{"weeks":[]}'
        MockOpenAI.return_value.chat.completions.create.return_value = mock_resp

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
