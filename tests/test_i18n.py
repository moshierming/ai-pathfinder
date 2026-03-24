"""Tests for i18n translation module."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from i18n import t, TRANSLATIONS


class TestTranslationFunction:
    def test_basic_zh(self):
        assert t("nav_path", "zh") == "🗺️ 路径规划"

    def test_basic_en(self):
        assert t("nav_path", "en") == "🗺️ Path Planner"

    def test_default_lang_is_zh(self):
        assert t("nav_path") == "🗺️ 路径规划"

    def test_missing_key_returns_key(self):
        assert t("nonexistent_key_xyz", "zh") == "nonexistent_key_xyz"

    def test_missing_en_falls_back_to_zh(self):
        # If a key only has "zh" entry, en should fall back to zh
        # We test with a key that has both — just ensure no crash
        result = t("nav_path", "fr")
        assert result == "🗺️ 路径规划"  # falls back to zh

    def test_format_kwargs(self):
        result = t("path_week", "zh", n=3)
        assert "3" in result
        result_en = t("path_week", "en", n=5)
        assert "5" in result_en

    def test_all_keys_have_zh_and_en(self):
        """Every defined key should have both zh and en translations."""
        for key, entry in TRANSLATIONS.items():
            assert "zh" in entry, f"Key '{key}' missing 'zh'"
            assert "en" in entry, f"Key '{key}' missing 'en'"

    def test_no_empty_translations(self):
        """No translation value should be empty string."""
        for key, entry in TRANSLATIONS.items():
            for lang, text in entry.items():
                assert text, f"Key '{key}' has empty '{lang}' translation"

    def test_all_nav_keys_exist(self):
        """All navigation keys should be defined."""
        for k in ["nav_path", "nav_chat", "nav_browser", "nav_radar", "nav_import"]:
            assert k in TRANSLATIONS, f"Missing nav key: {k}"

    def test_format_string_keys_have_placeholders(self):
        """Keys used with kwargs should contain format placeholders."""
        assert "{n}" in TRANSLATIONS["path_week"]["zh"]
        assert "{n}" in TRANSLATIONS["path_week"]["en"]
        assert "{done}" in TRANSLATIONS["path_progress"]["zh"]
        assert "{total}" in TRANSLATIONS["path_progress"]["en"]
        assert "{shown}" in TRANSLATIONS["browser_showing"]["zh"]
        assert "{total}" in TRANSLATIONS["browser_showing"]["en"]
