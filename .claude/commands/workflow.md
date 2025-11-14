---
description: Run complete plan → build → test → review → document → publish → branch workflow
---

# Complete Workflow

Orchestriert den vollständigen **plan → build → test → review → document → publish → branch** Workflow für ein GitHub Issue oder eine Notion Task.

**WICHTIG**: Dieser Command instruiert Claude, die Phasen **sequenziell SELBST auszuführen**. Claude führt jede Phase direkt aus, anstatt einen Sub-Agent zu starten.

## Execution Instructions für Claude

Wenn dieser Command ausgeführt wird, führst du folgende Schritte **direkt** aus (NICHT via Sub-Agent):

1. **Input Resolution**: Hole Task aus GitHub oder Notion
2. **State Initialization**: Erstelle `state/workflow_state.json`
3. **PLAN Phase**: Launch task-planner agent via Task tool
4. **Warte auf Completion**, update state
5. **BUILD Phase**: Launch build-implementer agent via Task tool
6. **Warte auf Completion**, update state
7. **REVIEW Phase**: Launch spec-implementation-reviewer agent via Task tool
8. **Warte auf Completion**, update state
9. **DOCUMENT Phase**: Launch feature-documenter agent via Task tool
10. **Warte auf Completion**, update state
11. **PUBLISH Phase**: Launch task-feedback-publisher agent via Task tool
12. **Warte auf Completion**, update state
13. **BRANCH Phase**: Create feature branch and commit all artifacts
14. **Completion**: Report success message

Du führst diese Schritte SELBST aus, nicht ein Sub-Agent!

## Usage

```bash
# Kein Parameter: Holt ersten execute-Task aus Notion (alle Projekte)
/workflow

# GitHub Issue (nur Zahl)
/workflow 42
/workflow #42

# Notion Task ID (beliebiges Format)
/workflow TASK-001
/workflow ADW-042
/workflow feature-auth

# Resume unterbrochenen Workflow
/workflow resume
/workflow resume 42
/workflow resume TASK-001
```

**Automatische Input-Erkennung mit Smart Fallback**:

- **Kein Parameter** → Holt **ersten Task mit Status "execute"** aus Notion Database
  - Ruft `/get_notion_tasks` auf (nutzt `PROJECT_NAME` aus `.env` als Filter)
  - Nimmt ersten Task (sortiert nach Priority desc, dann Created asc)
  - Perfekt für vollautomatische Workflows

- **Beliebiger Input** (z.B. `42`, `101`, `ok5`, `TASK-001`) → **Smart Detection**:

  **1. Zuerst GitHub versuchen:**
  - Prüfe ob git repository vorhanden
  - Falls ja: Versuche `gh issue view {input}`
  - Bei Erfolg: Nutze GitHub Issue
  - Bei Fehler (Issue nicht gefunden, nicht authenticated, etc.): → Weiter zu Schritt 2

  **2. Fallback zu Notion (nur bei GitHub-Fehler):**
  - Ruft `/get_notion_tasks` auf (mit `PROJECT_NAME` Filter aus `.env`)
  - Sucht Task mit `issue_id` == Input UND `project` == `PROJECT_NAME`
  - Extrahiert `page_id` automatisch (intern, unsichtbar für User)
  - Bei Erfolg: Nutze Notion Task
  - Bei Fehler: Gib klare Fehlermeldung

  **3. Beide fehlgeschlagen:**
  - Zeige User, dass weder GitHub noch Notion den Task finden konnten

**WICHTIG**:
- ✅ GitHub hat **Priorität** wenn git repo vorhanden
- ✅ Notion ist **Fallback** nur bei GitHub-Fehlern
- ✅ Notion-Suche **nur im aktuellen Projekt** (basierend auf `PROJECT_NAME` in `.env`)
- ✅ User gibt **beliebige Task IDs** ein - System entscheidet automatisch
- ❌ **NIEMALS** 32-Zeichen Notion Page IDs vom User akzeptieren!

**Beispiele**:
- `/workflow 101` → Zuerst GitHub Issue #101, Fallback: Notion Task "101" (nur Projekt Kassiopeia)
- `/workflow ok5` → Zuerst GitHub, Fallback: Notion Task "ok5" (nur Projekt Kassiopeia)
- `/workflow TASK-001` → Zuerst GitHub, Fallback: Notion Task "TASK-001" (nur Projekt Kassiopeia)

