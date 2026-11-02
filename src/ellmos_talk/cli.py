"""CLI entrypoint for ellmos-talk."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from .engine import TalkEngine


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ellmos-talk", description="Dual-Loop Live Speech & Visual Companion CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Show current TalkEngine status and visual state")

    turn_p = sub.add_parser("turn", help="Process a user utterance through Reflex + Cortex loops")
    turn_p.add_argument("utterance", help="Spoken or typed user input")
    turn_p.add_argument("--persona", default="buddha", choices=["buddha", "gemini", "claude", "codex"])
    turn_p.add_argument("--lang", default="de", choices=["de", "en"])

    dir_p = sub.add_parser("directive", help="Apply a JSON talk_control directive")
    dir_p.add_argument("json_payload", help="JSON object with pattern/emotion/mode/emoji_overlay")

    args = parser.parse_args(argv)
    engine = TalkEngine()

    if args.cmd == "status":
        print(json.dumps(engine.status(), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "turn":
        engine.update_visual_state({"persona": args.persona, "language": args.lang})
        result = engine.process_turn(args.utterance)
        print(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "directive":
        payload = json.loads(args.json_payload)
        state = engine.update_visual_state(payload)
        print(json.dumps(state.as_dict(), indent=2, ensure_ascii=False))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
