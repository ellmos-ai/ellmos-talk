"""Metadata, release-gate hygiene, and boundary contract tests for ellmos-talk."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    tomllib = pytest.importorskip("tomli")

from ellmos_talk import (
    TalkEngine,
    TalkVisualState,
    __version__,
    apply_talk_directive,
    extract_talk_directives,
)
from ellmos_talk.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_version_parity_across_package_pyproject_and_manifest() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))

    assert pyproject["project"]["version"] == __version__
    assert manifest["version"] == __version__
    assert manifest["id"] == pyproject["project"]["name"] == "ellmos-talk"


def test_v2_manifest_conforms_to_catalog_schema() -> None:
    manifest = json.loads((ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))

    assert manifest["schema"] == "ellmos.module.v2"
    assert manifest["category"] == "runtime"
    assert manifest["kind"] == "runtime"
    assert manifest["status"] == "development"
    assert manifest["visibility"] == "public"
    assert manifest["source_of_truth"] == {
        "type": "git-repository",
        "path": ".",
        "repository": "https://github.com/ellmos-ai/ellmos-talk",
    }
    assert manifest["entrypoints"] == {
        "python": "ellmos_talk.engine",
        "cli": "ellmos_talk.cli:main",
    }
    assert set(manifest["surfaces"]) >= {"library", "cli", "service"}
    assert manifest["boundaries"]["network"] == "local"
    assert manifest["boundaries"]["data"] == "user-local"


def test_pep561_pep639_and_pytest_hygiene() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]

    assert (ROOT / "src" / "ellmos_talk" / "py.typed").is_file()
    assert "Typing :: Typed" in project["classifiers"]
    assert not any(c.startswith("License ::") for c in project["classifiers"])
    assert project["license"] == "MIT"
    assert project["license-files"] == ["LICENSE"]
    assert "Repository" in project["urls"]
    assert "Security" in project["urls"]
    assert pyproject["tool"]["setuptools"]["package-data"]["ellmos_talk"] == ["py.typed"]

    addopts = pyproject["tool"]["pytest"]["ini_options"].get("addopts", "")
    assert "--basetemp" not in str(addopts)


def test_gitignore_and_release_governance_docs() -> None:
    gitignore_lines = {
        line.strip()
        for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    for required in ("__pycache__/", "*.pyc", ".env", "*.db", ".venv/", ".idea/", ".vscode/", "data/", "LOCK*.txt"):
        assert required in gitignore_lines

    assert (ROOT / "README.md").is_file()
    assert (ROOT / "README_de.md").is_file()
    assert (ROOT / "LICENSE").is_file()
    assert (ROOT / "CHANGELOG.md").is_file()

    todo_text = (ROOT / "TODO.md").read_text(encoding="utf-8")
    assert "## STATUS" in todo_text
    assert "**READY**" in todo_text

    security_text = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "https://github.com/ellmos-ai/ellmos-talk/security/advisories/new" in security_text
    assert "48 hours" in security_text and "48 Stunden" in security_text
    assert "5 business days" in security_text and "5 Werktagen" in security_text
    assert "30 calendar days" in security_text and "30 Kalendertagen" in security_text


def test_no_personal_home_paths_in_tracked_sources() -> None:
    pattern = re.compile(r"(?:[A-Za-z]:\\Users\\|/Users/|/home/)[^\s\"']+")
    for rel in (
        "pyproject.toml",
        "ellmos-module.v2.json",
        "README.md",
        "README_de.md",
        "SKILL.md",
        "llms.txt",
        "llm.txt",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "TODO.md",
        "CHANGELOG.md",
    ):
        content = (ROOT / rel).read_text(encoding="utf-8")
        assert not pattern.search(content), f"Personal path leak in {rel}"


def test_extract_directives_ignores_malformed_json_and_strips_unclosed_tags() -> None:
    raw = 'Hello <talk_control {not-json} /> world <talk_control {"emotion": "joyful"'
    cleaned, directives = extract_talk_directives(raw)
    assert directives == []
    assert "<talk_control" not in cleaned
    assert cleaned.startswith("Hello")


def test_apply_directive_bounds_and_wake_word_validation() -> None:
    with pytest.raises(ValueError, match="speed_hz"):
        apply_talk_directive(TalkVisualState(), {"speed_hz": 5.5})
    with pytest.raises(ValueError, match="speed_hz"):
        apply_talk_directive(TalkVisualState(), {"speed_hz": 0.05})
    with pytest.raises(ValueError, match="wake_word"):
        apply_talk_directive(TalkVisualState(), {"wake_word": "   "})

    updated = apply_talk_directive(TalkVisualState(), {"operating_mode": "wake_word", "speed_hz": 2.5})
    assert updated.operating_mode == "wake_word"
    assert updated.wake_word_enabled is True
    assert updated.speed_hz == 2.5


def test_summon_by_model_suppression_and_cli_directive(capsys: pytest.CaptureFixture[str]) -> None:
    engine = TalkEngine()
    engine.update_visual_state({"summon_policy": "muted"})
    suppressed = engine.summon_by_model("codex", "Ready")
    assert suppressed["accepted"] is False
    assert suppressed["delivery"] == "suppressed"

    assert main(["directive", '{"pattern": "wave", "emotion": "curious", "mode": "thinking"}']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["pattern"] == "wave"
    assert payload["emotion"] == "curious"
    assert payload["mode"] == "thinking"


def test_p022_llm_entrypoint_files() -> None:
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    llms_text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    llm_text = (ROOT / "llm.txt").read_text(encoding="utf-8")

    assert "name: ellmos-talk" in skill_text
    assert "ellmos-talk status" in skill_text
    assert "llms.txt" in llm_text
    assert "SKILL.md" in llm_text
    for required in ("Last-checked:", "## Prerequisites", "## Installation", "## Verification", "## Minimal Example"):
        assert required in llms_text


def test_community_governance_and_issue_templates() -> None:
    coc_text = (ROOT / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")
    contrib_text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    bug_tpl = (ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").read_text(encoding="utf-8")
    feat_tpl = (ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md").read_text(encoding="utf-8")

    assert "## Deutsch" in coc_text and "## English" in coc_text
    assert "## Deutsch" in contrib_text and "## English" in contrib_text
    assert "für" in contrib_text and "Änderung" in contrib_text
    assert "Tatsächliches Verhalten" in bug_tpl
    assert "Vorgeschlagene Lösung" in feat_tpl


def test_visual_assets_and_svg_integrity() -> None:
    import xml.etree.ElementTree as ET

    for rel in ("assets/banner.svg", "assets/banner.png", "assets/terminal-workflow.svg"):
        assert (ROOT / rel).is_file(), f"Missing asset {rel}"

    svg_root = ET.parse(ROOT / "assets" / "terminal-workflow.svg").getroot()
    assert svg_root.tag.endswith("svg")
    svg_text = (ROOT / "assets" / "terminal-workflow.svg").read_text(encoding="utf-8")
    assert "ellmos-talk" in svg_text
    assert "FastReflexLoop" in svg_text


def test_bilingual_readmes_badges_diagrams_and_attribution() -> None:
    for rel in ("README.md", "README_de.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "assets/banner.svg" in text
        assert "assets/terminal-workflow.svg" in text
        assert "SKILL.md" in text
        assert "llms.txt" in text
        assert "```mermaid" in text
        assert "flowchart LR" in text
        assert "sequenceDiagram" in text
        assert "Geiger" in text
        assert "MARKETING-LOG" not in text


def test_pyproject_keywords_and_frozen_version() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]

    assert project["version"] == "0.1.0"
    assert len(project.get("keywords", [])) >= 6
    assert "Documentation" in project.get("urls", {})
