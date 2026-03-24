"""Tests for config.py — constants integrity and consistency."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import (
    PROVIDER_PRESETS, LEVEL_EMOJI, TYPE_EMOJI, FOCUS_EMOJI, LEVEL_ORDER,
    LEVELS, PREFERENCES, LANGUAGES, FOCUS_OPTIONS, FOCUS_MAP,
    DIRECTIONS, DIRECTION_TO_DOMAIN, PRESET_PROFILES, PRESET_DESCRIPTIONS,
    SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT,
)


class TestProviderPresets:
    def test_has_required_keys(self):
        for name, preset in PROVIDER_PRESETS.items():
            assert "base_url" in preset, f"{name} missing base_url"
            assert "models" in preset, f"{name} missing models"
            assert isinstance(preset["models"], list)

    def test_preset_urls_are_strings(self):
        for name, preset in PROVIDER_PRESETS.items():
            assert isinstance(preset["base_url"], str)

    def test_non_custom_have_models(self):
        for name, preset in PROVIDER_PRESETS.items():
            if name != "自定义":
                assert len(preset["models"]) > 0, f"{name} should have at least one model"

    def test_custom_preset_empty(self):
        assert PROVIDER_PRESETS["自定义"]["base_url"] == ""
        assert PROVIDER_PRESETS["自定义"]["models"] == []

    def test_known_providers_exist(self):
        names = list(PROVIDER_PRESETS.keys())
        assert "DashScope (阿里云百炼)" in names
        assert "OpenAI" in names
        assert "DeepSeek" in names


class TestEmojiMaps:
    def test_level_emoji_covers_standard_levels(self):
        for lvl in ["beginner", "intermediate", "advanced"]:
            assert lvl in LEVEL_EMOJI

    def test_type_emoji_covers_standard_types(self):
        for typ in ["course", "video", "article", "repo", "book", "channel"]:
            assert typ in TYPE_EMOJI

    def test_focus_emoji_covers_all(self):
        for foc in ["foundational", "applied", "both"]:
            assert foc in FOCUS_EMOJI

    def test_level_order_values_ascending(self):
        keys = ["beginner", "beginner-to-intermediate", "intermediate",
                "intermediate-to-advanced", "advanced"]
        values = [LEVEL_ORDER[k] for k in keys]
        assert values == sorted(values)


class TestFormOptions:
    def test_levels_not_empty(self):
        assert len(LEVELS) >= 3

    def test_preferences_not_empty(self):
        assert len(PREFERENCES) >= 3

    def test_languages_not_empty(self):
        assert len(LANGUAGES) >= 2

    def test_focus_options_not_empty(self):
        assert len(FOCUS_OPTIONS) == 3

    def test_focus_map_covers_all_options(self):
        for opt in FOCUS_OPTIONS:
            assert opt in FOCUS_MAP, f"FOCUS_MAP missing option: {opt}"

    def test_focus_map_values_valid(self):
        valid = {"both", "foundational", "applied"}
        for opt, val in FOCUS_MAP.items():
            assert val in valid, f"FOCUS_MAP['{opt}'] = '{val}' not in {valid}"


class TestDirections:
    def test_directions_not_empty(self):
        assert len(DIRECTIONS) >= 5

    def test_all_directions_in_domain_map(self):
        for d in DIRECTIONS:
            assert d in DIRECTION_TO_DOMAIN, f"Direction '{d}' not in DIRECTION_TO_DOMAIN"

    def test_domains_are_lists_of_strings(self):
        for d, domains in DIRECTION_TO_DOMAIN.items():
            assert isinstance(domains, list)
            for val in domains:
                assert isinstance(val, str)


class TestPresetProfiles:
    def test_has_required_fields(self):
        required = {"level", "goal", "hours_per_week", "preference", "language", "direction", "focus"}
        for name, profile in PRESET_PROFILES.items():
            for field in required:
                assert field in profile, f"Preset '{name}' missing field '{field}'"

    def test_levels_are_valid(self):
        for name, profile in PRESET_PROFILES.items():
            assert profile["level"] in LEVELS, f"Preset '{name}' has invalid level"

    def test_directions_are_valid(self):
        for name, profile in PRESET_PROFILES.items():
            assert profile["direction"] in DIRECTIONS, f"Preset '{name}' has invalid direction"

    def test_descriptions_match_profiles(self):
        for name in PRESET_PROFILES:
            assert name in PRESET_DESCRIPTIONS, f"No description for preset '{name}'"

    def test_hours_positive(self):
        for name, profile in PRESET_PROFILES.items():
            assert profile["hours_per_week"] > 0


class TestSystemPrompts:
    def test_system_prompt_not_empty(self):
        assert len(SYSTEM_PROMPT) > 100

    def test_system_prompt_mentions_json(self):
        assert "JSON" in SYSTEM_PROMPT or "json" in SYSTEM_PROMPT

    def test_chat_prompt_not_empty(self):
        assert len(CHAT_SYSTEM_PROMPT) > 50

    def test_chat_prompt_has_rules(self):
        assert "规则" in CHAT_SYSTEM_PROMPT or "Rules" in CHAT_SYSTEM_PROMPT
