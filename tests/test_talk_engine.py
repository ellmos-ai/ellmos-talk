"""Tests for ellmos-talk dual-loop engine and visual directives."""

from __future__ import annotations

import json
import pytest

from ellmos_talk import (
    EMOTION_PALETTES,
    TalkEngine,
    TalkVisualState,
    apply_talk_directive,
    extract_talk_directives,
)
from ellmos_talk.cli import main


def test_extract_and_apply_directives():
    raw = (
        '<talk_control {"emotion": "joyful", "pattern": "constellation", "emoji_overlay": "🎉"} /> '
        "Hallo Lukas! Das hat wunderbar geklappt."
    )
    cleaned, directives = extract_talk_directives(raw)
    assert cleaned == "Hallo Lukas! Das hat wunderbar geklappt."
    assert len(directives) == 1
    state = apply_talk_directive(TalkVisualState(), directives[0])
    assert state.emotion == "joyful"
    assert state.pattern == "constellation"
    assert state.emoji_overlay == "🎉"
    assert state.color_primary == EMOTION_PALETTES["joyful"]["primary"]


def test_invalid_directive_raises():
    with pytest.raises(ValueError, match="Unsupported pattern"):
        apply_talk_directive(TalkVisualState(), {"pattern": "invalid"})
    with pytest.raises(ValueError, match="Unsupported emotion"):
        apply_talk_directive(TalkVisualState(), {"emotion": "angry_invalid"})


def test_reflex_barge_in_interrupts_speaking_mode():
    engine = TalkEngine()
    engine.update_visual_state({"mode": "speaking", "language": "de"})
    res = engine.process_turn("Warte kurz, ich habe noch eine Frage!")
    assert res.reflex.action == "barge_in"
    assert res.visual_state["mode"] == "listening"
    assert res.visual_state["pattern"] == "pulse"


def test_sentence_streaming_and_cortex_turn():
    engine = TalkEngine()
    engine.update_visual_state({"persona": "claude", "language": "en"})
    reply = (
        '<talk_control {"emotion": "focused", "pattern": "rings", "emoji_overlay": "🧠"} /> '
        "First sentence is ready immediately. Second sentence follows smoothly! Third concludes."
    )
    res = engine.process_turn("Explain the dual loop architecture in detail please.", model_response=reply)
    assert res.sentence_chunks == [
        "First sentence is ready immediately.",
        "Second sentence follows smoothly!",
        "Third concludes.",
    ]
    assert res.visual_state["emotion"] == "focused"
    assert res.visual_state["pattern"] == "rings"
    assert res.visual_state["mode"] == "speaking"


def test_cli_status_and_turn(capsys):
    assert main(["status"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["schema"] == "ellmos.talk.status.v1"

    assert main(["turn", "Wie geht es dir?", "--persona", "gemini", "--lang", "de"]) == 0
    turn_out = json.loads(capsys.readouterr().out)
    assert turn_out["visual_state"]["persona"] == "gemini"
    assert len(turn_out["sentence_chunks"]) >= 1



def test_operating_mode_model_binding_and_summon():
    engine = TalkEngine()
    state = engine.update_visual_state(
        {
            "operating_mode": "ptt",
            "bound_slot": "buddha_chat",
            "primary_model": "qwen3.8:27b-mlx",
            "fast_relay_model": "gemma4-e2b",
            "summon_policy": "knock",
            "language": "ar",
        }
    )
    assert state.operating_mode == "ptt"
    assert state.primary_model == "qwen3.8:27b-mlx"
    assert state.fast_relay_model == "gemma4-e2b"
    assert engine.reflex.model_name == "gemma4-e2b"
    assert state.language == "ar"

    summon = engine.summon_by_model(
        "claude",
        "Deployment auf Mac Studio ist bereit. Wollen wir starten?",
        emotion="focused",
        pattern="pulse",
    )
    assert summon["accepted"] is True
    assert summon["delivery"] == "knock"
    assert engine.state.pending_summon is not None
    assert engine.state.pending_summon["caller"] == "claude"

    ack = engine.acknowledge_summon(start_listening=True)
    assert ack["acknowledged"]["caller"] == "claude"
    assert engine.state.pending_summon is None
    assert engine.state.mode == "listening"


def test_device_selection_tauri_runtime_and_model_bundle():
    from ellmos_talk.directives import DEFAULT_TALK_MODEL_BUNDLE

    engine = TalkEngine()
    state = engine.update_visual_state(
        {
            "input_device_id": "usb-mic-01",
            "output_device_id": "headset-out-02",
            "camera_device_id": "webcam-front",
            "client_runtime": "tauri",
        }
    )
    assert state.input_device_id == "usb-mic-01"
    assert state.output_device_id == "headset-out-02"
    assert state.camera_device_id == "webcam-front"
    assert state.client_runtime == "tauri"
    assert any(m["id"] == "smollm2:360m" for m in DEFAULT_TALK_MODEL_BUNDLE["fast_relay_models"])
    assert any(m["id"] == "faster-whisper-base" for m in DEFAULT_TALK_MODEL_BUNDLE["stt_models"])
    assert any(m["id"] == "piper-de_DE-thorsten-high" for m in DEFAULT_TALK_MODEL_BUNDLE["tts_models"])

