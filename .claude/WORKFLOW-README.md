# Automated Workflow mit Stop Hooks

Dieser Workflow sorgt dafür, dass Claude automatisch durch alle Quality Gates geht, bevor ein Task als abgeschlossen gilt.

## Workflow-Phasen

```
1. Planning (idle)
   ↓
2. Building (Code schreiben + Tests schreiben)
   ↓
3. Testing (Tests ausführen)
   ↓ ← Loop zurück bei Fehlern
4. Review (Code-Analyse)
   ↓ ← Loop zurück zu Build bei Issues
5. E2E Testing (Playwright Tests)
   ↓ ← Loop zurück zu Build bei Fehlern
6. Documentation (Docs prüfen/erstellen)
   ↓
7. Commit & Push
   ↓
✓ Fertig!
```

## Wie es funktioniert

Der **Stop Hook** (`workflow-orchestrator.sh`) wird bei jedem Stop-Versuch ausgeführt:
- Prüft die aktuelle Workflow-Phase
- Führt entsprechende Checks aus
- Gibt `approve` oder `block` zurück
- Bei `block` erhält Claude die Anweisung, was noch zu tun ist

## State Management

Der Workflow-State wird gespeichert in: `.claude/workflow-state.json`

```json
{
  "phase": "building",
  "checks_passed": ["tests", "review"]
}
```

## Phasen im Detail

### 1. Building
- **Check**: Git diff - wurden Dateien geändert?
- **Block wenn**: Keine Änderungen
- **Message**: "Implementiere die geplanten Features und schreibe Tests"

### 2. Testing
- **Check**: `.claude/test-results.txt` existiert und enthält "All tests passed"
- **Block wenn**: Datei fehlt oder Tests fehlgeschlagen
- **Message**: "Führe die Tests aus und stelle sicher, dass sie erfolgreich durchlaufen"

### 3. Review
- **Check**: `.claude/review-result.txt` existiert und enthält "APPROVED"
- **Block wenn**: Datei fehlt
- **Message**: "Analysiere den Code auf Probleme. Wenn ok: erstelle review-result.txt mit 'APPROVED'"

### 4. E2E Testing
- **Check**: `.claude/e2e-results.txt` existiert und enthält "All E2E tests passed"
- **Block wenn**: Datei fehlt oder Tests fehlgeschlagen
- **Message**: "Führe Playwright Tests aus. Bei Fehlern zurück zu Build"

### 5. Documentation
- **Check**: `.claude/documentation-complete.txt` existiert (nur wenn Code-Dateien geändert wurden)
- **Block wenn**: Docs fehlen
- **Message**: "Erstelle/aktualisiere Dokumentation"

### 6. Commit & Push
- **Check**: Git status - alles committed und gepusht?
- **Block wenn**: Uncommitted changes oder nicht gepusht
- **Message**: "Erstelle Git Commit und pushe zum Repository"

## Helper Scripts

### Workflow starten
```bash
bash .claude/hooks/workflow-start.sh [phase]
```

Startet den Workflow in einer bestimmten Phase (default: `building`)

### Workflow zurücksetzen
```bash
bash .claude/hooks/workflow-reset.sh
```

Setzt den Workflow zurück auf `idle` und löscht alle State-Dateien.

### Workflow-Status prüfen
```bash
cat .claude/workflow-state.json
```

## Beispiel-Flow

1. **User**: "Implementiere ein neues Feature X"
2. **Claude plant** und beginnt zu coden
3. **Claude versucht zu stoppen**
4. **Hook blockiert**: "Führe Tests aus"
5. **Claude führt Tests aus**
6. **Claude versucht zu stoppen**
7. **Hook blockiert**: "Code Review durchführen"
8. **Claude reviewed Code, findet Issue**
9. **Claude fixt Issue**
10. **Claude versucht zu stoppen**
11. **Hook blockiert**: "Führe Tests erneut aus" (Loop)
12. ... (weitere Phasen)
13. **Hook approved**: ✓ Workflow complete!

## Logs

Workflow-Logs werden gespeichert in: `.claude/workflow.log`

```bash
tail -f .claude/workflow.log
```

## Anpassungen

Du kannst den Workflow anpassen, indem du `workflow-orchestrator.sh` editierst:
- Phasen hinzufügen/entfernen
- Checks anpassen
- Loop-Logik ändern
- Andere Tools integrieren (ESLint, Prettier, etc.)

## Deaktivieren

Um den Workflow zu deaktivieren, entferne einfach den Stop Hook aus `.claude/settings.json` oder kommentiere ihn aus.
