# Beitragsrichtlinie / Contributing Guide

## Deutsch

Vielen Dank für Ihr Interesse, zu `ellmos-talk` beizutragen!

### Wie Sie beitragen können

1. **Bug melden:** Erstellen Sie ein Issue mit dem Label `bug`
2. **Feature vorschlagen:** Erstellen Sie ein Issue mit dem Label `enhancement`
3. **Code beitragen:** Erstellen Sie einen Pull Request

### Pull Requests

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch: `git checkout -b feature/mein-feature`
3. Prüfen Sie Ihre Änderungen lokal (`pytest -ra -v` und `ruff check .`)
4. Committen Sie Ihre Änderungen: `git commit -m "Beschreibung der Änderung"`
5. Pushen Sie den Branch: `git push origin feature/mein-feature`
6. Erstellen Sie einen Pull Request

### Lizenz- und Rechtehinweise

Ohne ausdrückliche Zusatzregel gelten Pull Requests unter der MIT-Lizenz des Projekts ([LICENSE](LICENSE)).

### Code-Richtlinien

- Python: PEP 8 Stil, Typannotationen (`py.typed`, Python `>= 3.10`), keine neuen Laufzeitabhängigkeiten im Kernpaket
- Encoding: UTF-8 für alle Dateien (echte deutsche Umlaute in Endnutzerdokumenten)
- Sprache: Code und Kommentare auf Englisch; Dokumentation zweisprachig (EN/DE)
- Keine hartkodierten Benutzerpfade oder API-Keys

### Erste Schritte

Lesen Sie zuerst [README.md](README.md) (bzw. [README_de.md](README_de.md)) sowie [SKILL.md](SKILL.md) und installieren Sie die Entwicklungsumgebung über `pip install -e ".[dev]"`.

---

## English

Thank you for your interest in contributing to `ellmos-talk`!

### How to Contribute

1. **Report bugs:** Create an issue with the `bug` label
2. **Suggest features:** Create an issue with the `enhancement` label
3. **Contribute code:** Create a Pull Request

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Verify your changes locally (`pytest -ra -v` and `ruff check .`)
4. Commit your changes: `git commit -m "Description of change"`
5. Push the branch: `git push origin feature/my-feature`
6. Create a Pull Request

### Licensing and Contribution Terms

Unless stated otherwise, pull requests are understood to be submitted under the project's MIT license ([LICENSE](LICENSE)).

### Code Guidelines

- Python: PEP 8 style, type annotations (`py.typed`, Python `>= 3.10`), keep the core runtime zero-dependency
- Encoding: UTF-8 for all files
- Language: Code and comments in English; documentation bilingual (EN/DE)
- No hardcoded personal paths or API keys

### Getting Started

Start with [README.md](README.md) (or [README_de.md](README_de.md)) and [SKILL.md](SKILL.md), and install the dev dependencies via `pip install -e ".[dev]"`.
