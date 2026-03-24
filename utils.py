"""Pure utility functions: profile encoding, resource filtering, export."""
from __future__ import annotations

import base64
import json
import os
from datetime import datetime

import yaml

from config import DIRECTION_TO_DOMAIN, TYPE_EMOJI


def load_resources() -> list[dict]:
    """Load resources from resources.yaml."""
    path = os.path.join(os.path.dirname(__file__), "resources.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["resources"]


def encode_profile(profile: dict) -> str:
    """Encode profile dict to URL-safe base64 string."""
    raw = json.dumps(profile, ensure_ascii=False, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_profile(s: str) -> dict | None:
    """Decode base64 string to profile dict, or None on failure."""
    if not s or len(s) > 50000:
        return None
    try:
        raw = base64.urlsafe_b64decode(s.encode()).decode()
        data = json.loads(raw)
        if not isinstance(data, dict):
            return None
        return data
    except Exception:
        return None


def filter_resources_for_direction(
    resources: list[dict[str, object]],
    direction: str,
    language: str,
    focus: str = "both",
) -> list[dict[str, object]]:
    """Pre-filter resources by direction + language + focus, capped at 50."""
    domains = DIRECTION_TO_DOMAIN.get(direction, [])
    if domains:
        matched = [r for r in resources if any(d in r.get("domain", ["general"]) for d in domains)]
        seen = {r["id"] for r in matched}
        general = [r for r in resources if r["id"] not in seen and r.get("domain", ["general"]) == ["general"]]
        filtered = matched + general
    else:
        filtered = list(resources)

    if focus in ("foundational", "applied"):
        preferred = [r for r in filtered if r.get("focus") == focus]
        both_focus = [r for r in filtered if r.get("focus") == "both" and r not in preferred]
        others = [r for r in filtered if r not in preferred and r not in both_focus]
        filtered = preferred + both_focus + others

    if "中文" in language:
        preferred = [r for r in filtered if r.get("language") == "zh"]
        others = [r for r in filtered if r.get("language") != "zh"]
        filtered = preferred + others
    elif "英文" in language:
        preferred = [r for r in filtered if r.get("language") == "en"]
        others = [r for r in filtered if r.get("language") != "en"]
        filtered = preferred + others

    return filtered[:20]


def export_plan_markdown(
    path_data: dict[str, object],
    profile: dict[str, object],
    resources: list[dict[str, object]],
) -> str:
    """Export learning path as readable Markdown."""
    ridx = {r["id"]: r for r in resources}
    lines = [
        "# 🧭 我的 AI 学习路径",
        "",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 📋 个人画像",
        "",
        f"- **水平**：{profile.get('level', '-')}",
        f"- **方向**：{profile.get('direction', '-')}",
        f"- **学习重心**：{profile.get('focus', 'both')}",
        f"- **目标**：{profile.get('goal', '-')}",
        f"- **每周时间**：{profile.get('hours_per_week', '-')} 小时",
        f"- **语言偏好**：{profile.get('language', '-')}",
        "",
        "## 📊 路径概览",
        "",
        f"{path_data.get('summary', '')}",
        f"预计 **{path_data.get('estimated_weeks', '?')}** 周完成。",
        "",
    ]

    for week in path_data.get("weeks", []):
        lines.append(f"### 📅 第 {week['week']} 周 — {week['goal']}")
        if week.get("tip"):
            lines.append(f"\n> 💡 {week['tip']}\n")
        for rid in week.get("resources", []):
            r = ridx.get(rid)
            if not r:
                continue
            typ_emoji = TYPE_EMOJI.get(r["type"], "🔗")
            lines.append(f"- [ ] {typ_emoji} [{r['title']}]({r['url']}) — {r['level']}, {r['duration_hours']}h")
        lines.append("")

    lines.extend([
        "---",
        "*由 [AI Pathfinder](https://github.com/moshierming/ai-pathfinder) 生成*",
    ])
    return "\n".join(lines)


def export_plan_json(path_data: dict[str, object], profile: dict[str, object]) -> str:
    """Export learning path as importable JSON."""
    return json.dumps({"profile": profile, "path": path_data}, ensure_ascii=False, indent=2)

