---
name: automation-building
description: Build structured, n8n-style Python automations. This skill guides the creation of modular 'node' based pipelines, comprehensive README flow-maps, and Telegram-based error monitoring. Use this when designing complex data workflows, scrapers, or bot-driven automations to ensure they are human-readable and production-grade.
---

# Automation Skill

## What This Is & Why It Exists

This skill teaches AI agents how to structure code-based automations in a way that mirrors the visual, intuitive experience of **n8n workflows**. The goal is **familiarity without sacrificing power**: you should be able to open any automation project and instantly understand what's happening—just like opening an n8n canvas—while still getting efficient, production-ready code.

**Core Philosophy:** Organize code so humans can scan and understand the flow at a glance. Use judgment to balance clarity with efficiency. If something obviously should be combined, combine it. If it deserves its own file for clarity, separate it.

---

## Project Structure

Every automation should follow this structure:

```
my-automation/
├── README.md              # Your visual workflow map (see below)
├── main.py (or main.js)   # Orchestrates the entire workflow
├── requirements.txt       # Python dependencies (or package.json for JS)
├── .env                   # API keys and secrets
├── Dockerfile             # Docker setup (add at end for production)
├── docker-compose.yml     # If needed for multi-container setups
├── nodes/                 # Main workflow components (your "canvas")
│   ├── trigger.py
│   ├── fetch_news.py
│   ├── summarizer.py      # AI nodes use descriptive role names
│   └── post_telegram.py
└── utils/                 # Reusable helpers and tools
    ├── logger.py
    ├── telegram_error.py  # Error notifications
    └── validator.py
```

---

## Language Preference

**Primary Language: Python**

- Use Python whenever possible—it's the preferred language
- **Exception:** If JavaScript is significantly more efficient for the task, use JS with clear justification
- **Telegram bots:** ALWAYS use Python (no exceptions)
- If mixing languages in one project, clearly document why in README

---

## The `/nodes` Folder (Your Canvas)

This is where the main workflow lives. Each file should represent a **logical operation** in your automation.

**Guidelines:**
- Use **descriptive filenames** that explain what the node does (e.g., `fetch_news.py`, `filter_duplicates.py`, `post_telegram.py`)
- **No numbers** in filenames (no `01-trigger.py`, just `trigger.py`)
- **One logical operation per file** when it makes sense
- If combining operations is more efficient (e.g., small IF conditions), do it—don't create files for every tiny step
- Think: "Would separating this help me understand the workflow better?" If yes, separate. If no, combine.

**File Structure (each node file):**

```python
"""One or two lines: what this node does, and anything surprising about it."""

def execute(input_data):
    ...
    return output_data
```

**Keep it to that.** A reader who wants the input format, the output shape or
the dependency list should read the signature and the imports — those are
already in the file, and a comment restating them is one more thing that goes
stale. The full What/Input/Output/Why breakdown belongs in the README, once,
not at the top of every file.

---

## AI/LLM Nodes (Special Treatment)

When a node uses an AI model, it needs **extra clarity** because prompts and models change frequently.

**Filename Convention:** Use the AI's role as the filename
- `summarizer.py` - Summarizes articles
- `translator.py` - Translates content
- `sentiment_analyzer.py` - Analyzes sentiment
- `researcher.py` - Does research tasks

**Required Structure at Top of File:**

```python
"""One or two lines: what this AI node is for."""

# --- AI configuration: the block to edit when tuning ---
PROMPT = """Your clear, editable prompt here.
Can span multiple lines.
Be specific about what the AI should do."""

MODEL = "anthropic/claude-3.5-sonnet"  # Via OpenRouter (or direct API)
TOOLS = ["web_search", "calculator"]    # List tools if applicable, else empty list
TEMPERATURE = 0.7                       # Adjust for creativity vs consistency
MAX_TOKENS = 1000                       # Response length limit

# Any other model-specific settings go here.

# Rest of your code below...
```

**Why This Matters:** You need to quickly find and tweak prompts/models without digging through code. This config block at the top makes it instant.

---

## The README.md File (Your Visual Dashboard)

This is your **n8n canvas replacement**. Opening this file should give you the complete picture of the workflow.

