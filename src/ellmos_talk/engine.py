"""Dual-Loop Live Conversation Engine (FastReflexLoop + DeepCortexLoop)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Callable

from .directives import (
    TalkVisualState,
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

        if any(tok in lower for tok in ("stop", "stopp", "halt", "warte kurz", "wait")):
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

        needs_thinking_bridge = len(text.split()) >= 10
        return ReflexDecision(
            action="hand_off_to_cortex",
            backchannel_text=lang_pack["thinking"] if needs_thinking_bridge else None,
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
        return self.state

    def process_turn(self, user_utterance: str, *, model_response: str | None = None) -> TalkTurnResult:
        decision = self.reflex.evaluate_utterance(
            user_utterance,
            current_mode=self.state.mode,
            language=self.state.language,
            wake_word=self.state.wake_word,
            wake_word_enabled=self.state.wake_word_enabled,
        )
        self.state = apply_talk_directive(self.state, {"emotion": decision.emotion_hint})

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
