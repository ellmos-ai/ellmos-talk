---
name: ellmos-talk
version: 0.1.0
description: "Product skill for ellmos-talk: dual-loop live speech & visual companion conversation logic (FastReflexLoop, DeepCortexLoop, TalkEngine, TalkVisualState, and <talk_control {...} /> directives)."
---

# ellmos-talk Product Skill

`ellmos-talk` is a dependency-free Python package (`v0.1.0`, status: `development`) that implements the **conversation logic** for a dual-loop live speech and visual companion runtime.

## Capabilities & Boundaries

### What `ellmos-talk` provides
- **Fast reflex turn-taking (`FastReflexLoop`):** Deterministic, regex/keyword-based sub-250 ms (`latency_budget_ms = 180`) turn evaluation returning a `ReflexDecision` (`barge_in`, `wake_triggered`, `hand_off_to_cortex`, plus `backchannel_text` and `emotion_hint`).
- **Sentence-streaming cortex adapter (`DeepCortexLoop`):** Splits model replies via `stream_sentences()` for immediate TTS synthesis and invokes an optional `responder(prompt, persona, language)` callable.
- **Visual companion state & directives (`TalkVisualState`, `extract_talk_directives`, `apply_talk_directive`):** Extracts inline `<talk_control {...} />` JSON directives, strips unclosed `<talk_control` fragments, validates fields against strict allowlists/bounds, and updates `TalkVisualState`.
- **Session orchestration (`TalkEngine`):** Coordinates `process_turn`, `preview_reflex`, `summon_by_model`, `acknowledge_summon`, `update_visual_state`, and `status`.
- **CLI (`ellmos-talk` / `python -m ellmos_talk.cli`):** Provides `status`, `turn`, and `directive` commands with structured JSON output.

### What `ellmos-talk` does NOT do in `v0.1.0`
- Does **not** capture microphone/camera audio, run STT/TTS/VAD models, or render a GUI window (host runtime / `ellmos-voice-io` responsibility).
- Does **not** load or execute LLMs itself; `DeepCortexLoop.generate_response()` returns a fixed placeholder reply unless a `responder` callable is injected.
- Performs **no** network requests and spawns **no** subprocesses (Python standard library only).

## Prerequisites & Installation

- **Python:** `>= 3.10`
- **Dependencies:** None at runtime (Python stdlib only). Optional extras: `dev` (`pytest>=8.0`, `ruff>=0.8`), `voice` (`ellmos-voice-io` pinned in `pyproject.toml`, not yet imported by `ellmos-talk`).

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate | Windows: .venv\Scripts\activate
pip install -e .
pip install -e ".[dev]"
```

## Safe Invocation & CLI Reference

### 1. CLI Commands (Read-only / Local State per Process)

```bash
# Inspect CLI usage
ellmos-talk --help
python -m ellmos_talk.cli --help

# Inspect default status and TalkVisualState (schema: ellmos.talk.status.v1)
ellmos-talk status

# Run a single turn through FastReflexLoop + DeepCortexLoop
ellmos-talk turn "Why is the build failing?" --persona claude --lang en

# Validate and apply a JSON directive
ellmos-talk directive '{"pattern": "wave", "emotion": "curious", "mode": "thinking"}'
```

- **CLI options for `turn`:** `--persona {buddha,gemini,claude,codex}` (default `buddha`), `--lang {de,en}` (default `de`).
- **Exit codes:** `0` on success, `2` on invalid CLI arguments, non-zero (`ValueError` / `json.JSONDecodeError`) on invalid directive JSON or out-of-range values.

### 2. Python API Usage

```python
from ellmos_talk import TalkEngine, TalkVisualState, apply_talk_directive, extract_talk_directives

engine = TalkEngine()

# Optional fast Stage-1 reflex preview (schema: ellmos.talk.reflex.v1)
preview = engine.preview_reflex("Wie ist der Status?", persona="buddha", language="de")

# Full turn with injected model reply containing inline <talk_control {...} />
result = engine.process_turn(
    "Explain the architecture.",
    model_response='<talk_control {"emotion": "focused", "pattern": "rings"} /> Step one. Step two.',
)
print(result.spoken_text)       # "Step one. Step two."
print(result.sentence_chunks)   # ["Step one.", "Step two."]
print(result.visual_state["emotion"])  # "focused"
```

### 3. Directive Validation Rules & Error Behavior

Invalid directive values raise `ValueError` fail-closed:
- `pattern`: `orb`, `wave`, `rings`, `constellation`, `pulse`
- `emotion`: `calm`, `curious`, `joyful`, `focused`, `empathetic`, `alert` (updates `color_primary`, `color_secondary`, `color_glow`)
- `mode`: `listening`, `speaking`, `thinking`, `idle`, `muted`
- `persona`: `buddha`, `gemini`, `claude`, `codex`
- `language`: `de`, `en`, `es`, `fr`, `zh`, `ja`, `ru`, `ar`, `pt`, `hi`, `it`
- `operating_mode`: `ptt`, `duplex`, `wake_word`, `off`
- `summon_policy`: `knock`, `auto_popup`, `muted`
- `client_runtime`: `browser`, `tauri`, `mobile`, `companion`
- `speed_hz`: float in `[0.1, 5.0]`
- `wake_word`: non-empty string

## Verification & Result Readback

```bash
pytest -ra -v
ellmos-talk status
```

Structured schemas returned by `TalkEngine`:
- `status()` -> `schema: "ellmos.talk.status.v1"`
- `preview_reflex()` -> `schema: "ellmos.talk.reflex.v1"`
- `summon_by_model()` -> `schema: "ellmos.talk.summon.v1"` (`delivery`: `"auto_popup"` | `"knock"` | `"suppressed"`)
- `acknowledge_summon()` -> `schema: "ellmos.talk.summon-ack.v1"`
- `process_turn()` -> `TalkTurnResult` (`spoken_text`, `sentence_chunks`, `reflex`, `visual_state`, `applied_directives`)

## Further Documentation

- [README.md](README.md) (English) · [README_de.md](README_de.md) (Deutsch)
- [llms.txt](llms.txt) · [ellmos-module.v2.json](ellmos-module.v2.json) · [SECURITY.md](SECURITY.md)
