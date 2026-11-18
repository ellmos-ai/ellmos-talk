# Security Policy / Sicherheitsrichtlinie

---

## English

### Scope & Threat Model

`ellmos-talk` is a dependency-free Python package providing the dual-loop conversation logic (`FastReflexLoop`, `DeepCortexLoop`, `TalkEngine`) and inline `<talk_control {...} />` visual state directive parser (`extract_talk_directives`, `apply_talk_directive`, `TalkVisualState`) for local AI companion runtimes (`BACH`, `Open Ocean`):

- **Local-only conversation logic (`v0.1.0`):** Core runtime uses only the Python standard library (`argparse`, `collections.abc`, `dataclasses`, `datetime`, `json`, `re`, `typing`). It performs no network requests, spawns no subprocesses, and accesses no audio/camera hardware directly.
- **Strict directive allowlists:** `apply_talk_directive()` validates `persona`, `language`, `mode`, `pattern`, `emotion`, `operating_mode`, `summon_policy`, `client_runtime`, and `speed_hz` (`[0.1, 5.0]`) against fixed allowlists and bounds, raising `ValueError` on unsupported values.
- **Directive extraction boundary:** `extract_talk_directives()` parses only JSON objects (`dict`) inside `<talk_control {...} />` tags, strips unclosed `<talk_control` fragments from spoken output, and leaves malformed JSON unparsed without executing code.
- **Caller responsibility:** Audio capture, STT/TTS backends (e.g. `ellmos-voice-io`), model responders injected via `DeepCortexLoop(responder=...)`, and visual companion rendering are provided by the host runtime, which remains responsible for OS permissions and transport security.

### Supported Versions

| Version | Supported |
|---------|-----------|
| `0.1.x` (`0.1.0`) | Yes (`main`) |
| `< 0.1.0` | No |

### Reporting a Vulnerability & Response SLAs (`INV-SLA-09` / `INV-SLA-10`)

Please **do not** report unpatched security vulnerabilities through public GitHub issues, pull requests, or discussions.

Report vulnerabilities privately via **GitHub Private Vulnerability Reporting**:
- **Advisory Portal:** <https://github.com/ellmos-ai/ellmos-talk/security/advisories/new>

Include affected version, platform, minimal reproduction steps, and impact assessment. Never include live credentials or personal transcripts in reports.

Our binding response and remediation targets (`INV-SLA-09` & `INV-SLA-10`):
- **Acknowledgement:** within **48 hours**
- **Initial triage & severity assessment:** within **5 business days**
- **Remediation SLA (patch or documented mitigation for confirmed vulnerabilities):** within **30 calendar days**

---

## Deutsch (Sicherheitsrichtlinie)

### Geltungsbereich & Bedrohungsmodell

`ellmos-talk` ist ein abhängigkeitsfreies Python-Paket für die Dual-Loop-Gesprächslogik (`FastReflexLoop`, `DeepCortexLoop`, `TalkEngine`) sowie den Inline-Parser für visuelle `<talk_control {...} />`-Direktiven (`extract_talk_directives`, `apply_talk_directive`, `TalkVisualState`) in lokalen KI-Begleiter-Laufzeiten (`BACH`, `Open Ocean`):

- **Rein lokale Gesprächslogik (`v0.1.0`):** Die Laufzeit nutzt ausschließlich die Python-Standardbibliothek (`argparse`, `collections.abc`, `dataclasses`, `datetime`, `json`, `re`, `typing`), führt keine Netzwerkaufrufe aus, startet keine Subprozesse und greift nicht direkt auf Audio- oder Kamerahardware zu.
- **Strikte Direktiven-Allowlists:** `apply_talk_directive()` prüft `persona`, `language`, `mode`, `pattern`, `emotion`, `operating_mode`, `summon_policy`, `client_runtime` und `speed_hz` (`[0.1, 5.0]`) gegen feste Allowlists bzw. Grenzen und löst bei ungültigen Werten `ValueError` aus.
- **Grenzen der Direktiven-Extraktion:** `extract_talk_directives()` übernimmt nur JSON-Objekte (`dict`) aus `<talk_control {...} />`-Tags, entfernt ungeschlossene `<talk_control`-Fragmente aus dem Sprechtext und führt bei fehlerhaftem JSON keinerlei Code aus.
- **Verantwortung der aufrufenden Umgebung:** Audioaufnahme, STT-/TTS-Backends (z. B. `ellmos-voice-io`), über `DeepCortexLoop(responder=...)` übergebene Modell-Responder und das Begleiterfenster liegen in der Verantwortung des Host-Systems inklusive OS-Berechtigungen und Transportsicherheit.

### Unterstützte Versionen

| Version | Unterstützt |
|---------|-------------|
| `0.1.x` (`0.1.0`) | Ja (`main`) |
| `< 0.1.0` | Nein |

### Sicherheitslücken melden & Reaktionsfristen (`INV-SLA-09` / `INV-SLA-10`)

Bitte melden Sie ungepatchte Sicherheitslücken **niemals** über öffentliche GitHub-Issues, Pull-Requests oder Diskussionen.

Nutzen Sie ausschließlich die vertrauliche Meldung über **GitHub Private Vulnerability Reporting**:
- **Sicherheitsmeldung einreichen:** <https://github.com/ellmos-ai/ellmos-talk/security/advisories/new>

Verbindliche Reaktions- und Behebungsziele (`INV-SLA-09` & `INV-SLA-10`):
- **Eingangsbestätigung:** innerhalb von **48 Stunden**
- **Ersteinschätzung & Schweregrad-Triage:** innerhalb von **5 Werktagen**
- **Behebungszusage (Patch oder dokumentierte Risikominderung für bestätigte Schwachstellen):** innerhalb von **30 Kalendertagen**
