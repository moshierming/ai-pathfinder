"""Tests for views/progress.py — persistence logic."""

import json
import os
import sys
import shutil
import unittest
from unittest.mock import MagicMock, patch

# Ensure the Streamlit mock is consistent with other test files
mock_st = sys.modules.get("streamlit") or MagicMock()
if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = mock_st
mock_st.cache_data = lambda **kw: (lambda fn: fn)

# Reset session_state for each test
mock_st.session_state = {}

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestCollectProgress(unittest.TestCase):
    def setUp(self):
        mock_st.session_state = {}

    def test_collects_done_keys(self):
        mock_st.session_state["done_r01_1"] = True
        mock_st.session_state["done_r02_1"] = False
        mock_st.session_state["done_r03_2"] = True
        mock_st.session_state["other_key"] = "ignored"
        from views.progress import collect_progress
        data = collect_progress()
        self.assertEqual(data["done"], {"done_r01_1": True, "done_r03_2": True})

    def test_collects_profile_and_path(self):
        mock_st.session_state["profile"] = {"level": "🔰 零基础"}
        mock_st.session_state["path"] = {"summary": "test path"}
        from views.progress import collect_progress
        data = collect_progress()
        self.assertEqual(data["profile"]["level"], "🔰 零基础")
        self.assertEqual(data["path"]["summary"], "test path")

    def test_collects_chat_messages(self):
        mock_st.session_state["chat_messages"] = [{"role": "user", "content": "hi"}]
        from views.progress import collect_progress
        data = collect_progress()
        self.assertEqual(len(data["chat_messages"]), 1)

    def test_version_field(self):
        from views.progress import collect_progress
        data = collect_progress()
        self.assertEqual(data["version"], 1)

    def test_empty_state(self):
        from views.progress import collect_progress
        data = collect_progress()
        self.assertIsNone(data["profile"])
        self.assertIsNone(data["path"])
        self.assertEqual(data["done"], {})
        self.assertEqual(data["chat_messages"], [])


class TestRestoreProgress(unittest.TestCase):
    def setUp(self):
        mock_st.session_state = {}

    def test_restores_profile_and_path(self):
        from views.progress import restore_progress
        data = {
            "profile": {"level": "🌱 初学者"},
            "path": {"summary": "restored path"},
        }
        result = restore_progress(data)
        self.assertTrue(result)
        self.assertEqual(mock_st.session_state["profile"]["level"], "🌱 初学者")
        self.assertEqual(mock_st.session_state["path"]["summary"], "restored path")

    def test_restores_done_keys(self):
        from views.progress import restore_progress
        data = {
            "profile": {"level": "test"},
            "path": {"summary": "test"},
            "done": {"done_r01_1": True, "done_r05_3": True},
        }
        restore_progress(data)
        self.assertTrue(mock_st.session_state.get("done_r01_1"))
        self.assertTrue(mock_st.session_state.get("done_r05_3"))

    def test_restores_chat(self):
        from views.progress import restore_progress
        data = {
            "profile": {"level": "test"},
            "path": {"summary": "test"},
            "chat_messages": [{"role": "user", "content": "hello"}],
        }
        restore_progress(data)
        self.assertEqual(len(mock_st.session_state["chat_messages"]), 1)

    def test_returns_false_on_invalid(self):
        from views.progress import restore_progress
        self.assertFalse(restore_progress(None))
        self.assertFalse(restore_progress({}))
        self.assertFalse(restore_progress({"profile": None, "path": None}))

    def test_restores_language(self):
        from views.progress import restore_progress
        data = {
            "profile": {"level": "test"},
            "path": {"summary": "test"},
            "ui_lang": "en",
        }
        restore_progress(data)
        self.assertEqual(mock_st.session_state["ui_lang"], "en")


class TestLocalFilePersistence(unittest.TestCase):
    _test_dir = os.path.join(os.path.dirname(__file__), "..", "progress")

    def setUp(self):
        mock_st.session_state = {}
        # Clean up test directory
        if os.path.exists(self._test_dir):
            shutil.rmtree(self._test_dir)

    def tearDown(self):
        if os.path.exists(self._test_dir):
            shutil.rmtree(self._test_dir)

    def test_save_and_load_roundtrip(self):
        mock_st.session_state["profile"] = {"level": "test"}
        mock_st.session_state["path"] = {"summary": "roundtrip"}
        mock_st.session_state["done_r01_1"] = True
        from views.progress import save_progress_local, load_progress_local
        path = save_progress_local()
        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))

        loaded = load_progress_local()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["profile"]["level"], "test")
        self.assertEqual(loaded["done"]["done_r01_1"], True)

    def test_save_returns_none_without_path(self):
        from views.progress import save_progress_local
        result = save_progress_local()
        self.assertIsNone(result)

    def test_load_returns_none_when_no_file(self):
        from views.progress import load_progress_local
        result = load_progress_local()
        self.assertIsNone(result)


class TestProgressToJson(unittest.TestCase):
    def test_serializes_to_json(self):
        mock_st.session_state = {}
        mock_st.session_state["profile"] = {"level": "test"}
        mock_st.session_state["path"] = {"summary": "json test"}
        from views.progress import progress_to_json
        result = progress_to_json()
        parsed = json.loads(result)
        self.assertEqual(parsed["profile"]["level"], "test")
        self.assertIn("saved_at", parsed)

    def test_accepts_explicit_data(self):
        from views.progress import progress_to_json
        data = {"version": 1, "profile": {"level": "x"}, "path": {"summary": "y"}}
        result = progress_to_json(data)
        parsed = json.loads(result)
        self.assertEqual(parsed["version"], 1)


if __name__ == "__main__":
    unittest.main()
