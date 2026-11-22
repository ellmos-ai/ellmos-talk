# Changelog

All notable changes to `ellmos-talk` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Standardized `TODO.md` with release-gate `## STATUS` table (`10/10 PASS` on `final_gate_check.py`).
- Bilingual `SECURITY.md` (EN/DE) documenting local-only boundaries, allowlist validation, GitHub Private Vulnerability Reporting, and `48h`/`5d`/`30d` SLAs (`INV-SLA-09` & `INV-SLA-10`).
- PEP 561 typing marker (`src/ellmos_talk/py.typed`), `"Typing :: Typed"` classifier, PEP 639 `license-files = ["LICENSE"]`, `[project.urls]`, and `norecursedirs` in `pyproject.toml`.
- Contract and edge-case tests in `tests/test_metadata.py` covering version parity, v2 manifest schema conformance, PEP 561/639 metadata, `.gitignore` hygiene, bilingual docs, `extract_talk_directives` edge cases, `speed_hz`/`wake_word` validation, `summon_by_model` suppression policies, and CLI `directive`.

### Changed
- Fixed all 7 `ruff check` lint findings (`RUF022` sorted `__all__`, `UP035` `collections.abc`, `I001` import sorting, `RUF012` `ClassVar` annotation for `FastReflexLoop.BACKCHANNELS`).
- Hardened `.gitignore` with complete Python, test/lint cache, environment/secret, database, IDE, and multi-agent lock exclusion rules (`*.pyc`, `.env*`, `*.db`, `.venv/`, `.idea/`, `.vscode/`, `data/`, `LOCK*.txt`).
- Synchronized `ellmos-module.v2.json` to the canonical `ellmos.module.v2` schema (`category: "runtime"`, `kind: "runtime"`, `status: "development"`, `visibility: "public"`, `provides`, `optional`, `surfaces`, `boundaries`, `source_of_truth`), keeping version `0.1.0` unchanged.

## [0.1.0] - 2026-11-08

### Added
- Initial public module implementation of `ellmos-talk` (`FastReflexLoop`, `DeepCortexLoop`, `TalkEngine`, `TalkVisualState`, `extract_talk_directives`, `apply_talk_directive`, and `ellmos-talk` CLI).
- Bilingual documentation (`README.md`, `README_de.md`), `LICENSE` (MIT), and repository banner (`assets/banner.svg`, `assets/banner.png`).
