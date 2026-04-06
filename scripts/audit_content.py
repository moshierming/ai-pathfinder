#!/usr/bin/env python3
"""AI Pathfinder — 内容质量审计脚本.

Usage:
    python scripts/audit_content.py              # 基础审计（无网络请求）
    python scripts/audit_content.py --check-links  # 含链接有效性检测
    python scripts/audit_content.py --json         # JSON 输出（供 CI 使用）
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta

import yaml

# ── Constants ───────────────────────────────────────────────────────────────

REQUIRED_FIELDS_RESOURCE = {"id", "title", "url", "type", "topics", "domain",
                            "level", "description", "language", "free", "focus",
                            "duration_hours"}
REQUIRED_FIELDS_BUILDER = {"id", "title", "url", "type", "topics", "domain",
                           "level", "description", "language", "role", "links"}

VALID_TYPES = {"course", "video", "article", "repo", "book", "channel",
               "newsletter", "tool", "builder"}
VALID_LEVELS = {"beginner", "beginner-to-intermediate", "intermediate",
                "intermediate-to-advanced", "advanced"}
VALID_FOCUS = {"foundational", "applied", "both"}
VALID_ROLES = {"researcher", "engineer", "founder", "educator"}
VALID_LANGUAGES = {"zh", "en"}

MIN_DESC_LEN = 10
RECOMMENDED_DESC_LEN = 15
MAX_DESC_LEN = 100

COVERAGE_THRESHOLDS = {
    "beginner_pct": 20,
    "advanced_pct": 8,
    "zh_pct": 25,
    "min_per_domain": 5,
}

FRESHNESS_WARN_DAYS = 180   # 6 months
FRESHNESS_STALE_DAYS = 365  # 12 months

# ── Severity ────────────────────────────────────────────────────────────────

HIGH = "HIGH"
MED = "MED"
LOW = "LOW"


def load_yaml(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["resources"]


# ── Check Functions ─────────────────────────────────────────────────────────

def check_completeness(resources: list[dict]) -> list[dict]:
    """Check all required fields are present and non-empty."""
    issues = []
    for r in resources:
        rid = r.get("id", "???")
        is_builder = r.get("type") == "builder"
        required = REQUIRED_FIELDS_BUILDER if is_builder else REQUIRED_FIELDS_RESOURCE
        for field in required:
            if field not in r:
                issues.append({"severity": HIGH, "id": rid,
                               "msg": f"缺失必要字段: {field}"})
            elif r[field] is None or r[field] == "" or r[field] == []:
                issues.append({"severity": HIGH, "id": rid,
                               "msg": f"字段值为空: {field}"})
    return issues


def check_valid_enums(resources: list[dict]) -> list[dict]:
    """Check enum fields have valid values."""
    issues = []
    for r in resources:
        rid = r.get("id", "???")
        if r.get("type") not in VALID_TYPES:
            issues.append({"severity": HIGH, "id": rid,
                           "msg": f"无效 type: {r.get('type')}"})
        if r.get("level") not in VALID_LEVELS:
            issues.append({"severity": HIGH, "id": rid,
                           "msg": f"无效 level: {r.get('level')}"})
        if r.get("type") != "builder":
            if r.get("focus", "both") not in VALID_FOCUS:
                issues.append({"severity": MED, "id": rid,
                               "msg": f"无效 focus: {r.get('focus')}"})
        if r.get("type") == "builder":
            if r.get("role") not in VALID_ROLES:
                issues.append({"severity": HIGH, "id": rid,
                               "msg": f"无效 role: {r.get('role')}"})
        if r.get("language") not in VALID_LANGUAGES:
            issues.append({"severity": MED, "id": rid,
                           "msg": f"无效 language: {r.get('language')}"})
    return issues


def check_duplicates(resources: list[dict]) -> list[dict]:
    """Check for duplicate IDs and URLs."""
    issues = []
    # ID duplicates
    id_counts = Counter(r.get("id") for r in resources)
    for rid, count in id_counts.items():
        if count > 1:
            issues.append({"severity": HIGH, "id": rid,
                           "msg": f"ID 重复（出现 {count} 次）"})
    # URL duplicates (excluding deprecated, only within same category)
    active = [r for r in resources if not r.get("deprecated")]
    learning = [r for r in active if r.get("type") != "builder"]
    builders = [r for r in active if r.get("type") == "builder"]
    for group_name, group in [("learning", learning), ("builders", builders)]:
        url_map: dict[str, list[str]] = {}
        for r in group:
            url = r.get("url", "")
            url_map.setdefault(url, []).append(r.get("id", "???"))
        for url, ids in url_map.items():
            if len(ids) > 1:
                issues.append({"severity": HIGH, "id": ",".join(ids),
                               "msg": f"URL 重复（{group_name}）: {url}"})
    return issues


def check_descriptions(resources: list[dict]) -> list[dict]:
    """Check description length and quality."""
    issues = []
    for r in resources:
        rid = r.get("id", "???")
        desc = r.get("description", "")
        if len(desc) < MIN_DESC_LEN:
            issues.append({"severity": MED, "id": rid,
                           "msg": f"描述过短（{len(desc)}字，建议≥{RECOMMENDED_DESC_LEN}）: \"{desc}\""})
        elif len(desc) > MAX_DESC_LEN:
            issues.append({"severity": LOW, "id": rid,
                           "msg": f"描述过长（{len(desc)}字，建议≤{MAX_DESC_LEN}）"})
    return issues


def check_freshness(resources: list[dict]) -> list[dict]:
    """Check verified_date freshness."""
    issues = []
    now = datetime.now()
    resources_without_date = []
    for r in resources:
        rid = r.get("id", "???")
        if r.get("deprecated"):
            continue
        vd = r.get("verified_date")
        if not vd:
            resources_without_date.append(rid)
            continue
        try:
            verified = datetime.strptime(str(vd), "%Y-%m-%d")
            days = (now - verified).days
            if days > FRESHNESS_STALE_DAYS:
                issues.append({"severity": HIGH, "id": rid,
                               "msg": f"资源已过期（{days}天未验证），需要审查"})
            elif days > FRESHNESS_WARN_DAYS:
                issues.append({"severity": MED, "id": rid,
                               "msg": f"资源待检查（{days}天未验证）"})
        except ValueError:
            issues.append({"severity": MED, "id": rid,
                           "msg": f"verified_date 格式错误: {vd}（需要 YYYY-MM-DD）"})
    if resources_without_date:
        issues.append({"severity": LOW, "id": "GLOBAL",
                       "msg": f"{len(resources_without_date)} 条资源缺少 verified_date"})
    return issues


def check_coverage(resources: list[dict]) -> tuple[dict, list[dict]]:
    """Check distribution coverage across dimensions."""
    active = [r for r in resources if not r.get("deprecated")]
    learning = [r for r in active if r.get("type") != "builder"]
    builders = [r for r in active if r.get("type") == "builder"]

    stats = {
        "total": len(active),
        "learning": len(learning),
        "builders": len(builders),
    }

    issues = []

    # Level distribution
    level_counts = Counter(r.get("level") for r in learning)
    stats["levels"] = dict(level_counts)
    beginner_pct = level_counts.get("beginner", 0) / max(len(learning), 1) * 100
    advanced_pct = level_counts.get("advanced", 0) / max(len(learning), 1) * 100
    if beginner_pct < COVERAGE_THRESHOLDS["beginner_pct"]:
        issues.append({"severity": LOW, "id": "COVERAGE",
                       "msg": f"beginner 资源占比仅 {beginner_pct:.1f}%（建议≥{COVERAGE_THRESHOLDS['beginner_pct']}%）"})
    if advanced_pct < COVERAGE_THRESHOLDS["advanced_pct"]:
        issues.append({"severity": LOW, "id": "COVERAGE",
                       "msg": f"advanced 资源占比仅 {advanced_pct:.1f}%（建议≥{COVERAGE_THRESHOLDS['advanced_pct']}%）"})

    # Language distribution
    lang_counts = Counter(r.get("language") for r in active)
    stats["languages"] = dict(lang_counts)
    zh_pct = lang_counts.get("zh", 0) / max(len(active), 1) * 100
    if zh_pct < COVERAGE_THRESHOLDS["zh_pct"]:
        issues.append({"severity": LOW, "id": "COVERAGE",
                       "msg": f"中文资源占比仅 {zh_pct:.1f}%（建议≥{COVERAGE_THRESHOLDS['zh_pct']}%）"})

    # Type distribution
    type_counts = Counter(r.get("type") for r in active)
    stats["types"] = dict(type_counts)

    # Domain distribution
    domain_counts: Counter = Counter()
    for r in learning:
        for d in r.get("domain", ["general"]):
            domain_counts[d] += 1
    stats["domains"] = dict(domain_counts)
    for domain, count in domain_counts.items():
        if count < COVERAGE_THRESHOLDS["min_per_domain"]:
            issues.append({"severity": LOW, "id": "COVERAGE",
                           "msg": f"domain '{domain}' 仅有 {count} 条资源（建议≥{COVERAGE_THRESHOLDS['min_per_domain']}）"})

    # Topic distribution (top 20)
    topic_counts: Counter = Counter()
    for r in learning:
        for t in r.get("topics", []):
            topic_counts[t] += 1
    stats["top_topics"] = dict(topic_counts.most_common(20))

    return stats, issues


def check_links(resources: list[dict]) -> list[dict]:
    """Check URL accessibility (requires network). Only checks active resources."""
    try:
        import urllib.request
        import urllib.error
        import ssl
    except ImportError:
        return [{"severity": LOW, "id": "SYSTEM", "msg": "无法导入 urllib，跳过链接检测"}]

    issues = []
    active = [r for r in resources if not r.get("deprecated")]
    ctx = ssl.create_default_context()

    for r in active:
        rid = r.get("id", "???")
        url = r.get("url", "")
        try:
            req = urllib.request.Request(url, method="HEAD",
                                         headers={"User-Agent": "AI-Pathfinder-Audit/1.0"})
            resp = urllib.request.urlopen(req, timeout=10, context=ctx)
            if resp.status >= 400:
                issues.append({"severity": HIGH, "id": rid,
                               "msg": f"链接返回 HTTP {resp.status}: {url}"})
        except urllib.error.HTTPError as e:
            if e.code == 403:
                # Many sites block HEAD requests; don't flag as broken
                pass
            elif e.code >= 400:
                issues.append({"severity": HIGH, "id": rid,
                               "msg": f"链接返回 HTTP {e.code}: {url}"})
        except Exception as e:
            issues.append({"severity": MED, "id": rid,
                           "msg": f"链接无法访问: {url} ({type(e).__name__})"})
    return issues


# ── Report ──────────────────────────────────────────────────────────────────

SEVERITY_ICON = {HIGH: "❌", MED: "⚠️", LOW: "ℹ️"}
SEVERITY_ORDER = {HIGH: 0, MED: 1, LOW: 2}


def print_report(stats: dict, all_issues: list[dict], as_json: bool = False) -> int:
    """Print audit report. Returns exit code (1 if HIGH issues found)."""
    if as_json:
        print(json.dumps({"stats": stats, "issues": all_issues}, ensure_ascii=False, indent=2))
        return 1 if any(i["severity"] == HIGH for i in all_issues) else 0

    print("\n" + "=" * 60)
    print("  AI Pathfinder 内容质量审计报告")
    print("=" * 60)

    # Stats
    print(f"\n📊 总览")
    print(f"  资源总数: {stats['total']}（学习: {stats['learning']}, Builders: {stats['builders']}）")
    print(f"  类型分布: {stats.get('types', {})}")
    print(f"  语言分布: {stats.get('languages', {})}")
    print(f"  难度分布: {stats.get('levels', {})}")

    # Coverage
    print(f"\n📈 领域覆盖")
    for domain, count in sorted(stats.get("domains", {}).items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 40)
        print(f"  {domain:20s} {bar} {count}")

    print(f"\n🏷️  热门话题 (Top 15)")
    for topic, count in list(stats.get("top_topics", {}).items())[:15]:
        bar = "█" * min(count, 40)
        print(f"  {topic:25s} {bar} {count}")

    # Issues
    if all_issues:
        sorted_issues = sorted(all_issues, key=lambda i: SEVERITY_ORDER.get(i["severity"], 9))
        high_count = sum(1 for i in all_issues if i["severity"] == HIGH)
        med_count = sum(1 for i in all_issues if i["severity"] == MED)
        low_count = sum(1 for i in all_issues if i["severity"] == LOW)

        print(f"\n🔍 发现 {len(all_issues)} 个问题（❌ HIGH: {high_count}, ⚠️ MED: {med_count}, ℹ️ LOW: {low_count}）")
        for issue in sorted_issues:
            icon = SEVERITY_ICON.get(issue["severity"], "?")
            print(f"  {icon} [{issue['severity']}] {issue['id']}: {issue['msg']}")
    else:
        print(f"\n✅ 未发现任何质量问题！")

    has_high = any(i["severity"] == HIGH for i in all_issues)
    print(f"\n{'❌ 审计未通过 — 存在 HIGH 级别问题' if has_high else '✅ 审计通过'}")
    print("=" * 60 + "\n")
    return 1 if has_high else 0


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI Pathfinder 内容质量审计")
    parser.add_argument("--check-links", action="store_true",
                        help="检测链接有效性（需要网络，较慢）")
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 格式输出审计结果")
    args = parser.parse_args()

    yaml_path = os.path.join(os.path.dirname(__file__), "..", "resources.yaml")
    yaml_path = os.path.normpath(yaml_path)

    if not os.path.exists(yaml_path):
        print(f"❌ 找不到 resources.yaml: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    resources = load_yaml(yaml_path)

    all_issues: list[dict] = []
    all_issues.extend(check_completeness(resources))
    all_issues.extend(check_valid_enums(resources))
    all_issues.extend(check_duplicates(resources))
    all_issues.extend(check_descriptions(resources))
    all_issues.extend(check_freshness(resources))

    stats, coverage_issues = check_coverage(resources)
    all_issues.extend(coverage_issues)

    if args.check_links:
        print("🔗 正在检测链接有效性...（可能需要几分钟）")
        all_issues.extend(check_links(resources))

    exit_code = print_report(stats, all_issues, as_json=args.json)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
