#!/usr/bin/env python3
"""Validate the Codex adaptation metadata and migration-sensitive text.

This intentionally avoids third-party dependencies so it can run in a fresh
checkout before any local plugin installation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGINS = [
    "commercial-legal",
    "privacy-legal",
    "product-legal",
    "corporate-legal",
    "employment-legal",
    "regulatory-legal",
    "ai-governance-legal",
    "litigation-legal",
    "law-student",
    "legal-clinic",
    "legal-builder-hub",
    "ip-legal",
]
PRIMARY_QUALITY_ENTRYPOINTS = {
    "commercial-legal": "review",
    "corporate-legal": "tabular-review",
    "employment-legal": "termination-review",
    "privacy-legal": "use-case-triage",
    "product-legal": "launch-review",
    "regulatory-legal": "reg-feed-watcher",
    "ai-governance-legal": "use-case-triage",
    "litigation-legal": "matter-intake",
    "law-student": "case-brief",
    "legal-clinic": "client-intake",
    "legal-builder-hub": "skills-qa",
    "ip-legal": "infringement-triage",
}

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
PLUGIN_SLASH_COMMAND = re.compile(r"(?<![A-Za-z0-9])/[A-Za-z0-9_-]+:")
CODEX_SKILL_REFERENCE = re.compile(
    r"(?<![/\w.-])(" + "|".join(re.escape(p) for p in sorted(PLUGINS, key=len, reverse=True)) + r"):([a-z0-9][a-z0-9-]*)"
)
CODEX_CONFIG_PATH = re.compile(r"~/.codex/plugins/config/claude-for-legal-zh/([^/\s`]+)/PRACTICE\.md")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report validation context.
        errors.append(f"{rel(path)}: invalid JSON: {exc}")
        return {}


def frontmatter(path: Path, errors: list[str]) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{rel(path)}: missing YAML frontmatter")
        return ""
    end = text.find("\n---", 4)
    if end == -1:
        errors.append(f"{rel(path)}: unterminated YAML frontmatter")
        return ""
    return text[4:end]


def validate_marketplace(errors: list[str]) -> None:
    path = ROOT / ".agents" / "plugins" / "marketplace.json"
    data = load_json(path, errors)
    entries = {entry.get("name"): entry for entry in data.get("plugins", [])}
    for plugin in PLUGINS:
        entry = entries.get(plugin)
        if not entry:
            errors.append(f"{rel(path)}: missing plugin entry {plugin}")
            continue
        source = entry.get("source", {})
        if source.get("source") != "local":
            errors.append(f"{rel(path)}: {plugin} source must be local")
        expected = f"./{plugin}"
        if source.get("path") != expected:
            errors.append(f"{rel(path)}: {plugin} source.path must be {expected}")
        if not (ROOT / plugin / ".codex-plugin" / "plugin.json").exists():
            errors.append(f"{plugin}: missing .codex-plugin/plugin.json")
        policy = entry.get("policy", {})
        if policy.get("installation") != "AVAILABLE" or policy.get("authentication") != "ON_INSTALL":
            errors.append(f"{rel(path)}: {plugin} must include default install/auth policy")


def validate_plugin_manifest(plugin: str, errors: list[str]) -> None:
    path = ROOT / plugin / ".codex-plugin" / "plugin.json"
    data = load_json(path, errors)
    if data.get("name") != plugin:
        errors.append(f"{rel(path)}: name must match directory")
    if not SEMVER.match(str(data.get("version", ""))):
        errors.append(f"{rel(path)}: version must be semver")
    for key in ("description", "skills", "mcpServers", "license"):
        if not data.get(key):
            errors.append(f"{rel(path)}: missing {key}")
    if data.get("skills") != "./skills/":
        errors.append(f"{rel(path)}: skills must be ./skills/")
    if data.get("mcpServers") != "./.mcp.json":
        errors.append(f"{rel(path)}: mcpServers must be ./.mcp.json")
    if "hooks" in data:
        errors.append(f"{rel(path)}: Codex manifest must not reference Claude hooks")
    if not (ROOT / plugin / ".mcp.json").exists():
        errors.append(f"{plugin}: missing .mcp.json referenced by manifest")
    else:
        mcp = load_json(ROOT / plugin / ".mcp.json", errors)
        if set(mcp) - {"mcpServers"}:
            errors.append(f"{plugin}/.mcp.json: only mcpServers is accepted by Codex plugin validation")
    interface = data.get("interface", {})
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities", "defaultPrompt"):
        if not interface.get(key):
            errors.append(f"{rel(path)}: missing interface.{key}")
    if not (ROOT / plugin / "PRACTICE.md").exists():
        errors.append(f"{plugin}: missing Codex PRACTICE.md template")


def validate_skill_frontmatter(plugin: str, errors: list[str]) -> None:
    for path in sorted((ROOT / plugin / "skills").glob("*/SKILL.md")):
        fm = frontmatter(path, errors)
        if not fm:
            continue
        name_match = re.search(r"^name:\s*(\S+)", fm, flags=re.M)
        if not name_match:
            errors.append(f"{rel(path)}: missing frontmatter name")
        elif name_match.group(1) != path.parent.name:
            errors.append(f"{rel(path)}: frontmatter name must match skill directory")
        if not re.search(r"^description:\s*", fm, flags=re.M):
            errors.append(f"{rel(path)}: missing frontmatter description")
        if re.search(r"^user-invocable:\s*false\s*$", fm, flags=re.M):
            if not re.search(r"(参考|内部|共享|Reference|Loaded by|加载|已弃用)", fm):
                errors.append(f"{rel(path)}: helper skill description must clearly mark internal/reference use")
        if path.parts[-2] == "cold-start-interview":
            text = path.read_text(encoding="utf-8")
            expected = f"~/.codex/plugins/config/claude-for-legal-zh/{plugin}/PRACTICE.md"
            if expected not in text:
                errors.append(f"{rel(path)}: missing Codex PRACTICE.md path")
            if "## Codex 画像路径与旧 Claude 迁移" not in text:
                errors.append(f"{rel(path)}: missing legacy Claude migration guidance")


def validate_quality_gate(plugin: str, errors: list[str]) -> None:
    gate_path = ROOT / plugin / "skills" / "quality-gate" / "SKILL.md"
    if not gate_path.exists():
        errors.append(f"{plugin}: missing internal quality-gate skill")
        return
    gate = gate_path.read_text(encoding="utf-8")
    for marker in ("user-invocable: false", "PRACTICE.md", "来源"):
        if marker not in gate:
            errors.append(f"{rel(gate_path)}: quality gate missing {marker}")
    practice = (ROOT / plugin / "PRACTICE.md").read_text(encoding="utf-8")
    if f"{plugin}:quality-gate" not in practice:
        errors.append(f"{plugin}/PRACTICE.md: missing internal quality-gate rule")
    entrypoint = PRIMARY_QUALITY_ENTRYPOINTS[plugin]
    entrypoint_path = ROOT / plugin / "skills" / entrypoint / "SKILL.md"
    if not entrypoint_path.exists():
        errors.append(f"{plugin}: missing representative entrypoint {entrypoint}")
    elif f"{plugin}:quality-gate" not in entrypoint_path.read_text(encoding="utf-8"):
        errors.append(f"{rel(entrypoint_path)}: does not load internal quality-gate")


def validate_commercial_layers(errors: list[str]) -> None:
    required_paths = (
        ROOT / "commercial-legal" / "skills" / "service-engagement-review" / "SKILL.md",
        ROOT / "commercial-legal" / "skills" / "public-sector-contract-overlay" / "SKILL.md",
        ROOT / "commercial-legal" / "references" / "public-sector-contract-core.md",
    )
    for path in required_paths:
        if not path.exists():
            errors.append(f"{rel(path)}: missing commercial general/public-sector review layer")


def validate_json_files(errors: list[str]) -> None:
    for path in ROOT.rglob("*.json"):
        if ".git" in path.parts:
            continue
        load_json(path, errors)


def validate_semantic_references(errors: list[str]) -> None:
    skills_by_plugin = {
        plugin: {path.parent.name for path in (ROOT / plugin / "skills").glob("*/SKILL.md")}
        for plugin in PLUGINS
    }
    checked_suffixes = {".md", ".yaml", ".yml", ".html"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in checked_suffixes:
            continue
        if ".git" in path.parts or ".claude-plugin" in path.parts:
            continue
        if path.name == "CLAUDE.md":
            continue
        text = path.read_text(encoding="utf-8")
        path_rel = rel(path)
        for plugin, skill in CODEX_SKILL_REFERENCE.findall(text):
            if skill not in skills_by_plugin[plugin]:
                errors.append(f"{path_rel}: references missing skill {plugin}:{skill}")
        for plugin in CODEX_CONFIG_PATH.findall(text):
            if plugin.startswith("<") and plugin.endswith(">"):
                continue
            if plugin not in PLUGINS:
                errors.append(f"{path_rel}: Codex PRACTICE.md path references unknown plugin {plugin}")


def validate_residual_text(errors: list[str]) -> None:
    checked_suffixes = {".md", ".yaml", ".yml", ".html"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in checked_suffixes:
            continue
        if ".git" in path.parts or ".claude-plugin" in path.parts:
            continue
        if path.name == "CLAUDE.md":
            continue
        text = path.read_text(encoding="utf-8")
        path_rel = rel(path)
        if PLUGIN_SLASH_COMMAND.search(text):
            errors.append(f"{path_rel}: contains legacy /plugin:skill command syntax")
        if "Codex marketplace add" in text or "Codex plugin install" in text:
            errors.append(f"{path_rel}: contains non-existent Codex CLI install wording")
        if "Claude Code" in text or "claude-code" in text:
            errors.append(f"{path_rel}: contains Claude Code instead of Codex")
        if "Cowork" in text:
            errors.append(f"{path_rel}: contains Cowork platform wording in Codex default docs")
        if "~/.claude" in text:
            is_allowed_migration = path_rel.endswith("/skills/cold-start-interview/SKILL.md")
            is_legacy_template = path.name == "CLAUDE.md"
            if not (is_allowed_migration or is_legacy_template):
                errors.append(f"{path_rel}: old ~/.claude path outside migration guidance")
        if "CLAUDE.md" in text:
            is_allowed = (
                path_rel in {"README.md", "QUICKSTART.md"}
                or path_rel.endswith("/skills/cold-start-interview/SKILL.md")
                or path.name == "CLAUDE.md"
            )
            if not is_allowed:
                errors.append(f"{path_rel}: references CLAUDE.md outside legacy compatibility docs")


def main() -> int:
    errors: list[str] = []
    validate_marketplace(errors)
    for plugin in PLUGINS:
        validate_plugin_manifest(plugin, errors)
        validate_skill_frontmatter(plugin, errors)
        validate_quality_gate(plugin, errors)
    validate_commercial_layers(errors)
    validate_json_files(errors)
    validate_semantic_references(errors)
    validate_residual_text(errors)
    if errors:
        print("Codex validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Codex validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
