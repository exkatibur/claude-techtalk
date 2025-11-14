# Get Notion Tasks

Rufe Tasks aus der Notion Agentic Task Datenbank ab, gefiltert nach Projekt und Status, inklusive vollständiger Content-Analyse und Bild-Download.

## Zweck

Dieser Command stellt eine umfassende Schnittstelle zur Notion API bereit und holt alle Tasks aus der konfigurierten Notion Datenbank, die:
- Dem aktuellen Projekt zugeordnet sind (via PROJECT_NAME)
- Den gewünschten Status haben (z.B. "execute" für automatische Verarbeitung)
- Vollständige Content Blocks inklusive Bilder analysiert
- Workflow-Tags aus dem Content extrahiert
- Für die Planung und Implementierung bereit sind

---

## Variables (Optional)

- **database_id**: $1 (optional, default: `NOTION_AGENTIC_TASK_TABLE_ID` aus .env)
- **status_filter**: $2 (optional, default: "execute")
- **limit**: $3 (optional, default: 10)
- **project_name**: $4 (optional, default: `PROJECT_NAME` aus .env)

**Einfache Verwendung**: Ohne Parameter nutzt Command automatisch .env Konfiguration.

---

## Voraussetzungen

### 1. Notion Integration erstellen

1. Gehe zu [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Klicke "New Integration"
3. Name: z.B. "Kassiopeia Agents"
4. Kopiere den **Internal Integration Token**

### 2. Datenbank mit Integration verbinden

1. Öffne deine Notion Datenbank
2. Klicke "..." → "Add connections"
3. Wähle deine Integration

### 3. Umgebungsvariablen in `.env` setzen

```bash
NOTION_API_KEY=secret_your_integration_token_here
NOTION_AGENTIC_TASK_TABLE_ID=1bcdbb1ec8114df1a4704704e40e1f39
PROJECT_NAME=Kassiopeia
```

---

## Erwartete Datenbank-Struktur

| Property | Type | Beschreibung | Erforderlich |
|----------|------|--------------|--------------|
| **IssueID** | Rich Text | Task Identifier (z.B. "TASK-001") | ✅ Ja |
| **Task** | Title | Kurze Zusammenfassung | ✅ Ja |
| **Project** | Rich Text | Projekt-Zuordnung (z.B. "Kassiopeia") | ✅ Ja |
| **Status** | Status | Aktueller Status ("execute", "To Do", "In Progress", "Done") | ✅ Ja |
| **Priority** | Select | Highest/High/Medium/Low/Lowest | ⚠️ Optional |

**Page Content**: Ausführliche Beschreibung mit Markdown, Code-Blocks, Bildern

**Hinweis**: Diese Struktur entspricht der aktuellen Kassiopeia Notion Database. Falls deine Database andere Property-Typen hat, muss `commands/utils/get_notion_tasks.py` entsprechend angepasst werden.

---

## Ablauf

### 1. Umgebungsvariablen prüfen
- Lese `.env` und extrahiere NOTION_API_KEY, NOTION_AGENTIC_TASK_TABLE_ID, PROJECT_NAME
- Wenn eine Variable fehlt, gib klare Fehlermeldung mit Setup-Anleitung aus

### 2. Notion API Query ausführen

**Filter-Logik**:
```json
{
  "filter": {
    "and": [
      {
        "property": "Status",
        "status": { "equals": "execute" }
      },
      {
        "property": "Project",
        "rich_text": { "contains": "Kassiopeia" }
      }
    ]
  },
  "sorts": [
    {
      "property": "Priority",
      "direction": "descending"
    },
    {
      "timestamp": "created_time",
      "direction": "ascending"
    }
  ]
}
```

**Hinweis**: Da Project ein Rich Text Field ist, verwenden wir `contains` statt `equals` für mehr Flexibilität.

**Concurrent Access Control**:
- Überspringe Tasks mit Status "In Progress" (bereits in Bearbeitung)
- Überspringe Tasks die in letzten 30 Sekunden modifiziert wurden (Race Condition)

### 3. Für jeden Task: Content Blocks parsen

**Was extrahiert wird**:
- Alle Text-Blocks (paragraph, heading, quote, etc.)
- Code-Blocks mit Syntax-Highlighting
- Bilder (werden heruntergeladen und analysiert)
- Listen (bulleted, numbered, to-do)
- Callouts, Divider, etc.

**Content zu task_prompt kombinieren**:
```
ALLE Content Blocks → Zu einem String kombiniert → task_prompt
```

### 4. Workflow-Tags aus Content extrahieren

Erkenne und parse Tags im Format `{{key: value}}`:

| Tag | Bedeutung | Beispiel |
|-----|-----------|----------|
| `{{worktree: name}}` | Target Git Worktree | `{{worktree: feature-auth}}` |
| `{{model: opus}}` | Claude Model Präferenz | `{{model: opus}}` oder `{{model: sonnet}}` |
| `{{workflow: plan}}` | Force Workflow Type | `{{workflow: plan\|build}}` |
| `{{app: appname}}` | Target App Directory | `{{app: tidysnap}}` |
| `{{prototype: type}}` | Prototype Template | `{{prototype: flutter_app}}` |

**Beispiel Task Content**:
```markdown
Implement user authentication with Supabase

{{worktree: feature-auth}}
{{model: sonnet}}
{{workflow: plan}}

Requirements:
- Email/Password login
- Google OAuth
- Session management
```

**Extrahierte Tags**:
```json
{
  "worktree": "feature-auth",
  "model": "sonnet",
  "workflow": "plan"
}
```

### 5. Bilder herunterladen und analysieren

Für jedes Bild im Content:

1. **Download**:
   ```bash
   mkdir -p /tmp/notion_images/
   curl -o /tmp/notion_images/image-{hash}.png {notion_image_url}
   ```

2. **Analysieren mit Read Tool**:
   ```markdown
   Use Read tool on /tmp/notion_images/image-{hash}.png
   ```

3. **Beschreibung generieren**:
   - Was zeigt das Bild? (UI Mockup, Diagram, Screenshot)
   - Welche Details sind wichtig? (Buttons, Colors, Layout)
   - Wie beeinflusst es die Implementation?

4. **In Task-Daten einfügen**:
   ```json
   {
     "images": [
       {
         "path": "/tmp/notion_images/login-mockup.png",
         "description": "Login screen with email field, password field, and Google SSO button. Clean minimal design with brand colors."
       }
     ]
   }
   ```

### 6. Execution Trigger erkennen

**Execution Modes**:

| Last Block Content | Trigger | Bedeutung |
|--------------------|---------|-----------|
| Normaler Content | `"execute"` | Verarbeite gesamten Task |
| `continue -` | `"continue"` | Setze vorherigen Task fort |
| Leer | `"execute"` | Default: Verarbeite Task |

**task_prompt Logik**:
- **Execute**: Alle Content Blocks kombiniert
- **Continue**: Nur Content nach `continue -`

---

## Response Format

**KRITISCH**: Gib **NUR** valides JSON zurück, keine Markdown-Blöcke, keine Erklärungen!

```json
[
  {
    "page_id": "abc123def456",
    "issue_id": "TASK-123",
    "task": "Implement user authentication",
    "project": "Kassiopeia",
    "status": "execute",
    "priority": "High",
    "content_blocks": [
      {
        "type": "paragraph",
        "paragraph": {
          "rich_text": [
            {
              "text": {
                "content": "Implement Supabase auth..."
              }
            }
          ]
        }
      },
      {
        "type": "image",
        "image": {
          "type": "external",
          "external": {
            "url": "https://notion.so/image/..."
          }
        }
      }
    ],
    "tags": {
      "worktree": "feature-auth",
      "model": "sonnet",
      "workflow": "plan"
    },
    "execution_trigger": "execute",
    "task_prompt": "Implement user authentication with Supabase\n\nRequirements:\n- Email/Password login\n- Google OAuth\n- Session management",
    "images": [
      {
        "path": "/tmp/notion_images/login-mockup-abc123.png",
        "description": "Login screen mockup showing email field, password field, Remember Me checkbox, and Google SSO button below. Clean design with Kassiopeia brand colors."
      }
    ]
  }
]
```

---

## Fehlerbehandlung

### Retry-Logik (Exponential Backoff)

Bei Notion API Fehlern:
1. **Versuch 1**: Sofort
2. **Versuch 2**: Nach 2 Sekunden
3. **Versuch 3**: Nach 4 Sekunden

**Error Types**:

| Error | Aktion |
|-------|--------|
| **401 Unauthorized** | Check NOTION_API_KEY, gib Setup-Anleitung |
| **404 Not Found** | Check NOTION_AGENTIC_TASK_TABLE_ID |
| **429 Rate Limit** | Warte 60s, dann retry |
| **Network Error** | Retry mit Exponential Backoff |
| **No Tasks Found** | Gib leeres Array zurück `[]` |

### Setup-Anleitung bei fehlenden Credentials

```markdown
❌ Notion API Key fehlt!

Setup-Schritte:
1. Gehe zu https://www.notion.so/my-integrations
2. Erstelle neue Integration "Kassiopeia Agents"
3. Kopiere Integration Token
4. Füge zu .env hinzu:
   NOTION_API_KEY=secret_...

5. Verbinde Integration mit Datenbank:
   - Öffne Datenbank in Notion
   - Klicke "..." → "Add connections"
   - Wähle "Kassiopeia Agents"

Dann erneut versuchen: /get_notion_tasks
```

---

## Verwendung in Agents

### Von task-planner Agent

```markdown
When no workflow_state exists with notion_page_id:
1. Use SlashCommand tool: /get_notion_tasks
2. Parse returned JSON
3. Filter tasks where status="execute"
4. Select task based on priority
5. Create plan from task_prompt
```

### Direkt vom User

```bash
# Einfach (nutzt .env):
/get_notion_tasks

# Mit Parametern:
/get_notion_tasks {database_id} execute 5 Kassiopeia
```

---

## Status-Workflow in Notion

Setze **Status** Field für Automation:

| Status | Bedeutung | Wann |
|--------|-----------|------|
| **To Do** | Noch nicht bereit | Initial |
| **execute** | ✅ Bereit für Agent | Wenn Task vollständig |
| **In Progress** | Wird verarbeitet | Agent setzt automatisch |
| **Done** | Abgeschlossen | Nach Fertigstellung |

**Trigger**: Ändere Status zu "execute" → Agent verarbeitet automatisch

---

## Beispiel Task in Notion

### Properties
- **IssueID**: TASK-042
- **Task**: Add photo upload with AI classification
- **Project**: Kassiopeia
- **Status**: execute
- **Priority**: High

### Page Content
```markdown
Implement photo upload feature for TidySnap app

{{worktree: feature-photo-upload}}
{{model: sonnet}}
{{workflow: plan|build}}

## Requirements
- Camera access for iOS and Android
- Upload to Supabase Storage
- AI classification using GPT-4 Vision
- Display classification results to user

## UI Mockup
[Image: login-ui-mockup.png]

## Technical Notes
- Use image_picker package for camera
- Integrate Supabase storage bucket "cleanup-photos"
- Call OpenAI API with GPT-4 Vision for classification
```

### Extrahiertes Ergebnis

```json
{
  "page_id": "abc123",
  "issue_id": "TASK-042",
  "task": "Add photo upload with AI classification",
  "project": "Kassiopeia",
  "status": "execute",
  "priority": "High",
  "tags": {
    "worktree": "feature-photo-upload",
    "model": "sonnet",
    "workflow": "plan|build"
  },
  "execution_trigger": "execute",
  "task_prompt": "Implement photo upload feature for TidySnap app...",
  "images": [
    {
      "path": "/tmp/notion_images/login-ui-mockup-abc123.png",
      "description": "Mobile UI mockup showing camera button, photo preview, and classification results display with confidence scores."
    }
  ]
}
```

---

## Python Implementation (Optional)

Falls du `/get_notion_tasks` selbst implementieren möchtest:

```python
from notion_client import Client
import os
import requests
from pathlib import Path

notion = Client(auth=os.environ["NOTION_API_KEY"])
database_id = os.environ["NOTION_AGENTIC_TASK_TABLE_ID"]
project_name = os.environ["PROJECT_NAME"]

# Query database
results = notion.databases.query(
    database_id=database_id,
    filter={
        "and": [
            {"property": "Status", "status": {"equals": "execute"}},
            {"property": "Project", "rich_text": {"contains": project_name}}
        ]
    },
    sorts=[
        {"property": "Priority", "direction": "descending"},
        {"timestamp": "created_time", "direction": "ascending"}
    ]
)

tasks = []
for page in results["results"]:
    # Get full page content
    blocks = notion.blocks.children.list(page["id"])

    # Extract tags from content
    tags = {}
    task_prompt = ""

    for block in blocks["results"]:
        # Parse text content
        if block["type"] == "paragraph":
            text = block["paragraph"]["rich_text"][0]["text"]["content"]
            task_prompt += text + "\n"

            # Extract {{tag: value}}
            import re
            tag_matches = re.findall(r'\{\{(\w+):\s*([^}]+)\}\}', text)
            for key, value in tag_matches:
                tags[key] = value.strip()

        # Download images
        elif block["type"] == "image":
            img_url = block["image"]["external"]["url"]
            img_path = f"/tmp/notion_images/{page['id']}.png"
            Path("/tmp/notion_images").mkdir(exist_ok=True)
            response = requests.get(img_url)
            with open(img_path, "wb") as f:
                f.write(response.content)

    tasks.append({
        "page_id": page["id"].replace("-", ""),
        "issue_id": page["properties"]["IssueID"]["rich_text"][0]["text"]["content"],
        "task": page["properties"]["Task"]["title"][0]["text"]["content"],
        "project": page["properties"]["Project"]["rich_text"][0]["text"]["content"],
        "status": page["properties"]["Status"]["status"]["name"],
        "priority": page["properties"]["Priority"]["select"]["name"] if page["properties"]["Priority"]["select"] else "",
        "tags": tags,
        "task_prompt": task_prompt.strip()
    })

# Output JSON only
import json
print(json.dumps(tasks, indent=2))
```

---

## Best Practices

1. **Status richtig setzen**: Nur "execute" für bereit Tasks
2. **Tags nutzen**: `{{worktree: name}}` für automatisches Branch Management
3. **Bilder hinzufügen**: UI Mockups helfen Agent enorm
4. **Detaillierte Prompts**: Mehr Context = bessere Implementation
5. **Priority setzen**: High Priority Tasks werden zuerst verarbeitet
6. **Concurrent Safety**: Nicht manuell Status ändern während Agent läuft

---

## Weiterführende Links

- [Notion API Docs](https://developers.notion.com/)
- [Python Notion SDK](https://github.com/ramnes/notion-sdk-py)
- [NOTION_INTEGRATION.md](../docs/NOTION_INTEGRATION.md)

---

**Erweiterte Version mit vollständiger Content-Analyse, Bild-Download und Workflow-Tags!** 🎉
