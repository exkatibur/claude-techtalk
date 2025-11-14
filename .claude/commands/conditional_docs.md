# Conditional Documentation Guide

Dieser Guide hilft dir zu entscheiden, welche Dokumentation du basierend auf deiner aktuellen Aufgabe lesen solltest. Überprüfe die Bedingungen unten und lies nur relevante Dokumentation, bevor du mit der Aufgabe beginnst.

## Instructions

- Überprüfe die Aufgabe, die du durchführen sollst
- Gehe durch jeden Dokumentationspfad in der "Conditional Documentation" Sektion
- Für jeden Pfad: Prüfe ob eine der Bedingungen auf deine Aufgabe zutrifft
  - **WICHTIG**: Lies die Dokumentation NUR wenn mindestens eine Bedingung zutrifft
- **WICHTIG**: Lies nicht exzessiv Dokumentation. Nur lesen wenn relevant für die Aufgabe!

---

## Conditional Documentation

### CLAUDE.md
- **Pfad**: `/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia/CLAUDE.md`
- **Bedingungen**:
  - Wenn du zum ersten Mal mit dem Kassiopeia Projekt arbeitest
  - Wenn du die Projekt-Vision und Ziele verstehen musst
  - Wenn du wissen willst welcher Tech Stack verwendet wird (Flutter, Supabase, Riverpod)
  - Wenn du die Entwicklungsansätze und Konventionen lernen musst
  - Wenn du verstehen willst was TidySnap ist und welche Helper-Apps geplant sind

---

### README.md (Flutter Projekt)
- **Pfad**: `/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia/TidySnap/README.md` oder `tidy-snap-flutter/README.md`
- **Bedingungen**:
  - Wenn du an irgendetwas unter `TidySnap/` oder `tidy-snap-flutter/` arbeitest
  - Wenn du die Flutter Projektstruktur verstehen musst
  - Wenn du lernen willst wie man die App startet oder stoppt
  - Wenn du Setup-Instruktionen für Flutter/Supabase brauchst
  - Wenn du die Feature-Organisation verstehen musst (Clean Architecture)

---

### Ziel.md / Kurzfassung.md / plot.md
- **Pfad**: `/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia/Ziel.md` (und verwandte)
- **Bedingungen**:
  - Wenn du die Story-Elemente verstehen musst (Kassiopeia Charakter, Raumschiff Kapella)
  - Wenn du Content für YouTube oder Social Media erstellst
  - Wenn du Branding-Entscheidungen treffen musst (Bezug zur Story)
  - Wenn du verstehen willst wie Story und Technologie miteinander verbunden sind
  - Wenn du die langfristige Vision (5-10 Jahre) des Projekts brauchst

---

### docs/AGENTS_SETUP_COMPLETE.md
- **Pfad**: `/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia/docs/AGENTS_SETUP_COMPLETE.md`
- **Bedingungen**:
  - Wenn du mit Claude Code Agents arbeitest
  - Wenn du neue Agents erstellen oder anpassen willst
  - Wenn du den Workflow (plan → build → test → review → doc) verstehen musst
  - Wenn du wissen willst welche Commands verfügbar sind
  - Wenn du Troubleshooting für Agent-Probleme brauchst

---

### docs/NOTION_INTEGRATION.md
- **Pfad**: `/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia/docs/NOTION_INTEGRATION.md`
- **Bedingungen**:
  - Wenn du Tasks aus Notion in den Workflow einbinden willst
  - Wenn du `/get_notion_tasks` Command verwendest
  - Wenn du Notion Datenbank-Struktur verstehen musst
  - Wenn du Workflow-Tags (`{{worktree: name}}`) verwenden willst
  - Wenn du Image-Analyse aus Notion Tasks brauchst
  - Wenn du Troubleshooting für Notion API Fehler brauchst

---

### docs/WORKFLOW_QUICK_START.md
- **Pfad**: `/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia/docs/WORKFLOW_QUICK_START.md`
- **Bedingungen**:
  - Wenn du den `/workflow` Command zum ersten Mal verwendest
  - Wenn du verstehen willst wie man vollständige Workflows ausführt
  - Wenn du wissen willst wie man Workflows resumed nach Fehlern
  - Wenn du Troubleshooting für Workflow-Probleme brauchst
  - Wenn du Beispiele für erfolgreiche Workflow-Runs sehen willst

---

## Feature-Dokumentation (app_docs/)

**Hinweis**: Feature-Dokumentation wird durch den `feature-documenter` Agent automatisch hinzugefügt.

---

### Feature 3: Cleanup Motivation Widget

- **Pfad**: `app_docs/feature-3-cleanup-motivation-widget.md`
- **Bedingungen**:
  - Wenn du am Dashboard arbeitest
  - Wenn du motivationale Features oder User Engagement implementierst
  - Wenn du Riverpod Provider für Dashboard-Widgets erstellst
  - Wenn du Supabase Queries für tägliche Statistiken schreibst
  - Wenn du deutsche Sprach-Features implementierst
  - Wenn du Code in `lib/features/dashboard/` änderst
  - Wenn du AnimatedSwitcher oder Quote-Rotations-Logic implementierst
  - Wenn du Fehler siehst wie "daily cleanup count error" oder "quote service error"
- **Keywords**: dashboard, motivation, widget, quote, zitat, cleanup, stats, statistik, daily count, tägliche anzahl, riverpod provider, supabase query, animation, tap interaction, german language, deutsch, motivational messages, user engagement

---

### Beispiel: Feature Authentication (Template - nicht existent)