---

## What Happens

Dieser Command orchestriert **DIREKT** alle Phasen sequenziell (ohne Sub-Agent):

### 0. Input Resolution mit Smart Fallback

**Beliebiger Input** (z.B. "101", "ok5", "TASK-001"):

**Schritt 1: GitHub zuerst versuchen**
```bash
# Check if git repo exists
if [ -d .git ]; then
  # Try to fetch GitHub issue
  gh issue view {input}

  # If success: Use GitHub Issue
  # If failure: Continue to Notion fallback
fi
```

**Schritt 2: Notion Fallback (nur bei GitHub-Fehler)**
```bash
# Query Notion mit PROJECT_NAME Filter
/get_notion_tasks

# Filter results:
# - issue_id == {input}
# - project == PROJECT_NAME (aus .env)

# If found: Extract page_id (intern)
# If not found: Error
```

**WICHTIG**: User gibt NIEMALS die 32-Zeichen Notion Page ID manuell ein!
User gibt immer nur die **lesbare Task ID** (z.B. "101", "ok5", "TASK-001") ein.

**Beispiel 1: GitHub Erfolg**
```
Input: 101
→ Check .git: Not found
→ Skip GitHub (no repo)
→ Fallback to Notion
→ /get_notion_tasks (project=Kassiopeia)
→ Find task: {"issue_id": "101", "page_id": "2a7d93...", "project": "Kassiopeia"}
→ Resolved Page ID: 2a7d931546ed800785a2d79ff48a7354 (intern)
→ Continue with Initialize Workflow State
```

**Beispiel 2: GitHub zu Notion Fallback**
```
Input: ok5
→ Check .git: Found
→ Try: gh issue view ok5
→ Error: "issue not found"
→ Fallback to Notion
→ /get_notion_tasks (project=Kassiopeia)
→ Find task: {"issue_id": "ok5", "page_id": "abc123...", "project": "Kassiopeia"}
→ Resolved Page ID: abc123... (intern)
→ Continue with Initialize Workflow State
```

**Beispiel 3: Beide fehlgeschlagen**
```
Input: FAKE-999
→ Check .git: Found
→ Try: gh issue view FAKE-999
→ Error: "issue not found"
→ Fallback to Notion
→ /get_notion_tasks (project=Kassiopeia)
→ No task with issue_id="FAKE-999" in project "Kassiopeia"
→ ERROR: Task not found in GitHub or Notion
```

### 1. Initialize Workflow State

Erstellt `state/workflow_state.json`:
```json
{
  "workflow_id": "issue-42",
  "phase": "init",
  "status": "started",
  "next_action": "plan",
  "issue_number": "42",
  "timestamp": "2025-01-15T10:30:00Z",
  "retry_count": 0,
  "max_retries": 2
}
```

### 2. Execute PLAN Phase

**Action**: Launch `task-planner` agent via Task tool

**Input**: Issue number (GitHub) oder Page ID (Notion)

**Output**:
- Creates `specs/plan-42.md`
- Updates state: `next_action: "build"`

**Progress**: 🟢 PLAN complete → Ready for BUILD

### 3. Execute BUILD Phase

**Action**: Launch `build-implementer` agent via Task tool

**Input**: Plan file from state (`specs/plan-42.md`)

**Output**:
- Implements all plan tasks
- Writes tests (unit + widget + integration)
- Runs `flutter analyze`
- Commits changes
- Updates state: `next_action: "test"`

**Progress**: 🟢 BUILD complete → Ready for TEST

### 4. Execute TEST Phase

**Action**: Launch `app-validator` agent via Task tool

**Input**: Current codebase state

**Output**:
- Runs 5 Flutter tests (analyze, unit, widget, integration, build)
- Returns JSON with test results
- Updates state: `next_action: "review"`

**On Test Failures**:
- Launch `test-failure-fixer` agent
- Retry BUILD phase
- Max retries: 3

**Progress**: 🟢 TEST complete → Ready for REVIEW

### 5. Execute REVIEW Phase

