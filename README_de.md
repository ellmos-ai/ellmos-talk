# ellmos-talk

[English](README.md) | **Deutsch**

Dual-Loop-Engine für Live-Gespräch und visuellen Begleiter im ellmos-Ökosystem (BACH, Open Ocean). Ein kleines, abhängigkeitsfreies Python-Paket mit der **Gesprächslogik**: ein schneller, regelbasierter Reflex für das Sprecherwechsel-Verhalten, ein Satz-Streaming-Adapter für ein Hauptmodell und ein vom Modell gesteuerter visueller Zustand, den ein Begleiterfenster darstellen kann.

> **Status: early (v0.1.0).** Dieses Paket enthält die Engine, das Zustandsmodell und den Direktiven-Parser. Es enthält **keine** Audioaufnahme, Spracherkennung, Sprachausgabe und auch nicht das Visualisierungsfenster selbst. Die Standardantwort der Cortex-Schleife ist ein fester Platzhalter, solange kein eigener Responder übergeben wird.

## Funktionen

1. **`FastReflexLoop`** entscheidet pro Aufruf, wie mit einer Äußerung umzugehen ist: `continue`, `barge_in`, `backchannel`, `hand_off_to_cortex` oder `wake_triggered`.
   - Er arbeitet **deterministisch und regelbasiert** (reguläre Ausdrücke und Stichwortlisten). Das Feld `model_name` (Standard `smollm2:360m`) wird nur als Bezeichnung eines schnellen Relay-Modells gespeichert; in diesem Paket wird kein Modell geladen oder aufgerufen.
   - Neue Eingabe im Modus `speaking`, ein alleinstehendes „stop / stopp / halt / warte (kurz) / wait / pause" oder das alleinstehende Weckwort (Standard `hey buddha`) führt zu Unterbrechung bzw. Wake-Reaktion mit kurzem Rückmeldetext (Deutsch oder Englisch).
   - Alle anderen Äußerungen gehen mit einem Emotionshinweis (`calm`, `curious`, `joyful`, `focused`) an den Cortex.
2. **`DeepCortexLoop`** kapselt das Hauptmodell.
   - `stream_sentences(text)` teilt eine Antwort in Satzstücke, damit eine TTS-Stufe schon mit dem ersten Satz beginnen kann.
   - `generate_response(...)` ruft einen optional übergebenen `responder(prompt, persona, language)` auf. Ohne ihn kommt eine feste Platzhalterantwort.
3. **`TalkEngine`** verbindet beides mit einem `TalkVisualState` und bietet `process_turn`, `preview_reflex`, `summon_by_model`, `acknowledge_summon`, `update_visual_state` und `status`.
4. **`<talk_control {...} />`-Direktiven** lassen das Modell den Begleiterzustand direkt im Text steuern. `extract_talk_directives(text)` entfernt sie aus dem Sprechtext und liefert das geparste JSON; `apply_talk_directive(state, directive)` prüft und übernimmt sie.

### Werte des visuellen Zustands

| Feld | Erlaubte Werte |
|---|---|
| `pattern` | `orb`, `wave`, `rings`, `constellation`, `pulse` |
| `emotion` | `calm`, `curious`, `joyful`, `focused`, `empathetic`, `alert` (setzt jeweils eine Farbpalette) |
| `mode` | `listening`, `speaking`, `thinking`, `idle`, `muted` |
| `persona` | `buddha`, `gemini`, `claude`, `codex` |
| `language` | `de`, `en`, `es`, `fr`, `zh`, `ja`, `ru`, `ar`, `pt`, `hi`, `it` |
| `operating_mode` | `ptt`, `duplex`, `wake_word`, `off` |
| `summon_policy` | `knock`, `auto_popup`, `muted` |
| `client_runtime` | `browser`, `tauri`, `mobile`, `companion` |

Weitere Felder: `emoji_overlay`, `wake_word`, `wake_word_enabled`, `speed_hz` (0,1 bis 5,0), `bound_slot`, `primary_model`, `fast_relay_model` sowie Geräte-IDs für Eingabe, Ausgabe und Kamera. Ungültige Werte lösen `ValueError` aus. `DEFAULT_TALK_MODEL_BUNDLE` ist ein reiner Datenkatalog vorgeschlagener Relay-, STT-, TTS- und VAD-/Wake-Modelle; nichts davon wird hier geladen oder ausgeführt.

Ein Modell kann über `summon_by_model(...)` eine Sitzung eröffnen: je nach `summon_policy` und Anwesenheit lautet das Ergebnis `auto_popup`, `knock` oder `suppressed`.

## Installation

Benötigt Python 3.10 oder neuer; es gibt keine Laufzeitabhängigkeiten. Aus einem Klon:

```bash
pip install -e .
# optionale Extras aus pyproject.toml
pip install -e ".[dev]"     # pytest
pip install -e ".[voice]"   # deklariert ellmos-voice-io; wird von diesem Paket noch nicht importiert
```

## Nutzung

```bash
ellmos-talk status
ellmos-talk turn "Warum schlägt der Build fehl?" --persona claude --lang de
ellmos-talk directive '{"pattern": "wave", "emotion": "curious", "mode": "thinking"}'
```

```python
from ellmos_talk import TalkEngine

engine = TalkEngine()
result = engine.process_turn(
    "Wie fange ich an?",
    model_response='<talk_control {"emotion": "joyful"} /> Fangen wir an. Öffne zuerst das Projekt.',
)
print(result.sentence_chunks)   # ['Fangen wir an.', 'Öffne zuerst das Projekt.']
print(result.visual_state["emotion"])
```

Die Tests liegen in `tests/test_talk_engine.py` (Aufruf mit `pytest`).

## Bezug zu ellmos und Open Ocean

`ellmos-talk` gehört zu den Erweiterungsmodulen in der Modulzuordnung von [Open Ocean](https://github.com/ellmos-ai/open-ocean). Es ist dafür gedacht, mit [ellmos-voice-io](https://github.com/ellmos-ai/ellmos-voice-io) für Spracheingabe und -ausgabe kombiniert zu werden; diese Anbindung ist noch nicht Teil dieses Repositories. Die Modul-Metadaten stehen in `ellmos-module.v2.json`.

## Lizenz

MIT, wie in `pyproject.toml` angegeben.
