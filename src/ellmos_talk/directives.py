"""Model-driven visual state and <talk_control {...} /> directive parser."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import re
from typing import Any

VALID_PATTERNS = ("orb", "wave", "rings", "constellation", "pulse")
VALID_EMOTIONS = ("calm", "curious", "joyful", "focused", "empathetic", "alert")
VALID_MODES = ("listening", "speaking", "thinking", "idle", "muted")
VALID_LANGUAGES = ("de", "en", "es", "fr", "zh", "ja", "ru", "ar", "pt", "hi", "it")
VALID_PERSONAS = ("buddha", "gemini", "claude", "codex")
VALID_OPERATING_MODES = ("ptt", "duplex", "wake_word", "off")
VALID_SUMMON_POLICIES = ("knock", "auto_popup", "muted")
VALID_CLIENT_RUNTIMES = ("browser", "tauri", "mobile", "companion")

DEFAULT_TALK_MODEL_BUNDLE: dict[str, Any] = {
    "fast_relay_models": [
        {"id": "smollm2:360m", "provider": "ollama", "size_mb": 250, "default": True, "role": "fast_relay"},
        {"id": "qwen3-0.6b-voice", "provider": "ollama", "size_mb": 400, "default": False, "role": "fast_relay"},
        {"id": "gemma4-e2b", "provider": "ollama", "size_mb": 1500, "default": False, "role": "fast_relay"},
    ],
    "stt_models": [
        {"id": "faster-whisper-base", "provider": "ellmos-voice-io", "size_mb": 145, "default": True, "role": "stt"},
        {"id": "faster-whisper-small", "provider": "ellmos-voice-io", "size_mb": 460, "default": False, "role": "stt"},
    ],
    "tts_models": [
        {"id": "piper-de_DE-thorsten-high", "provider": "ellmos-voice-io", "size_mb": 60, "default": True, "role": "tts_de"},
        {"id": "piper-en_US-lessac-medium", "provider": "ellmos-voice-io", "size_mb": 60, "default": True, "role": "tts_en"},
        {"id": "kokoro-82m-v1.0", "provider": "ellmos-voice-io", "size_mb": 80, "default": True, "role": "tts_multilingual"},
    ],
    "vad_wake_models": [
        {"id": "silero-vad-v5", "provider": "ellmos-voice-io", "size_mb": 2, "default": True, "role": "vad"},
        {"id": "openwakeword-hey-buddha", "provider": "ellmos-voice-io", "size_mb": 5, "default": True, "role": "wake_word"},
    ],
}

EMOTION_PALETTES: dict[str, dict[str, str]] = {
    "calm": {"primary": "#00d4aa", "secondary": "#0ea5e9", "glow": "rgba(0, 212, 170, 0.38)"},
    "curious": {"primary": "#38bdf8", "secondary": "#818cf8", "glow": "rgba(56, 189, 248, 0.42)"},
    "joyful": {"primary": "#fbbf24", "secondary": "#f472b6", "glow": "rgba(251, 191, 36, 0.45)"},
    "focused": {"primary": "#6366f1", "secondary": "#22d3ee", "glow": "rgba(99, 102, 241, 0.44)"},
    "empathetic": {"primary": "#ec4899", "secondary": "#a855f7", "glow": "rgba(236, 72, 153, 0.40)"},
    "alert": {"primary": "#f97316", "secondary": "#ef4444", "glow": "rgba(249, 115, 22, 0.48)"},
}

_DIRECTIVE_RE = re.compile(r"<talk_control\s+(\{.*?\})\s*/?>", re.DOTALL)


@dataclass(frozen=True)
class TalkVisualState:
    persona: str = "buddha"
    language: str = "de"
    mode: str = "idle"
    pattern: str = "orb"
    emotion: str = "calm"
    color_primary: str = "#00d4aa"
    color_secondary: str = "#0ea5e9"
    color_glow: str = "rgba(0, 212, 170, 0.38)"
    emoji_overlay: str = "🧘"
    wake_word: str = "hey buddha"
    wake_word_enabled: bool = True
    speed_hz: float = 1.0
    operating_mode: str = "ptt"  # "ptt" (Funkgerät) | "duplex" | "wake_word" | "off"
    bound_slot: str = "buddha_chat"
    primary_model: str = "qwen3.8:27b-mlx"
    fast_relay_model: str = "smollm2:360m"
    summon_policy: str = "knock"  # "knock" | "auto_popup" | "muted"
    pending_summon: dict[str, Any] | None = None
    input_device_id: str = "default"
    output_device_id: str = "default"
    camera_device_id: str = "default"
    client_runtime: str = "browser"  # "browser" | "tauri" | "mobile" | "companion"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def extract_talk_directives(text: str) -> tuple[str, list[dict[str, Any]]]:
    """Extract inline `<talk_control {...} />` JSON directives and return clean spoken text."""
    directives: list[dict[str, Any]] = []

    def _replace(match: re.Match[str]) -> str:
        raw_json = match.group(1)
        try:
            parsed = json.loads(raw_json)
            if isinstance(parsed, dict):
                directives.append(parsed)
                return ""
        except json.JSONDecodeError:
            pass
        return match.group(0)

    cleaned = _DIRECTIVE_RE.sub(_replace, text)
    cleaned = re.sub(r"<talk_control\b[^>]*>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<talk_control\b[^\n]*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned).strip()
    return cleaned, directives


def apply_talk_directive(state: TalkVisualState, directive: dict[str, Any]) -> TalkVisualState:
    """Apply a validated model or user directive to TalkVisualState."""
    updates: dict[str, Any] = {}

    if "persona" in directive:
        persona = str(directive["persona"]).strip().lower()
        if persona not in VALID_PERSONAS:
            raise ValueError(f"Unsupported persona: {persona}")
        updates["persona"] = persona

    if "language" in directive:
        lang = str(directive["language"]).strip().lower()
        if lang not in VALID_LANGUAGES:
            raise ValueError(f"Unsupported language: {lang}")
        updates["language"] = lang

    if "mode" in directive:
        mode = str(directive["mode"]).strip().lower()
        if mode not in VALID_MODES:
            raise ValueError(f"Unsupported mode: {mode}")
        updates["mode"] = mode

    if "pattern" in directive:
        pattern = str(directive["pattern"]).strip().lower()
        if pattern not in VALID_PATTERNS:
            raise ValueError(f"Unsupported pattern: {pattern}")
        updates["pattern"] = pattern

    if "emotion" in directive:
        emotion = str(directive["emotion"]).strip().lower()
        if emotion not in VALID_EMOTIONS:
            raise ValueError(f"Unsupported emotion: {emotion}")
        palette = EMOTION_PALETTES[emotion]
        updates["emotion"] = emotion
        updates["color_primary"] = palette["primary"]
        updates["color_secondary"] = palette["secondary"]
        updates["color_glow"] = palette["glow"]

    if "color_primary" in directive and isinstance(directive["color_primary"], str):
        updates["color_primary"] = directive["color_primary"].strip()
    if "color_secondary" in directive and isinstance(directive["color_secondary"], str):
        updates["color_secondary"] = directive["color_secondary"].strip()

    if "emoji_overlay" in directive and isinstance(directive["emoji_overlay"], str):
        updates["emoji_overlay"] = directive["emoji_overlay"].strip()[:8]

    if "wake_word" in directive and isinstance(directive["wake_word"], str):
        ww = directive["wake_word"].strip().lower()
        if not ww:
            raise ValueError("wake_word must not be empty")
        updates["wake_word"] = ww

    if "wake_word_enabled" in directive:
        updates["wake_word_enabled"] = bool(directive["wake_word_enabled"])

    if "speed_hz" in directive:
        speed = float(directive["speed_hz"])
        if not 0.1 <= speed <= 5.0:
            raise ValueError("speed_hz must be in [0.1, 5.0]")
        updates["speed_hz"] = speed

    if "operating_mode" in directive:
        op_mode = str(directive["operating_mode"]).strip().lower()
        if op_mode not in VALID_OPERATING_MODES:
            raise ValueError(f"Unsupported operating_mode: {op_mode}")
        updates["operating_mode"] = op_mode
        if op_mode == "wake_word":
            updates["wake_word_enabled"] = True

    if "bound_slot" in directive and isinstance(directive["bound_slot"], str):
        bs = directive["bound_slot"].strip()
        if bs:
            updates["bound_slot"] = bs

    if "primary_model" in directive and isinstance(directive["primary_model"], str):
        pm = directive["primary_model"].strip()
        if pm:
            updates["primary_model"] = pm

    if "fast_relay_model" in directive and isinstance(directive["fast_relay_model"], str):
        fm = directive["fast_relay_model"].strip()
        if fm:
            updates["fast_relay_model"] = fm

    if "summon_policy" in directive:
        sp = str(directive["summon_policy"]).strip().lower()
        if sp not in VALID_SUMMON_POLICIES:
            raise ValueError(f"Unsupported summon_policy: {sp}")
        updates["summon_policy"] = sp

    if "pending_summon" in directive:
        ps = directive["pending_summon"]
        if ps is None or isinstance(ps, dict):
            updates["pending_summon"] = ps

    for dev_field in ("input_device_id", "output_device_id", "camera_device_id"):
        if dev_field in directive and isinstance(directive[dev_field], str):
            val = directive[dev_field].strip()
            if val:
                updates[dev_field] = val

    if "client_runtime" in directive:
        cr = str(directive["client_runtime"]).strip().lower()
        if cr not in VALID_CLIENT_RUNTIMES:
            raise ValueError(f"Unsupported client_runtime: {cr}")
        updates["client_runtime"] = cr

    return replace(state, **updates)