**Action**: Launch `spec-implementation-reviewer` agent via Task tool

**Input**:
- Spec file (`specs/plan-42.md`)
- Git diff vs main branch

**Output**:
- JSON with review results
- Screenshots of implementation
- Issue severity assessment

**Decision**:
- ✅ No blockers → `next_action: "document"`
- ⚠️ Blocker issues → `next_action: "fix"`

**On Blocker Issues**:
- Launch `code-issue-fixer` agent
- Retry BUILD → TEST → REVIEW loop
- Max retries: 2

**Progress**: 🟢 REVIEW complete → Ready for DOCUMENT

### 6. Execute DOCUMENT Phase

**Action**: Launch `feature-documenter` agent via Task tool

**Input**:
- Issue/ADW ID
- Spec path
- Screenshot directory

**Output**:
- Creates `app_docs/feature-42-{slug}.md`
- Copies screenshots to `app_docs/assets/`
- Updates `conditional_docs.md`
- Updates state: `next_action: "publish"`

**Progress**: 🟢 DOCUMENT complete → Ready for PUBLISH

### 7. Execute PUBLISH Phase

**Action**: Launch `task-feedback-publisher` agent via Task tool

**Input**:
- Workflow state (reads from `state/workflow_state.json`)
- Documentation file path
- Screenshot directory

**Output**:
- Posts documentation summary to GitHub Issue (if GitHub workflow)
- Uploads screenshots as embedded images in GitHub comment
- OR updates Notion Task page with documentation (if Notion workflow)
- Creates `state/task-feedback-result.json` with publish status
- Updates state: `next_action: "branch"`

**GitHub Example Output**:
- Issue comment with documentation summary
- Embedded screenshot images
- Links to full documentation and commits
- Label added: "✅ implemented"

**Notion Example Output**:
- Task status updated to "Done"
- Documentation appended to task page
- Screenshots uploaded to Notion

**On Failure**:
- If GitHub CLI not configured: Skip with warning
- If Notion API not configured: Skip with warning
- Non-blocking: Workflow continues even if publish fails

**Progress**: 🟢 PUBLISH complete → Ready for BRANCH

### 8. Execute BRANCH Phase

**Action**: Create feature branch and commit all workflow artifacts (executed directly, not via agent)

**Steps**:
1. **Create feature branch**: `git checkout -b feature/issue-{id}-{slug}`
2. **Copy screenshots to assets**: `cp review_screenshots/*.png app_docs/assets/`
3. **Stage all artifacts**: `git add app_docs/ state/`
4. **Commit with message**:
   ```
   docs: Add Issue #{id} workflow artifacts (screenshots, documentation, state)

   This commit contains all workflow artifacts from the automated implementation:
   - [Description] documentation
   - X screenshots showing the implemented feature
   - Updated workflow state marking completion

   The feature was successfully implemented, reviewed, and documented
   through the automated workflow process.

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```
5. **Push branch**: `git push -u origin feature/issue-{id}-{slug}`
6. **Update state**: `next_action: "done"`

**Output**:
- Feature branch created and pushed
- All workflow artifacts committed
- GitHub provides PR creation URL
- State updated to done

**Progress**: 🟢 BRANCH complete → Workflow DONE!

### 9. Completion

**Final State**:
```json
{
  "workflow_id": "issue-42",
  "phase": "done",
  "status": "completed",
  "next_action": "done",
  "timestamp": "2025-01-15T10:45:00Z"
}
```

**User Message**:
```
🎉 Workflow Complete for Issue #42!

✅ PLAN: specs/plan-42.md
✅ BUILD: 3 files modified, committed (abc123)
✅ TEST: 5/5 passed
✅ REVIEW: No blocker issues
✅ DOCUMENT: app_docs/feature-42-photo-upload.md
✅ PUBLISH: Posted to GitHub Issue #42
✅ BRANCH: feature/issue-42-photo-upload

Feature ist produktionsbereit! 🚀

Create PR: https://github.com/owner/repo/pull/new/feature/issue-42-photo-upload
```

---

## Workflow State Machine

