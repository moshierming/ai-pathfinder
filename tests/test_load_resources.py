"""Tests for load_resources and resources.yaml integrity."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import load_resources
from config import DIRECTION_TO_DOMAIN


class TestLoadResources:
    """Verify resources.yaml loads correctly and has valid structure."""

    def test_returns_list(self):
        resources = load_resources()
        assert isinstance(resources, list)
        assert len(resources) > 0

    def test_unique_ids(self):
        resources = load_resources()
        ids = [r["id"] for r in resources]
        assert len(ids) == len(set(ids)), "Duplicate resource IDs found"

    def test_required_fields(self):
        base_required = {"id", "title", "url", "type", "topics", "level", "description"}
        resources = load_resources()
        for r in resources:
            required = base_required | ({"duration_hours"} if r["type"] != "builder" else set())
            for field in required:
                assert field in r, f"Resource {r.get('id', '?')} missing field '{field}'"

    def test_valid_types(self):
        valid_types = {"course", "video", "article", "repo", "book", "channel", "newsletter", "tool", "builder"}
        resources = load_resources()
        for r in resources:
            assert r["type"] in valid_types, f"Resource {r['id']} has unknown type '{r['type']}'"

    def test_valid_levels(self):
        valid_levels = {"beginner", "beginner-to-intermediate", "intermediate",
                        "intermediate-to-advanced", "advanced"}
        resources = load_resources()
        for r in resources:
            assert r["level"] in valid_levels, f"Resource {r['id']} has unknown level '{r['level']}'"

    def test_valid_focus(self):
        valid_focus = {"foundational", "applied", "both"}
        resources = load_resources()
        for r in resources:
            assert r.get("focus", "both") in valid_focus, f"Resource {r['id']} has unknown focus '{r.get('focus')}'"

    def test_domains_are_known(self):
        """All resource domains should match domains used in DIRECTION_TO_DOMAIN."""
        all_domains = {"general"}
        for domains in DIRECTION_TO_DOMAIN.values():
            all_domains.update(domains)
        resources = load_resources()
        for r in resources:
            for d in r.get("domain", ["general"]):
                assert d in all_domains, f"Resource {r['id']} has unknown domain '{d}'"

    def test_urls_are_strings(self):
        resources = load_resources()
        for r in resources:
            assert isinstance(r["url"], str)
            assert r["url"].startswith("http"), f"Resource {r['id']} URL doesn't start with http"

    def test_duration_positive(self):
        resources = load_resources()
        for r in resources:
            if r["type"] == "builder":
                continue
            assert r["duration_hours"] > 0, f"Resource {r['id']} has non-positive duration"

    def test_topics_are_lists(self):
        resources = load_resources()
        for r in resources:
            assert isinstance(r["topics"], list), f"Resource {r['id']} topics is not a list"

    def test_has_channels(self):
        """Should have at least a few channel-type resources for trend radar."""
        resources = load_resources()
        channels = [r for r in resources if r["type"] == "channel"]
        assert len(channels) >= 3, "Need at least 3 channel resources for trend radar"

    def test_language_values(self):
        valid_langs = {"zh", "en"}
        resources = load_resources()
        for r in resources:
            assert r.get("language", "en") in valid_langs, f"Resource {r['id']} has unknown language"

    def test_count_minimum(self):
        """Should have at least 50 resources."""
        resources = load_resources()
        assert len(resources) >= 50

    def test_has_builders(self):
        """Should have builder-type resources for trend radar builders section."""
        resources = load_resources()
        builders = [r for r in resources if r["type"] == "builder"]
        assert len(builders) >= 10, "Need at least 10 builder resources"

    def test_builder_has_role(self):
        """Every builder must declare a role."""
        valid_roles = {"researcher", "engineer", "founder", "educator"}
        resources = load_resources()
        for r in resources:
            if r["type"] != "builder":
                continue
            assert r.get("role") in valid_roles, f"Builder {r['id']} missing or invalid role"

    def test_builder_has_links(self):
        """Every builder should have at least one social link."""
        resources = load_resources()
        for r in resources:
            if r["type"] != "builder":
                continue
            links = r.get("links", {})
            assert isinstance(links, dict) and len(links) > 0, (
                f"Builder {r['id']} missing social links"
            )
