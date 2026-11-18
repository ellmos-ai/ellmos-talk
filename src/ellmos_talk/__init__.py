"""ellmos-talk: Dual-loop live speech & visual companion engine."""

from .directives import (
    EMOTION_PALETTES,
    VALID_EMOTIONS,
    VALID_LANGUAGES,
    VALID_MODES,
    VALID_PATTERNS,
    TalkVisualState,
    apply_talk_directive,
    extract_talk_directives,
)
from .engine import (
    DeepCortexLoop,
    FastReflexLoop,
    ReflexDecision,
    TalkEngine,
    TalkTurnResult,
)

__all__ = [
    "EMOTION_PALETTES",
    "VALID_EMOTIONS",
    "VALID_LANGUAGES",
    "VALID_MODES",
    "VALID_PATTERNS",
    "DeepCortexLoop",
    "FastReflexLoop",
    "ReflexDecision",
    "TalkEngine",
    "TalkTurnResult",
    "TalkVisualState",
    "apply_talk_directive",
    "extract_talk_directives",
]

__version__ = "0.1.0"