```
INIT → PLAN → BUILD → TEST → REVIEW → DOCUMENT → PUBLISH → BRANCH → DONE
                ↓      ↓       ↓
                ↓      ↓    (issues?)
                ↓      ↓       ↓
                ← FIX ←────────┘
                  ↓
              (retry_count < max_retries)
                  ↓
                BUILD → TEST → REVIEW
                                 ↓
                          (approved?)
                                 ↓
                            DOCUMENT → PUBLISH → BRANCH → DONE
```

**Retry Limits**:
- PLAN: 2 retries
- BUILD: 3 retries (with test-failure-fixer)
- REVIEW: 2 retries (with code-issue-fixer)
- DOCUMENT: 1 retry
- PUBLISH: 1 retry (non-blocking, can skip on failure)
- BRANCH: 1 retry

**Escalation**: Wenn max_retries erreicht → `next_action: "escalate"` → User-Intervention

---

## Manual vs Auto Mode

### Manual Mode (Current Implementation)

Claude führt alle Phasen **direkt** aus:
- Startet Sub-Agents sequenziell via Task tool
- Wartet auf Completion jeder Phase
- Updated State Transitions nach jeder Phase
- User entscheidet nur wann `/workflow` gestartet wird

**Flow**:
```bash
You: /workflow 42

Claude: 🚀 Starting workflow...
        📋 Resolving task...
        ✅ Found GitHub Issue #42

        Phase 1: PLAN ⏳
        [Launching task-planner agent...]
        ✅ PLAN complete → specs/plan-42.md

        Phase 2: BUILD ⏳
        [Launching build-implementer agent...]
        ✅ BUILD complete

        Phase 3: REVIEW ⏳
        [Launching spec-implementation-reviewer agent...]
        ✅ REVIEW complete

        Phase 4: DOCUMENT ⏳
        [Launching feature-documenter agent...]
        ✅ DOCUMENT complete

        Phase 5: PUBLISH ⏳
        [Launching task-feedback-publisher agent...]
        ✅ PUBLISH complete → Posted to GitHub Issue #42

        Phase 6: BRANCH ⏳
        [Creating feature branch and committing artifacts...]
        ✅ BRANCH complete → feature/issue-42-description

        🎉 All phases complete!
```

### Auto Mode (Optional - mit Hooks)

Falls du Git Hooks oder Notion Webhooks einrichtest:
- Webhook triggert `/workflow` automatisch bei neuem Issue
- Workflow läuft vollständig autonom
- Du erhältst nur Notification bei Completion oder Errors

**Setup** (optional):
```bash
# .git/hooks/post-commit
#!/bin/bash
if [[ $(git log -1 --pretty=%B) =~ "Implements #([0-9]+)" ]]; then
  issue_num="${BASH_REMATCH[1]}"
  /workflow $issue_num
fi
```

---

## Resume Unterbrochenen Workflow

Falls Workflow unterbrochen wurde (Error, Abbruch, System Crash):

```bash
# State prüfen:
cat state/workflow_state.json

# Resume:
/workflow resume
# oder explizit mit Issue:
/workflow resume 42
```

**Was passiert**:
- Liest `workflow_state.json`
- Checkt `next_action` Field
- Setzt bei letzter Phase fort
- Verwendet gespeicherte `retry_count`

**Beispiel**:
```json
{
  "phase": "build",
  "status": "failed",
  "next_action": "fix",
  "retry_count": 1,
  "max_retries": 3
}
```

Resume führt aus: FIX → BUILD → TEST → REVIEW → DOCUMENT

---

## Estimated Duration

Typische Laufzeiten pro Phase:

| Phase | Dauer | Abhängig von |
|-------|-------|--------------|
| PLAN | 1-2 Min | Issue-Komplexität, Notion Images |
| BUILD | 3-5 Min | Code-Umfang, Test-Anzahl |
| TEST | 2-3 Min | Test-Suite Größe |
| REVIEW | 2-3 Min | Git Diff Size, Screenshots |
| DOCUMENT | 1-2 Min | Feature-Komplexität |
| PUBLISH | 30-60 Sek | GitHub API / Notion API |
| BRANCH | 30-60 Sek | Git Operations |
| **Total** | **~12-18 Min** | **Komplettes Feature** |

Bei Retry-Loops: +5-10 Min pro Retry

