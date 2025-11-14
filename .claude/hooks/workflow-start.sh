#!/bin/bash

# Workflow starten (z.B. nach Planning Phase)

PROJECT_ROOT="/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia"
STATE_FILE="$PROJECT_ROOT/.claude/workflow-state.json"
LOG_FILE="$PROJECT_ROOT/.claude/workflow.log"

PHASE="${1:-building}"

echo "{\"phase\":\"$PHASE\",\"checks_passed\":[]}" > "$STATE_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Workflow gestartet in Phase: $PHASE" >> "$LOG_FILE"

echo "Workflow gestartet in Phase: $PHASE"
echo "Der Stop Hook wird jetzt bei jedem Stop die nächste Phase prüfen."