- **Pfad**: `app_docs/feature-001-user-authentication.md`
- **Bedingungen**:
  - Wenn du an Login/Registration Features arbeitest
  - Wenn du Supabase Auth integrieren musst
  - Wenn du Authentication Flows implementierst oder debuggst
  - Wenn du Code in `lib/features/auth/` änderst
  - Wenn du mit Authentication Providern (Riverpod) arbeitest
  - Wenn du Fehler siehst wie "Supabase auth error" oder "session expired"
- **Keywords**: auth, login, registration, supabase auth, session, jwt, password, riverpod provider

---

### Beispiel: Feature Photo Upload (Template - nicht existent)

- **Pfad**: `app_docs/feature-002-photo-upload.md`
- **Bedingungen**:
  - Wenn du an Photo/Image Upload Features arbeitest
  - Wenn du Kamera-Integration implementierst (image_picker package)
  - Wenn du Supabase Storage verwendest
  - Wenn du AI Bildklassifizierung hinzufügst (GPT-4 Vision)
  - Wenn du Code in `lib/features/photo/` änderst
  - Wenn du Fehler siehst wie "image upload failed" oder "storage error"
- **Keywords**: photo, image, upload, camera, storage, ai classification, gpt-4 vision, image_picker

---

### Beispiel: Feature Room Management (Template - nicht existent)

- **Pfad**: `app_docs/feature-003-room-management.md`
- **Bedingungen**:
  - Wenn du Raum-Management Features implementierst
  - Wenn du Supabase Database für Räume verwendest
  - Wenn du CRUD Operations für Räume hinzufügst
  - Wenn du Code in `lib/features/rooms/` änderst
  - Wenn du mit Room Models oder Repositories arbeitest
  - Wenn du Fehler siehst wie "database error" oder "room not found"
- **Keywords**: room, room management, crud, supabase database, repository, model

---

## TidySnap-spezifische Dokumentation

### TidySnap/TODO/*.md
- **Pfad**: `/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia/TidySnap/TODO/*.md`
- **Bedingungen**:
  - Wenn du neue Features für TidySnap planst
  - Wenn du wissen willst welche Features noch nicht implementiert sind
  - Wenn du die Roadmap für TidySnap verstehen musst
  - Wenn du an einem spezifischen TODO-Feature arbeitest (z.B. START_PHOTO_UPLOAD_AI.md)

---

### TidySnap/*_IMPLEMENTATION.md
- **Pfad**: Verschiedene Files wie `AUTHENTICATION_IMPLEMENTATION.md`, `ROOM_MANAGEMENT_FEATURE.md`, etc.
- **Bedingungen**:
  - Wenn du an dem spezifischen Feature arbeitest (z.B. Authentication)
  - Wenn du die Implementation Details verstehen musst
  - Wenn du API Endpoints für das Feature brauchst
  - Wenn du Troubleshooting für das Feature machst
  - Wenn du Code Reviews für das Feature durchführst

---

## Verwendung in Agents

### Vor der Implementation

```markdown
Before implementing feature X:
1. Use SlashCommand tool: /conditional_docs
2. Match current task keywords against documentation index
3. Read relevant documentation files from list
4. Apply learned patterns to implementation
```

### Beispiel Agent Logic

```markdown
Task: "Implement user login with Supabase"

Relevante Docs (basierend auf Keywords):
1. ✅ CLAUDE.md → Tech Stack (Supabase)
2. ✅ TidySnap/README.md → Project Structure
3. ✅ app_docs/feature-001-user-authentication.md → Authentication Patterns (falls existent)
4. ❌ app_docs/feature-002-photo-upload.md → NICHT relevant (kein Keyword-Match)
```

---

## Wartung

### Automatisches Update durch Agents

Der `feature-documenter` Agent fügt automatisch neue Einträge hinzu nach Dokumentations-Erstellung:

**Format für neue Einträge**:
```markdown
### Feature {Nummer}: {Beschreibung}

- **Pfad**: `app_docs/feature-{nummer}-{slug}.md`
- **Bedingungen**:
  - Wenn du an {Feature} arbeitest
  - Wenn du {spezifische Technologie} integrierst
  - Wenn du Code in `{directory}` änderst
  - Wenn du Fehler siehst wie "{error message}"
- **Keywords**: keyword1, keyword2, keyword3, ...
```

### Manuelles Update

Du kannst auch manuell Bedingungen verfeinern:

1. Lies bestehende Feature-Dokumentation
2. Identifiziere häufige Use Cases
3. Füge spezifische Bedingungen hinzu
4. Update Keywords für besseres Matching

---

## Best Practices

1. **Spezifisch sein**: "Beim Ändern von Riverpod Providers in auth/" statt nur "auth"
2. **Fehler-Pattern**: Typische Error Messages als Trigger hinzufügen
3. **Cross-Feature**: Wenn Feature A oft mit Feature B interagiert, gegenseitig referenzieren
4. **Sprache**: Deutsche UND englische Keywords für besseres Matching
5. **File-Level**: Spezifische Files erwähnen (z.B. "lib/features/auth/providers/auth_provider.dart")
6. **Nicht übertreiben**: Nur relevante Docs listen, nicht alles
7. **Keywords pflegen**: Regelmäßig erweitern basierend auf tatsächlichen Suchanfragen

---

## Hinweis

**Stand**: Weitgehend leer - wird automatisch gefüllt wenn Features dokumentiert werden durch `feature-documenter` Agent.

Erste Feature-Dokumentationen werden hinzugefügt sobald Features in TidySnap implementiert und dokumentiert sind.

---

**Lies nur was du brauchst, nicht mehr!** 📚