---

## Success Criteria

Ein Workflow ist erfolgreich wenn:
- ✅ Alle 7 Phasen executed ohne finale Errors
- ✅ PLAN erstellt und validiert
- ✅ BUILD implementiert alle Tasks
- ✅ TEST zeigt alle 5 Tests passed
- ✅ REVIEW findet keine Blocker-Issues
- ✅ DOCUMENT generiert vollständige Markdown-Datei
- ✅ PUBLISH postet Feedback zu GitHub/Notion (oder skip mit warning)
- ✅ BRANCH erstellt Feature-Branch mit allen Artifacts
- ✅ State file zeigt `next_action: "done"`
- ✅ User erhält klare Summary-Message mit PR-Link

**Final Message Format**:
```
🎉 Workflow Complete for Issue #42!

✅ PLAN: specs/plan-42.md
✅ BUILD: Implemented + committed (hash: abc123)
✅ TESTS: 5/5 passed
✅ REVIEW: No blocking issues
✅ DOCUMENT: app_docs/feature-42-description.md
✅ PUBLISH: Posted to GitHub Issue #42
✅ BRANCH: feature/issue-42-description

Summary:
- 3 files modified
- 15 unit tests added
- 2 widget tests added
- 1 integration test added
- Feature ready for merge!

Create PR: https://github.com/owner/repo/pull/new/feature/issue-42-description
```

---

## Error Handling

### Automatisches Error Recovery

Der Workflow hat eingebaute Recovery-Mechanismen:

**Test Failures** → `test-failure-fixer` agent
- Analysiert failing tests
- Implementiert fixes
- Retried BUILD → TEST
- Max 3 Versuche

**Review Issues** → `code-issue-fixer` agent
- Liest Review-Findings
- Implementiert fixes
- Retried BUILD → TEST → REVIEW
- Max 2 Versuche

### Escalation zu User

Bei folgenden Szenarien wird eskaliert:

**Max Retries Exhausted**:
```
❌ Workflow Failed at Phase: BUILD
Issue: #42
Attempts: 3/3

Error: flutter analyze found 5 errors in lib/features/auth/

Recommendation:
1. Check errors: flutter analyze
2. Fix manually or run: /fix
3. Resume: /workflow resume 42

State saved at: state/workflow_state.json
```

**Unrecoverable Errors**:
- Notion API auth failure
- GitHub CLI not authenticated
- Flutter SDK missing
- Supabase config invalid

**Ambiguous Requirements**:
- Spec unclear or conflicting
- Missing critical information
- Multiple valid interpretations

### Manual Intervention

Bei Escalation:

1. **Check State**:
   ```bash
   cat state/workflow_state.json
   # See: phase, status, error, retry_count
   ```

2. **Fix Issue**:
   ```bash
   # Fix manually, oder:
   /fix
   ```

3. **Resume**:
   ```bash
   /workflow resume 42
   ```

---

## Input Variants

Der Command akzeptiert **beliebige Task IDs** und nutzt intelligentes Fallback:

### Beliebige Task IDs (Smart Detection)
```bash
/workflow 101
/workflow ok5
/workflow TASK-001
/workflow #42
/workflow feature-auth-redesign
"Run workflow for 101"
"Complete ok5"
"Full cycle for TASK-001"
```

**Smart Detection mit Fallback**:
1. **GitHub zuerst**: Prüfe git repo + `gh issue view {input}`
   - Bei Erfolg: GitHub Issue nutzen
   - Bei Fehler: → Notion Fallback
2. **Notion Fallback**: `/get_notion_tasks` (mit `PROJECT_NAME` Filter)
   - Suche Task mit `issue_id` == Input UND `project` == `PROJECT_NAME`
   - Bei Erfolg: Notion Task nutzen
   - Bei Fehler: Beide Quellen fehlgeschlagen → Error

**Beispiele**:
- ✅ `101` → Zuerst GitHub #101, dann Notion "101" (Projekt Kassiopeia)
- ✅ `ok5` → Zuerst GitHub, dann Notion "ok5" (Projekt Kassiopeia)
- ✅ `TASK-001` → Zuerst GitHub, dann Notion "TASK-001" (Projekt Kassiopeia)
- ✅ `#42` → Zuerst GitHub #42, dann Notion "42" (Projekt Kassiopeia)