**Required Sections:**

### 1. Workflow Overview
```markdown
# [Automation Name]

**Purpose:** [What this automation does in 2-3 sentences]

**Trigger:** [What starts it - cron job, webhook, manual, etc.]
```

### 2. Visual Flow Map
```markdown
## Workflow Flow

```
Trigger (every 15min)
    ↓
Fetch News (RSS + APIs)
    ↓
Summarizer (AI - Claude Sonnet)
    ↓
Filter Duplicates
    ↓
Post to Telegram
```
```

Show the **complete visual path** of data through your workflow.

### 3. Node Breakdown
```markdown
## Nodes Explained

### trigger.py
- **What:** Cron job that runs every 15 minutes
- **Input:** None (starts the workflow)
- **Output:** Timestamp and trigger signal
- **Why:** Ensures regular news updates

### fetch_news.py
- **What:** Fetches articles from 3 RSS feeds and 2 news APIs
- **Input:** None
- **Output:** Array of raw article objects
- **Tools:** feedparser, requests
- **Why:** Aggregates news from multiple sources

### summarizer.py (AI)
- **What:** Uses Claude to create 2-sentence summaries
- **Input:** Array of articles with full text
- **Output:** Articles with added 'summary' field
- **Model:** Claude 3.5 Sonnet via OpenRouter
- **Prompt:** Located in nodes/summarizer.py (easily editable)
- **Why:** Makes articles digestible for quick reading

[... continue for each node ...]
```

**Each node needs:**
- What it does
- Input format
- Output format
- Key tools/dependencies
- Why it exists in the flow

### 4. Setup Instructions
```markdown
## Setup & Run

1. Copy `.env.example` to `.env` and fill in:
   - `TELEGRAM_BOT_TOKEN` - Your bot token
   - `OPENROUTER_API_KEY` - For AI models
   - [other keys...]

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run:
   ```bash
   python main.py
   ```

4. Docker (production):
   ```bash
   docker-compose up -d
   ```
```

### 5. Quick Debugging
```markdown
## Debugging

- **Test single node:** `python nodes/summarizer.py` (each node should be runnable standalone for testing)
- **Check logs:** View `automation.log` or Telegram error bot
- **Common issues:** [List 2-3 typical problems and fixes]
```

**The Goal:** Someone (including future you) should open README.md and understand the entire automation in 2-3 minutes.

---

## Error Handling (Telegram Bot)

All errors should be sent to a Telegram bot for monitoring.

**In `.env.example`:**
```
TELEGRAM_ERROR_BOT_TOKEN=your_token_here
TELEGRAM_ERROR_CHAT_ID=your_chat_id_here
```

**In `utils/telegram_error.py`:**
```python
import os
import requests

def send_error(error_message, node_name="Unknown"):
    """Send error notification to Telegram"""
    token = os.getenv("TELEGRAM_ERROR_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ERROR_CHAT_ID")
    
    message = f"🚨 {project_name}\n📍 Node: {node_name}\n❌ Error: {error_message}"    
    # Send to Telegram
    # ... implementation
```

**Usage in nodes:**
```python
from utils.telegram_error import send_error

try:
    # your code
except Exception as e:
    send_error(str(e), node_name="fetch_news")
    raise  # Re-raise after logging
```

---

## The `main.py` File (Orchestration)

This file **sequences all the nodes** like n8n's main execution flow.

**Example Structure:**

```python
"""
MAIN WORKFLOW ORCHESTRATOR
Runs nodes in sequence, handles data flow between them
"""

from nodes import trigger, fetch_news, summarizer, post_telegram
from utils.logger import log_info, log_error
from utils.telegram_error import send_error

def run_workflow():
    try:
        # Step 1: Trigger
        log_info("Starting workflow...")
        trigger_data = trigger.execute()
        
        # Step 2: Fetch
        log_info("Fetching news...")
        articles = fetch_news.execute(trigger_data)
        
        # Step 3: AI Processing
        log_info("Summarizing articles...")
        summarized = summarizer.execute(articles)
        
        # Step 4: Output
        log_info("Posting to Telegram...")
        result = post_telegram.execute(summarized)
        
        log_info(f"Workflow complete. Posted {result['count']} articles")
        
    except Exception as e:
        log_error(f"Workflow failed: {str(e)}")
        send_error(str(e), node_name="main_workflow")

if __name__ == "__main__":
    run_workflow()
```

