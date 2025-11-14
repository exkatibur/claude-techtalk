#!/bin/bash

# Workflow zurücksetzen

PROJECT_ROOT="/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia"
STATE_FILE="$PROJECT_ROOT/.claude/workflow-state.json"

echo '{"phase":"idle","checks_passed":[]}' > "$STATE_FILE"
rm -f "$PROJECT_ROOT/.claude/test-results.txt"
rm -f "$PROJECT_ROOT/.claude/review-result.txt"
rm -f "$PROJECT_ROOT/.claude/e2e-results.txt"
rm -f "$PROJECT_ROOT/.claude/documentation-complete.txt"

echo "Workflow zurückgesetzt auf 'idle' Phase"