**Automatische Auflösung (bei Notion)**:
1. Ruft `/get_notion_tasks` auf (nutzt `PROJECT_NAME` aus `.env`)
2. Filtert Tasks: `issue_id` == Input UND `project` == `PROJECT_NAME`
3. Extrahiert `page_id` automatisch (intern, User sieht sie nicht)
4. Startet Workflow mit intern aufgelöster Page ID

### Resume
```bash
/workflow resume
/workflow resume 42
/workflow resume TASK-001
"Resume workflow for issue #42"
"Resume TASK-001"
"Continue workflow from where it stopped"
```

---

## Examples

### Example 1: Auto-Pickup (ohne Parameter)

```bash
/workflow
# Kein Parameter angegeben - holt ersten execute-Task

🔍 Querying Notion for execute-ready tasks...
📋 Found 3 tasks with status "execute"
✅ Selected: TASK-001 "Add Cleanup Motivation Widget to Dashboard" (Priority: High)

Phase 1: PLAN ⏳
✅ Created specs/plan-TASK-001.md

Phase 2: BUILD ⏳
✅ Implementation complete

Phase 3: TEST ⏳
✅ All tests passed

Phase 4: REVIEW ⏳
✅ No blocker issues

Phase 5: DOCUMENT ⏳
✅ Documentation generated

🎉 Workflow Complete!
```

**Use Case**: Perfekt für vollautomatische Workflows oder Cron-Jobs, die einfach den nächsten Task verarbeiten sollen.

### Example 2: Feature from GitHub Issue

```bash
/workflow 5
# Issue #5: "Add photo upload with AI classification"

🚀 Starting workflow for Issue #5...

Phase 1: PLAN ⏳
✅ Created specs/plan-5.md (8 tasks identified)

Phase 2: BUILD ⏳
✅ Implemented lib/features/photo/upload.dart
✅ 12 unit tests, 3 widget tests, 1 integration test
✅ flutter analyze clean
✅ Committed (hash: def456)

Phase 3: TEST ⏳
✅ 5/5 tests passed

Phase 4: REVIEW ⏳
✅ Screenshots captured
✅ No blocker issues (2 tech_debt items noted)

Phase 5: DOCUMENT ⏳
✅ Generated app_docs/feature-5-photo-upload-ai.md

🎉 Workflow Complete! Feature ready for merge.
```

### Example 3: Bug Fix with Retry

```bash
/workflow 23
# Issue #23: "Fix authentication timeout"

Phase 1: PLAN ⏳
✅ Plan created

Phase 2: BUILD ⏳
❌ flutter analyze failed (3 errors)

🔧 Auto-fixing with test-failure-fixer...
✅ Fixes applied, retrying...

Phase 2: BUILD ⏳ (Retry 1/3)
✅ Build successful

Phase 3: TEST ⏳
✅ All tests passed

Phase 4: REVIEW ⏳
⚠️ 1 blocker issue: "Missing null check in auth_provider"

🔧 Auto-fixing with code-issue-fixer...
✅ Fixes applied, retrying...

Phase 4: REVIEW ⏳ (Retry 1/2)
✅ No blocker issues

Phase 5: DOCUMENT ⏳
✅ Documentation generated

🎉 Workflow Complete!
```

### Example 4: Notion Task mit automatischer ID-Auflösung

```bash
/workflow TASK-001
# User gibt nur Task ID an!

🔍 Resolving Notion Task ID "TASK-001"...
📋 Found task: "Add Cleanup Motivation Widget to Dashboard"
📄 Page ID: 2a7d... (intern aufgelöst, User sieht diese nicht)

Phase 1: PLAN ⏳
✅ Analyzing task requirements...
✅ Created specs/plan-TASK-001.md (7 tasks identified)

Phase 2: BUILD ⏳
✅ Implemented lib/features/dashboard/widgets/motivation_card.dart
✅ Created quote service with 5 motivational quotes
✅ Integrated Supabase cleanup count query
✅ 3 unit tests, 2 widget tests
✅ Committed (hash: abc123)

Phase 3: TEST ⏳
✅ 5/5 tests passed

Phase 4: REVIEW ⏳
✅ No blocker issues

Phase 5: DOCUMENT ⏳
✅ Generated app_docs/feature-TASK-001-motivation-widget.md

🎉 Workflow Complete!
```

