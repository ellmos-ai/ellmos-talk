# TODO: ellmos-talk

**Audit Date:** 2026-11-18
**Auditor:** AI Modules Care (`ellmos-ai`)
**Target Repo:** `ellmos-ai/ellmos-talk`
**Version:** `0.1.0` (`development` / `public`)

---

## OPEN ROADMAP & OPERATIONS

- [ ] **Optional `ellmos-voice-io` adapter:** Implement and test optional STT/TTS/VAD bridge wiring for the declared `[voice]` extra (`ellmos-voice-io>=0.1.0`) while keeping core zero-dependency.
- [ ] **Multilingual backchannels:** Extend `FastReflexLoop.BACKCHANNELS` beyond `de`/`en` to the remaining `VALID_LANGUAGES` (`es`, `fr`, `zh`, `ja`, `ru`, `ar`, `pt`, `hi`, `it`) and expose them in CLI `--lang`.
- [ ] **Visual companion bridge:** Document and smoke-test `TalkVisualState` / `summon_by_model` event transport with `ellmos-system-gui` / Tauri companion clients.
- [ ] **GitHub CI workflow:** Add a minimal-privilege `.github/workflows/ci.yml` (`permissions: contents: read`) running `pytest`, `ruff check`, and `compileall` across Python 3.10–3.13.

---

## COMPLETED HYGIENE (2026-11-18)

- [x] Resolved all 7 `ruff check` findings (`RUF022`, `UP035`, `I001`, `RUF012` `ClassVar`) across `src/ellmos_talk/` and `tests/test_talk_engine.py`.
- [x] Hardened `.gitignore` with `final_gate_check.py` minimum entries (`*.pyc`, `.env`, `*.db`, `.venv/`, `.idea/`, `.vscode/`, `data/`, `LOCK*.txt`, secret/cache patterns).
- [x] Synchronized `ellmos-module.v2.json` to full `ellmos.module.v2` schema (`category: "runtime"`, `kind: "runtime"`, `status: "development"`, `visibility: "public"`, `source_of_truth: git-repository`, `provides`, `optional`, `surfaces`, `boundaries`) matching the module catalog.
- [x] Added PEP 561 marker `src/ellmos_talk/py.typed`, `"Typing :: Typed"` classifier, PEP 639 `license-files = ["LICENSE"]`, `[project.urls]`, and `norecursedirs` in `pyproject.toml`.
- [x] Created bilingual `SECURITY.md` (EN/DE, GitHub Private Vulnerability Reporting, `48h`/`5d`/`30d` SLAs) and `CHANGELOG.md`.
- [x] Added metadata/contract and directive/engine/CLI edge-case tests in `tests/test_metadata.py`.

---

## STATUS

| Category | Status | Notes |
|---|---|---|
| Secrets | :green_circle: | Verified clean via `final_gate_check.py` (no live secrets tracked) |
| Private Data (PII) | :green_circle: | Verified clean via `final_gate_check.py` (0 PII warnings) |
| .gitignore | :green_circle: | Contains `__pycache__/`, `*.pyc`, `*.py[cod]`, `.env`, `*.db`, `.venv/`, `.idea/`, `.vscode/`, `data/`, `LOCK*.txt` |
| Language (English) | :green_circle: | Bilingual `README.md` (EN) + `README_de.md` (DE) |
| BACH Internals | :green_circle: | None present |
| Database Files | :green_circle: | No `.db` or `.sqlite` files tracked |
| README.md | :green_circle: | Present with dual-loop overview, visual state values, installation, and CLI/Python examples |
| LICENSE | :green_circle: | MIT (`LICENSE` present and declared via PEP 639 `license-files`) |
| SECURITY.md | :green_circle: | Bilingual EN/DE policy with GitHub Private Vulnerability Reporting & 48h/5d/30d SLAs |
| **Overall** | **READY** | Gate check ready (`10 PASS, 0 FAIL, 0 WARN`) |

**Audit Date:** 2026-11-18
**Gate Check Exit Code:** `0`
