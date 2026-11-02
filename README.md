# ellmos-talk

Dual-Loop Live-Gesprächs- und Visualisierungs-Engine für BACH & Open-Ocean (`OCEAN-TALK-01`, BACH `#3764` / Ocean `#534`).

## Architektur: Dual-Loop (Reflex + Cortex)

1. **Fast Reflex Loop (`FastReflexLoop`, < 250 ms):**
   - Leichtgewichtiger lokaler Turn-Taking-, Barge-In- und Backchannel-Controller (`SmolLM2-360M` / `Qwen2.5-0.5B` oder deterministischer lokaler Reflex-Klassifikator).
   - Erkennt sofort Unterbrechungen (*Barge-in*), Satzenden und Rückmeldesignale.
2. **Deep Cortex Loop (`DeepCortexLoop`):**
   - Verbindet das gewählte Hauptmodell (**Buddha**, **Gemini**, **Claude**, **Codex**) per Satz-Streaming (`stream_sentences`) mit `ellmos-voice-io`, sodass bereits der erste gesprochene Satz vertont wird, während das Hauptmodell weiterdenkt.
3. **Modellgesteuertes Visualisierungsfenster (`talk_control`):**
   - Das Modell steuert über `<talk_control {...} />` oder den MCP-/API-Kanal das eigene Companion-Fenster (`/talk`):
     - `pattern`: `orb | wave | rings | constellation | pulse`
     - `emotion`: `calm | curious | joyful | focused | empathetic | alert` (automatischer Farbwechsel)
     - `emoji_overlay`: z. B. `✨`, `🤔`, `🧘`
     - `mode`: `listening | speaking | thinking | idle | muted`
     - `language`: `de | en` (erweiterbar)