### Example 5: Notion Task with Images

```bash
/workflow ADW-042
# Notion Task: "Login Screen Redesign" with 2 mockup images

🔍 Resolving Notion Task ID...
📋 Found task with 2 attached images

Phase 1: PLAN ⏳
📷 Found 2 images, downloading...
📷 Analyzed: login-mockup-1.png (email/password fields)
📷 Analyzed: login-mockup-2.png (Google SSO button)
✅ Plan created with UI requirements

Phase 2: BUILD ⏳
✅ Implemented LoginScreen widget
✅ Added google_sign_in package
✅ 8 widget tests

[... continues ...]

🎉 Workflow Complete!
```

---

## Technical Details

### Sub-Agents Used

Claude startet folgende Agents sequenziell via Task tool:
- `task-planner` (PLAN phase)
- `build-implementer` (BUILD phase)
- `spec-implementation-reviewer` (REVIEW phase)
- `feature-documenter` (DOCUMENT phase)
- `task-feedback-publisher` (PUBLISH phase)

Auto-Recovery Agents (bei Bedarf):
- `test-failure-fixer` (bei Test-Fehlern)
- `code-issue-fixer` (bei Review-Issues)

**Note**: BRANCH phase wird direkt von Claude ausgeführt (keine Sub-Agent), da es simple Git-Operationen sind.

### State Management

Alle Agents lesen und schreiben `state/workflow_state.json`:
- **Sequential Access**: Ein Agent nach dem anderen
- **Atomic Updates**: State wird nur bei Phase-Completion updated
- **Retry Tracking**: `retry_count` wird bei jedem Retry inkementiert
- **Timestamp Tracking**: Jede State-Änderung wird timestamped

### Communication

Agents kommunizieren via:
- **State File**: Primäre Datenquelle für Workflow-Context
- **Plan File**: `specs/plan-{id}.md` - Shared zwischen Agents
- **Test Results**: `test-results/*.json` - Von app-validator zu test-failure-fixer
- **Review Results**: `state/review-results.json` - Von reviewer zu code-issue-fixer
- **Feedback Results**: `state/task-feedback-result.json` - Von task-feedback-publisher (publish status)

---

## Best Practices

1. **Klare Issue Descriptions**: Je detaillierter das GitHub Issue/Notion Task, desto besser der Plan
2. **Bilder hinzufügen**: UI Mockups in Notion helfen enorm
3. **Tags nutzen**: `{{worktree: name}}` für Branch Management
4. **Regelmäßig committen**: Nicht während Workflow manuell committen
5. **State nicht editieren**: Lass Agents das State File managen
6. **Bei Errors: Resume**: Nicht neu starten, sondern `/workflow resume`

---

## Troubleshooting

### "Workflow stuck at BUILD"
**Check**: `cat state/workflow_state.json` - siehe `error` field
**Fix**: Address error, dann `/workflow resume`

### "Tests failing repeatedly"
**Check**: `flutter test` manuell ausführen
**Fix**: Manuell fixen, dann `/workflow resume`

### "Agent nicht responding"
**Check**: Warte 30-60 Sekunden (Agent können länger brauchen)
**Fix**: Falls wirklich stuck, Ctrl+C, dann `/workflow resume`

### "State file corrupted"
**Backup**: `cp state/workflow_state.json state/workflow_state.json.backup`
**Fix**: Manually edit oder delete und neu starten

---

## Notes

- Command ist für **End-to-End Automation** designed
- Für **einzelne Phasen**: Nutze individuelle Agents (`task-planner`, etc.)
- Für **Quick Fixes**: Skip Workflow, nutze direkt `/fix`
- **Parallel Workflows**: Nutze verschiedene Issues, State ist per Issue getrennt
- **Interrupt Safety**: Workflow kann jederzeit mit Ctrl+C abgebrochen und resumed werden

---

**Für maximale Automatisierung: Nutze `/workflow` und lehne dich zurück!** ☕
