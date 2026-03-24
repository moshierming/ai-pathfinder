"""E2E tests for core user flows using Playwright."""

import re
import pytest


pytestmark = pytest.mark.e2e


class TestAppLoads:
    """Verify the app starts and renders its main UI."""

    def test_title_visible(self, page, app_url):
        page.goto(app_url)
        page.wait_for_selector("[data-testid='stApp']", timeout=15000)
        assert page.title()

    def test_sidebar_present(self, page, app_url):
        page.goto(app_url)
        sidebar = page.wait_for_selector("[data-testid='stSidebar']", timeout=15000)
        assert sidebar.is_visible()

    def test_form_visible_on_first_load(self, page, app_url):
        page.goto(app_url)
        page.wait_for_selector("[data-testid='stApp']", timeout=15000)
        # Form should have level selector and goal input
        assert page.locator("text=当前水平").count() > 0 or page.locator("text=Current Level").count() > 0


class TestNavigation:
    """Test sidebar navigation between pages."""

    def test_navigate_to_chat(self, page, app_url):
        page.goto(app_url)
        page.wait_for_selector("[data-testid='stSidebar']", timeout=15000)
        # Click chat nav option
        page.locator("[data-testid='stSidebar']").locator("text=智能对话").click()
        page.wait_for_timeout(2000)
        # Chat page should show title
        assert page.locator("text=智能对话").count() > 0 or page.locator("text=AI Chat").count() > 0

    def test_navigate_to_browser(self, page, app_url):
        page.goto(app_url)
        page.wait_for_selector("[data-testid='stSidebar']", timeout=15000)
        page.locator("[data-testid='stSidebar']").locator("text=资源浏览").click()
        page.wait_for_timeout(2000)
        assert page.locator("text=资源库").count() > 0 or page.locator("text=Resource Library").count() > 0

    def test_navigate_to_radar(self, page, app_url):
        page.goto(app_url)
        page.wait_for_selector("[data-testid='stSidebar']", timeout=15000)
        page.locator("[data-testid='stSidebar']").locator("text=趋势雷达").click()
        page.wait_for_timeout(2000)
        assert page.locator("text=趋势雷达").count() > 0 or page.locator("text=Trend Radar").count() > 0


class TestResourceBrowser:
    """Test resource browsing functionality."""

    def test_resource_count_displayed(self, page, app_url):
        page.goto(app_url)
        page.wait_for_selector("[data-testid='stSidebar']", timeout=15000)
        page.locator("[data-testid='stSidebar']").locator("text=资源浏览").click()
        page.wait_for_timeout(2000)
        # Should show metric with resource count
        metrics = page.locator("[data-testid='stMetric']")
        assert metrics.count() > 0

    def test_search_filters_resources(self, page, app_url):
        page.goto(app_url)
        page.wait_for_selector("[data-testid='stSidebar']", timeout=15000)
        page.locator("[data-testid='stSidebar']").locator("text=资源浏览").click()
        page.wait_for_timeout(2000)
        # Type in search box
        search = page.locator("input[type='text']").first
        if search.is_visible():
            search.fill("RAG")
            page.wait_for_timeout(1000)
            # Page should still render without errors
            assert page.locator("[data-testid='stApp']").is_visible()


class TestLanguageToggle:
    """Test i18n language switching."""

    def test_toggle_to_english(self, page, app_url):
        page.goto(app_url)
        page.wait_for_selector("[data-testid='stSidebar']", timeout=15000)
        # Click language toggle button
        lang_btn = page.locator("[data-testid='stSidebar']").locator("button:has-text('🌐')")
        if lang_btn.count() > 0:
            lang_btn.click()
            page.wait_for_timeout(2000)
            # After toggle, should show English text
            assert page.locator("text=AI Pathfinder").count() > 0


class TestPresetTemplates:
    """Test quick-start preset templates."""

    def test_preset_buttons_visible(self, page, app_url):
        page.goto(app_url)
        page.wait_for_selector("[data-testid='stApp']", timeout=15000)
        # Preset section should have "选择" buttons
        select_btns = page.locator("button:has-text('选择')")
        assert select_btns.count() >= 4  # At least 4 presets visible
