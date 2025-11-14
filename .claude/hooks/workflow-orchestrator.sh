#!/bin/bash

# Workflow Orchestrator - prüft bei jedem Stop, welche Phase als nächstes kommt
# und gibt decision zurück

PROJECT_ROOT="/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia"
STATE_FILE="$PROJECT_ROOT/.claude/workflow-state.json"
LOG_FILE="$PROJECT_ROOT/.claude/workflow.log"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# State initialisieren falls nicht vorhanden
if [ ! -f "$STATE_FILE" ]; then
    echo '{"phase":"idle","checks_passed":[]}' > "$STATE_FILE"
fi

# State lesen
PHASE=$(jq -r '.phase' "$STATE_FILE")
CHECKS_PASSED=$(jq -r '.checks_passed[]' "$STATE_FILE" 2>/dev/null)

log "Current phase: $PHASE"

# Workflow-Logik
case "$PHASE" in
    "idle"|"planning")
        # Nach Planning kommt Build
        echo "{\"decision\":\"approve\",\"reason\":\"Planning abgeschlossen. Workflow beginnt.\"}"
        jq '.phase = "building"' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
        ;;

    "building")
        # Prüfe ob Code geschrieben wurde (neue/geänderte Dateien)
        if git diff --quiet HEAD 2>/dev/null; then
            echo "{\"decision\":\"block\",\"reason\":\"Phase: Build & Write Tests - Es wurden noch keine Änderungen vorgenommen. Bitte implementiere die geplanten Features und schreibe Tests.\"}"
        else
            log "Build phase completed, moving to testing"
            jq '.phase = "testing"' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
            echo "{\"decision\":\"block\",\"reason\":\"Code geschrieben. Führe jetzt die Tests aus (npm test / flutter test / pytest).\"}"
        fi
        ;;

    "testing")
        # Versuche Tests zu finden und auszuführen
        log "Testing phase - checking for test execution"

        # Prüfe ob Tests existieren und erfolgreich waren (vereinfachte Prüfung)
        if [ -d "TidySnap" ]; then
            # Flutter Projekt
            TEST_RESULT_FILE="$PROJECT_ROOT/.claude/test-results.txt"
            if [ -f "$TEST_RESULT_FILE" ] && grep -q "All tests passed" "$TEST_RESULT_FILE"; then
                log "Tests passed, moving to review"
                jq '.phase = "review" | .checks_passed += ["tests"]' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
                echo "{\"decision\":\"block\",\"reason\":\"Tests erfolgreich! Jetzt Code Review durchführen und auf Probleme prüfen.\"}"
            else
                echo "{\"decision\":\"block\",\"reason\":\"Phase: Testing - Bitte führe die Tests aus und stelle sicher, dass sie erfolgreich durchlaufen. Speichere das Ergebnis in .claude/test-results.txt\"}"
            fi
        else
            echo "{\"decision\":\"block\",\"reason\":\"Phase: Testing - Führe die Tests für das Projekt aus.\"}"
        fi
        ;;

    "review")
        # Code Review Phase
        log "Review phase"
        REVIEW_FILE="$PROJECT_ROOT/.claude/review-result.txt"

        if [ -f "$REVIEW_FILE" ] && grep -q "APPROVED" "$REVIEW_FILE"; then
            log "Review passed, moving to e2e tests"
            jq '.phase = "e2e_testing" | .checks_passed += ["review"]' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
            echo "{\"decision\":\"block\",\"reason\":\"Review abgeschlossen! Jetzt Playwright E2E-Tests ausführen.\"}"
        else
            echo "{\"decision\":\"block\",\"reason\":\"Phase: Review - Analysiere den Code auf Probleme, Bugs oder Verbesserungspotential. Wenn Issues gefunden: zurück zu Build. Wenn ok: erstelle .claude/review-result.txt mit 'APPROVED'.\"}"
        fi
        ;;

    "e2e_testing")
        # Playwright Tests
        log "E2E testing phase"
        E2E_RESULT_FILE="$PROJECT_ROOT/.claude/e2e-results.txt"

        if [ -f "$E2E_RESULT_FILE" ] && grep -q "All E2E tests passed" "$E2E_RESULT_FILE"; then
            log "E2E tests passed, moving to documentation"
            jq '.phase = "documentation" | .checks_passed += ["e2e"]' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
            echo "{\"decision\":\"block\",\"reason\":\"E2E Tests erfolgreich! Jetzt Dokumentation prüfen/erstellen.\"}"
        else
            echo "{\"decision\":\"block\",\"reason\":\"Phase: E2E Testing - Führe Playwright Tests aus. Bei Fehlern zurück zu Build Phase.\"}"
        fi
        ;;

    "documentation")
        # Dokumentation prüfen
        log "Documentation phase"

        # Prüfe ob relevante Docs existieren (vereinfacht)
        CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null)
        NEEDS_DOCS=false

        for file in $CHANGED_FILES; do
            # Wenn Code-Dateien geändert wurden, prüfe auf Docs
            if [[ $file == *.dart ]] || [[ $file == *.js ]] || [[ $file == *.ts ]]; then
                NEEDS_DOCS=true
                break
            fi
        done

        if [ "$NEEDS_DOCS" = true ]; then
            DOC_FILE="$PROJECT_ROOT/.claude/documentation-complete.txt"
            if [ -f "$DOC_FILE" ]; then
                log "Documentation complete, moving to commit"
                jq '.phase = "ready_to_commit" | .checks_passed += ["documentation"]' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
                echo "{\"decision\":\"block\",\"reason\":\"Dokumentation vorhanden! Jetzt commit & push durchführen.\"}"
            else
                echo "{\"decision\":\"block\",\"reason\":\"Phase: Documentation - Code wurde geändert. Bitte erstelle/aktualisiere relevante Dokumentation (README, Code-Kommentare, etc.) und erstelle dann .claude/documentation-complete.txt\"}"
            fi
        else
            log "No documentation needed, moving to commit"
            jq '.phase = "ready_to_commit"' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
            echo "{\"decision\":\"block\",\"reason\":\"Keine Dokumentation nötig. Jetzt commit & push durchführen.\"}"
        fi
        ;;

    "ready_to_commit")
        # Prüfe ob committed und gepusht wurde
        log "Ready to commit phase"

        if git diff --quiet HEAD && [ -z "$(git status --porcelain)" ]; then
            # Alles committed
            if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/$(git branch --show-current) 2>/dev/null)" ]; then
                echo "{\"decision\":\"block\",\"reason\":\"Code committed aber nicht gepusht. Bitte 'git push' ausführen.\"}"
            else
                log "Workflow complete! Resetting state"
                echo '{"phase":"idle","checks_passed":[]}' > "$STATE_FILE"
                echo "{\"decision\":\"approve\",\"reason\":\"Workflow erfolgreich abgeschlossen! ✓ Alle Phasen durchlaufen, Code committed und gepusht.\"}"
            fi
        else
            echo "{\"decision\":\"block\",\"reason\":\"Phase: Commit & Push - Bitte erstelle einen Git Commit mit den Änderungen und pushe zum Remote Repository.\"}"
        fi
        ;;

    *)
        echo "{\"decision\":\"approve\",\"reason\":\"Workflow phase unknown, allowing stop.\"}"
        ;;
esac
