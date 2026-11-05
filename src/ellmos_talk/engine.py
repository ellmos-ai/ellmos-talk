"""Dual-Loop Live Conversation Engine (FastReflexLoop + DeepCortexLoop)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import re
from typing import Any, Callable

from .directives import (
    TalkVisualState,
     VALID_PERSONAS,
    apply_talk_directive,
    extract_talk_directives,
)

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")


@dataclass(frozen=True)
class ReflexDecision:
    action: str  # "continue" | "barge_in" | "backchannel" | "hand_off_to_cortex" | "wake_triggered"
    backchannel_text: str | None
    emotion_hint: str
    latency_budget_ms: int = 180

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TalkTurnResult:
    spoken_text: str
    sentence_chunks: list[str]
    reflex: ReflexDecision
    visual_state: dict[str, Any]
    applied_directives: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class FastReflexLoop:
    """Sub-250ms reflex controller for turn-taking, barge-in, wake-word, and backchanneling."""

    BACKCHANNELS = {
        "de": {
            "thinking": "Einen kurzen Moment, ich schaue mir das an.",
            "ack": "Verstanden.",
            "barge_in": "Ich höre dir zu.",
        },
        "en": {
            "thinking": "One moment, let me check that.",
            "ack": "Got it.",
            "barge_in": "I'm listening.",
        },
    }

    def __init__(self, model_name: str = "smollm2:360m"):
        self.model_name = model_name

    def evaluate_utterance(
        self,
        utterance: str,
        *,
        current_mode: str = "idle",
        language: str = "de",
        wake_word: str = "hey buddha",
        wake_word_enabled: bool = True,
    ) -> ReflexDecision:
        text = utterance.strip()
        lower = text.lower()
        lang_pack = self.BACKCHANNELS.get(language, self.BACKCHANNELS["de"])

        if current_mode == "speaking" and text:
            return ReflexDecision(
                action="barge_in",
                backchannel_text=lang_pack["barge_in"],
                emotion_hint="focused",
            )

        if wake_word_enabled and wake_word and lower.startswith(wake_word.lower()):
            remainder = text[len(wake_word) :].lstrip(" ,.!?:;-")
            if not remainder:
                return ReflexDecision(
                    action="wake_triggered",
                    backchannel_text=lang_pack["barge_in"],
                    emotion_hint="curious",
                )

        if re.fullmatch(r"\s*(stop|stopp|halt|warte(?:\s+kurz)?|wait|pause)[.!?\s]*", lower):
            return ReflexDecision(
                action="barge_in",
                backchannel_text=lang_pack["barge_in"],
                emotion_hint="alert",
            )

        emotion_hint = "calm"
        if "?" in text or any(w in lower for w in ("warum", "wie", "why", "how", "erklär")):
            emotion_hint = "curious"
        elif any(w in lower for w in ("danke", "super", "klasse", "great", "thanks")):
            emotion_hint = "joyful"
        elif any(w in lower for w in ("fehler", "problem", "kaputt", "error", "urgent")):
            emotion_hint = "focused"

        needs_thinking_bridge = len(text.split()) >= 5 or "?" in text
        return ReflexDecision(
            action="hand_off_to_cortex",
            backchannel_text=lang_pack["thinking"] if needs_thinking_bridge else lang_pack["ack"],
            emotion_hint=emotion_hint,
        )


class DeepCortexLoop:
    """Sentence-streaming adapter for the primary reasoning model (Buddha, Gemini, Claude, Codex)."""

    def __init__(self, responder: Callable[[str, str, str], str] | None = None):
        self._responder = responder

    def stream_sentences(self, text: str) -> list[str]:
        """Split a clean response into low-latency sentence chunks for immediate TTS synthesis."""
        cleaned = text.strip()
        if not cleaned:
            return []
        parts = [p.strip() for p in _SENTENCE_SPLIT_RE.split(cleaned) if p.strip()]
        return parts or [cleaned]

    def generate_response(self, prompt: str, *, persona: str = "buddha", language: str = "de") -> str:
        if self._responder is not None:
            return self._responder(prompt, persona, language)
        if language == "en":
            return (
                '<talk_control {"emotion": "curious", "pattern": "wave", "emoji_overlay": "✨"} /> '
                f"[{persona.capitalize()}] I heard you clearly. How would you like to proceed?"
            )
        return (
            '<talk_control {"emotion": "curious", "pattern": "wave", "emoji_overlay": "✨"} /> '
            f"[{persona.capitalize()}] Ich habe dich klar verstanden. Wie wollen wir weitermachen?"
        )


class TalkEngine:
    """Coordinator combining FastReflexLoop, DeepCortexLoop, and TalkVisualState."""

    def __init__(
        self,
        reflex: FastReflexLoop | None = None,
        cortex: DeepCortexLoop | None = None,
        initial_state: TalkVisualState | None = None,
    ):
        self.reflex = reflex or FastReflexLoop()
        self.cortex = cortex or DeepCortexLoop()
        self.state = initial_state or TalkVisualState()

    def update_visual_state(self, directive: dict[str, Any]) -> TalkVisualState:
        self.state = apply_talk_directive(self.state, directive)
        if "fast_relay_model" in directive and isinstance(directive["fast_relay_model"], str):
            self.reflex.model_name = directive["fast_relay_model"].strip()
        return self.state

    def summon_by_model(
        self,
        caller: str,
        message: str,
        *,
        emotion: str = "focused",
        pattern: str = "pulse",
        emoji_overlay: str = "📻",
        presence_verified: bool = True,
        voice_allowed: bool = True,
    ) -> dict[str, Any]:
        """Allow a model (Buddha, Claude, Gemini, Codex) to initiate a live Funkgerät/Talk session."""
        norm_caller = str(caller or "buddha").strip().lower()
        persona = norm_caller if norm_caller in VALID_PERSONAS else self.state.persona
        policy = self.state.summon_policy
        if not voice_allowed or policy == "muted" or self.state.operating_mode == "off":
            return {
                "schema": "ellmos.talk.summon.v1",
                "accepted": False,
                "delivery": "suppressed",
                "reason": "muted_or_voice_disabled",
                "visual_state": self.state.as_dict(),
            }
        auto_open = bool(policy == "auto_popup" and presence_verified)
        delivery = "auto_popup" if auto_open else "knock"
        summon_payload = {
            "caller": norm_caller,
            "persona": persona,
            "message": str(message or "").strip(),
            "emotion": emotion,
            "pattern": pattern,
            "emoji_overlay": emoji_overlay,
            "delivery": delivery,
            "auto_open": auto_open,
            "presence_verified": presence_verified,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state = apply_talk_directive(
            self.state,
            {
                "persona": persona,
                "emotion": emotion if emotion in ("calm", "curious", "joyful", "focused", "empathetic", "alert") else "focused",
                "pattern": pattern if pattern in ("orb", "wave", "rings", "constellation", "pulse") else "pulse",
                "emoji_overlay": emoji_overlay,
                "mode": "speaking" if auto_open else "idle",
                "pending_summon": summon_payload,
            },
        )
        return {
            "schema": "ellmos.talk.summon.v1",
            "accepted": True,
            "delivery": delivery,
            "summon": summon_payload,
            "sentences": self.cortex.stream_sentences(summon_payload["message"]),
            "visual_state": self.state.as_dict(),
        }

    def acknowledge_summon(self, *, start_listening: bool = True) -> dict[str, Any]:
        """Accept or clear a pending model summon from the Funkgerät button or companion window."""
        prev = self.state.pending_summon
        next_mode = "listening" if start_listening else "idle"
        self.state = apply_talk_directive(
            self.state,
            {
                "pending_summon": None,
                "mode": next_mode,
            },
        )
        return {
            "schema": "ellmos.talk.summon-ack.v1",
            "acknowledged": prev,
            "visual_state": self.state.as_dict(),
        }

    def preview_reflex(
        self,
        user_utterance: str,
        *,
        persona: str | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Sub-250ms Stage-1 FastReflexLoop backchannel & visualizer transition prior to DeepCortex completion."""
        patch: dict[str, Any] = {}
        if persona and persona.strip().lower() in VALID_PERSONAS:
            patch["persona"] = persona.strip().lower()
        if language and language.strip().lower() in ("de", "en", "es", "fr", "zh", "ja", "ru", "ar", "pt", "hi", "it"):
            patch["language"] = language.strip().lower()
        if patch:
            self.update_visual_state(patch)
        decision = self.reflex.evaluate_utterance(
            user_utterance,
            current_mode=self.state.mode,
            language=self.state.language,
            wake_word=self.state.wake_word,
            wake_word_enabled=self.state.wake_word_enabled,
        )
        next_mode = "listening" if decision.action in ("barge_in", "wake_triggered") else "thinking"
        next_pattern = "pulse" if decision.action in ("barge_in", "wake_triggered") else "wave"
        self.state = apply_talk_directive(
            self.state,
            {
                "mode": next_mode,
                "emotion": decision.emotion_hint,
                "pattern": next_pattern,
                "pending_summon": None,
            },
        )
        ack_text = decision.backchannel_text or ("Verstanden." if self.state.language != "en" else "Got it.")
        return {
            "schema": "ellmos.talk.reflex.v1",
            "reflex": {
                **decision.as_dict(),
                "ack_text": ack_text,
                "latency_target_ms": decision.latency_budget_ms,
                "fast_model": self.reflex.model_name,
            },
            "visual_state": self.state.as_dict(),
        }

    def process_turn(self, user_utterance: str, *, model_response: str | None = None) -> TalkTurnResult:
        decision = self.reflex.evaluate_utterance(
            user_utterance,
            current_mode=self.state.mode,
            language=self.state.language,
            wake_word=self.state.wake_word,
            wake_word_enabled=self.state.wake_word_enabled,
        )
        self.state = apply_talk_directive(self.state, {"emotion": decision.emotion_hint, "pending_summon": None})

        if decision.action in ("barge_in", "wake_triggered") and model_response is None:
            spoken = decision.backchannel_text or ""
            self.state = apply_talk_directive(self.state, {"mode": "listening", "pattern": "pulse"})
            return TalkTurnResult(
                spoken_text=spoken,
                sentence_chunks=self.cortex.stream_sentences(spoken),
                reflex=decision,
                visual_state=self.state.as_dict(),
                applied_directives=[{"mode": "listening", "pattern": "pulse", "emotion": decision.emotion_hint}],
            )

        self.state = apply_talk_directive(self.state, {"mode": "thinking"})
        raw_reply = (
            model_response
            if model_response is not None
            else self.cortex.generate_response(
                user_utterance,
                persona=self.state.persona,
                language=self.state.language,
            )
        )
        clean_text, directives = extract_talk_directives(raw_reply)
        for d in directives:
            self.state = apply_talk_directive(self.state, d)
        self.state = apply_talk_directive(self.state, {"mode": "speaking"})
        chunks = self.cortex.stream_sentences(clean_text)
        return TalkTurnResult(
            spoken_text=clean_text,
            sentence_chunks=chunks,
            reflex=decision,
            visual_state=self.state.as_dict(),
            applied_directives=directives,
        )

    def status(self) -> dict[str, Any]:
        return {
            "schema": "ellmos.talk.status.v1",
            "reflex_model": self.reflex.model_name,
            "visual_state": self.state.as_dict(),
        }