Keep it clean and sequential. The flow should be obvious just by reading top to bottom.

---

## Common Tools & Integrations

These are the tools you use most frequently. The AI should default to these when applicable:

### Communication
- **Telegram:** Primary bot communication + error logging
  - Use `python-telegram-bot` library
  - API tokens via `.env`

### AI/LLM Models
- **OpenRouter:** Primary model gateway (allows easy model switching)
  - Use for most AI tasks
  - Easy to swap between Claude, GPT, Gemini, etc.
- **Direct Integrations:** OpenAI, Anthropic, Gemini
  - Use when OpenRouter doesn't support needed features
- **Perplexity:** Research tasks (direct integration)
- **Tavily:** Alternative research tool

### Databases
- **Primary:** Google Sheets or Notion
  - Use when you need easy manual access
  - Good for dashboards, tracking, collaborative data
- **Simple:** SQLite
  - Use when you don't need to easily access the data manually
  - Good for logs, caches, simple key-value storage

### Other
- **Requests/aiohttp:** HTTP requests
- **Feedparser:** RSS feeds
- **Schedule/APScheduler:** Cron-like scheduling in Python

---

## Docker Setup (Production)

Every workflow should be **dockerized** for production deployment.

**Dockerfile Example:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

**docker-compose.yml Example:**

```yaml
version: '3.8'

services:
  automation:
    build: .
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

Add Docker files **at the end** after the automation is tested and working.

---

## How Much to Comment

This is the rule that keeps these projects readable, and the one most often got
wrong. Aim for **under 15% of a file being prose.** Past that the code stops
being scannable and the comments start going stale faster than they are read.

**Write a comment when:**
- The file needs a one- or two-line docstring saying what it is.
- Something is genuinely surprising — a workaround, a trap, a real incident.
  "This fails closed on purpose", "a <br> here means Telegram drops the whole
  message", "the 12h window exists because daily reports score 0.97 on cosine".
- A number was chosen for a reason a reader could not guess.

**Do not write a comment when:**
- It restates the code. `# --- Fetch the article ---` above `def fetch_article()`
  is noise, and so is a docstring listing the arguments the signature already
  shows.
- It is a banner. `# ====== SECTION ======` blocks separate nothing that a blank
  line and a function name do not separate better.
- It is a tutorial. Explaining what a decorator is, or what an API is, belongs
  in the README if anywhere.
- It is history. "This used to be X, then we tried Y" — that is what git log is
  for, unless the old approach is a trap someone would fall into again.

**A short note that earns its place beats three paragraphs.** If a rationale
genuinely needs paragraphs, that is a sign it belongs in the README or in
`docs/`, with the code carrying a one-line pointer to it.

## Key Principles Summary

1. **Visual Clarity:** Structure should mirror n8n's visual flow
2. **Descriptive Names:** Filenames explain what nodes do
3. **One Logical Operation:** Per file when it makes sense
4. **AI Nodes Are Special:** Clear config blocks at top (PROMPT, MODEL, TOOLS, etc.)
5. **README Is Your Canvas:** Complete visual map + explanations
6. **Python First:** Use Python unless JS is significantly better
7. **Error Handling:** All errors → Telegram bot
8. **Use Judgment:** Don't create files for every tiny step if combining makes sense
9. **Educational:** Future you should understand everything from README
10. **Production Ready:** Dockerize at the end

---

## Final Note to AI Agents

When building automations with this skill:

- **Understand the goal:** Help the human scan and understand workflows visually
- **Use your judgment:** These are guidelines, not rigid rules
- **Prioritize clarity:** But don't sacrifice efficiency
- **Make the README thorough:** It's the human's main reference
- **AI nodes need extra care:** Prompts change often, make them easy to find
- **Think like n8n:** Each file is a "node" the human can click into and understand

If you're unsure whether to split something into a separate file, ask yourself: "Would this help the human understand the workflow better?" If yes, split it. If it would just add complexity, keep it together.