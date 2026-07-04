---
name: telegram-bot
description: Build Telegram bots using python-telegram-bot and Bot API 10.1 Rich Messages. Use this skill whenever the user mentions a Telegram bot of any kind — whether it's the whole project or a side feature like notifications, pipeline alerts, airlock approvals, status dashboards, or progress updates to themselves. Even if the user just says "send me a Telegram message when it's done" or "add a bot for monitoring", this skill applies. Always use it — the difference between a bot built with this skill and one without is immediately visible in how polished and rich the output looks.
---

# Telegram Bot Skill

Every bot you build should be beautiful out of the box. Bot API 10.1 unlocks tables, LaTeX, syntax-highlighted code, collapsible sections, spoilers, and more — rendered natively in every Telegram client. Use them. A wall of plain text is always the wrong choice when a table or a structured rich message would do.

---

## Stack — non-negotiable

```
pip install python-telegram-bot httpx telegramify-markdown
```

- **`python-telegram-bot`** — all command handling, polling, and update routing
- **`httpx`** — HTTP client for `sendRichMessage`; use sync (`httpx.post`) outside PTB handlers, async (`await client.post`) inside them. Do not use `requests` inside PTB async handlers — it blocks the event loop.
- **`telegramify-markdown`** — converts markdown strings to Telegram Rich HTML payloads

Never use aiogram, pyrogram, or raw polling loops.

Always include a `requirements.txt`:
```
python-telegram-bot==21.10
httpx>=0.27.0
telegramify-markdown>=1.2.0
```

### httpx as an alternative to requests

`httpx` is a drop-in replacement for `requests` with native async support. Use it when the bot is already running in an async context (e.g. inside a PTB handler) and you want to avoid blocking the event loop:

```
pip install httpx
```

Sync usage is identical to `requests`:
```python
import httpx

resp = httpx.post(f"{API_BASE}/sendRichMessage", json={...}, timeout=30)
data = resp.json()
```

Async usage (inside an `async def`, e.g. a PTB command handler):
```python
async with httpx.AsyncClient() as client:
    resp = await client.post(f"{API_BASE}/sendRichMessage", json={...}, timeout=30)
    data = resp.json()
```

**When to use which:**
- Sync bot / fire-and-forget alerter → `requests` (simpler, no client lifecycle)
- Async PTB handler that sends rich messages → `httpx.AsyncClient` (non-blocking)
- Mixed codebase → pick one and stay consistent; `httpx` works in both modes

---

## Four sending functions — always present in every bot

Two sync (for fire-and-forget notifiers, background threads, cron scripts) and two async (for inside PTB handlers). Include all four — you will need both pairs.

```python
import logging
import httpx
from telegramify_markdown import richify

TOKEN = "..."
API_BASE = f"https://api.telegram.org/bot{TOKEN}"
logger = logging.getLogger(__name__)


# ── Sync versions ─────────────────────────────────────────────────────────────
# Use ONLY outside PTB async handlers (standalone alerters, background threads).
# requests.post / httpx.post are synchronous — they block the asyncio event loop.

def send_rich(chat_id: int, markdown: str, extra_html: str = "") -> dict:
    """Markdown → Rich HTML → sendRichMessage. For outbound alerts."""
    base_html = richify(markdown).to_dict().get("html", "")
    resp = httpx.post(
        f"{API_BASE}/sendRichMessage",
        json={"chat_id": chat_id, "rich_message": {"html": base_html + extra_html}},
        timeout=30,
    )
    data = resp.json()
    if not data.get("ok"):
        logger.error("sendRichMessage failed: %s", data)
    return data


def send_rich_html(chat_id: int, html: str) -> dict:
    """Raw Rich HTML → sendRichMessage. For <details>, <sub>, <sup>."""
    resp = httpx.post(
        f"{API_BASE}/sendRichMessage",
        json={"chat_id": chat_id, "rich_message": {"html": html}},
        timeout=30,
    )
    data = resp.json()
    if not data.get("ok"):
        logger.error("sendRichMessage failed: %s", data)
    return data


# ── Async versions ────────────────────────────────────────────────────────────
# Use inside PTB async handlers (cmd_*, handle_callback, etc.).
# These await the HTTP call so the event loop stays free for other updates.

async def send_rich_async(chat_id: int, markdown: str, extra_html: str = "") -> dict:
    """Async markdown → Rich HTML → sendRichMessage. For use inside PTB handlers."""
    base_html = richify(markdown).to_dict().get("html", "")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE}/sendRichMessage",
            json={"chat_id": chat_id, "rich_message": {"html": base_html + extra_html}},
            timeout=30,
        )
    data = resp.json()
    if not data.get("ok"):
        logger.error("sendRichMessage failed: %s", data)
    return data


async def send_rich_html_async(chat_id: int, html: str) -> dict:
    """Async raw Rich HTML → sendRichMessage. For <details>, <sub>, <sup> inside PTB handlers."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE}/sendRichMessage",
            json={"chat_id": chat_id, "rich_message": {"html": html}},
            timeout=30,
        )
    data = resp.json()
    if not data.get("ok"):
        logger.error("sendRichMessage failed: %s", data)
    return data
```

### Which to call where

| Context | Function to use |
|---------|----------------|
| PTB command handler (`async def cmd_*`) | `await send_rich_async()` / `await send_rich_html_async()` |
| PTB callback handler (`async def handle_callback`) | `await send_rich_async()` for new messages; see editing note below |
| Standalone alerter / background thread / cron | `send_rich()` / `send_rich_html()` (sync) |
| Module-level init or startup code | sync is fine |

### Editing messages — no rich equivalent of editMessageText

`editMessageRichText` does not exist in the Bot API (returns 404). There is no way to edit an existing rich message in-place. When a callback handler needs to update the message after a button tap, send a new rich message instead, or use PTB's native `await query.edit_message_text()` with `ParseMode.HTML` for lightweight edits (bold, italic, code — no tables or headings).

---

## Rich element reference — pick what fits the bot

These are all natively rendered in Telegram. Choose the ones that make sense for what you're building.

### Headings
```markdown
# H1   ## H2   ### H3   #### H4
```

### Tables
```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| value    | value    | value    |
```
Good for: status dashboards, comparisons, leaderboards, structured data summaries.

### Math / LaTeX
```markdown
Inline: $E = mc^2$

Block:
$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$
```
`richify` converts `$...$` → `<tg-math>` and `$$...$$` → `<tg-math-block>` automatically.
In Python strings, always double-escape LaTeX: `\\int`, `\\frac`, `\\sqrt`, `\\pi`, `\\infty`.

### Syntax-highlighted code blocks
````markdown
```python
def hello():
    return "world"
```
````
Specify the language for full highlighting. Supported: python, javascript, typescript, sql, bash, json, yaml, go, rust, and more.

### Inline code
```markdown
Use `inline code` for commands, variable names, or short values.
```

### Lists — unordered with nesting
```markdown
- Top level
  - Second level
    - Third level
```

### Lists — ordered
```markdown
1. First step
2. Second step
3. Third step
```

### Text styles
```markdown
**Bold** | *Italic* | ***Bold italic*** | ~~Strikethrough~~
```

### Spoiler (tap to reveal)
```markdown
||Hidden text revealed on tap||
```
Good for: answers, sensitive values, collapsible alerts, fun easter eggs.

### Block quote
```markdown
> This appears as a styled block quote.
```

### Inline link
```markdown
[Link text](https://example.com)
```

### Divider
```markdown
---
```

### Subscript / Superscript — requires `send_rich_html_async`
```html
H<sub>2</sub>O     x<sup>2</sup> + y<sup>2</sup> = r<sup>2</sup>
```

### Collapsible section — requires `send_rich_html_async`
```html
<details>
  <summary>Click to expand</summary>
  <p>Hidden content — can contain lists, code, inline math.</p>
  <pre><code class="language-python">print("hello")</code></pre>
  <p>Inline math: <tg-math>a^2 + b^2 = c^2</tg-math></p>
</details>
```
Good for: long logs, stack traces, changelogs, verbose output you don't want to clutter the main message.

### Expandable block quote — requires `send_rich_html_async`
```html
<blockquote expandable>
  <p>Long content behind a "Show more" tap.</p>
</blockquote>
```

### Raw math tags (when building HTML manually)
```html
<tg-math>E = mc^2</tg-math>
<tg-math-block>\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}</tg-math-block>
```

### Raw table (when building HTML manually)
```html
<table>
  <tr><th>Header</th><th>Header</th></tr>
  <tr><td>Cell</td><td>Cell</td></tr>
</table>
```

---

## Bot skeleton

```python
#!/usr/bin/env python3
import logging
import httpx
from telegramify_markdown import richify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "YOUR_TOKEN_HERE"
API_BASE = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def send_rich(chat_id: int, markdown: str, extra_html: str = "") -> dict:
    base_html = richify(markdown).to_dict().get("html", "")
    resp = httpx.post(
        f"{API_BASE}/sendRichMessage",
        json={"chat_id": chat_id, "rich_message": {"html": base_html + extra_html}},
        timeout=30,
    )
    data = resp.json()
    if not data.get("ok"):
        logger.error("sendRichMessage failed: %s", data)
    return data


def send_rich_html(chat_id: int, html: str) -> dict:
    resp = httpx.post(
        f"{API_BASE}/sendRichMessage",
        json={"chat_id": chat_id, "rich_message": {"html": html}},
        timeout=30,
    )
    data = resp.json()
    if not data.get("ok"):
        logger.error("sendRichMessage failed: %s", data)
    return data


async def send_rich_async(chat_id: int, markdown: str, extra_html: str = "") -> dict:
    base_html = richify(markdown).to_dict().get("html", "")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE}/sendRichMessage",
            json={"chat_id": chat_id, "rich_message": {"html": base_html + extra_html}},
            timeout=30,
        )
    data = resp.json()
    if not data.get("ok"):
        logger.error("sendRichMessage failed: %s", data)
    return data


async def send_rich_html_async(chat_id: int, html: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE}/sendRichMessage",
            json={"chat_id": chat_id, "rich_message": {"html": html}},
            timeout=30,
        )
    data = resp.json()
    if not data.get("ok"):
        logger.error("sendRichMessage failed: %s", data)
    return data


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_rich_async(update.effective_chat.id, """\
# Bot Name

One-line description of what this bot does.

## Commands

| Command | Description |
|---------|-------------|
| /start  | Show this message |
| /status | ... |
""")


def main() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    logger.info("Bot running.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
```

---

## Bot type patterns

Read the context and pick the right architecture.

### Notification / alerting bot
Pushes messages proactively from a pipeline, cron, or event. No PTB handlers involved — sync `send_rich` is correct here.

```python
CHAT_ID = 123456789  # your personal chat ID

def notify(markdown: str) -> None:
    send_rich(CHAT_ID, markdown)
```

Use tables for structured status, code blocks for logs, `<details>` for verbose output that shouldn't clutter the alert.

### Airlock / approval bot
User triggers an action → bot shows a summary and asks for approval → you tap a button → bot proceeds.

Add `InlineKeyboardMarkup` with callback buttons (✅ Approve / ❌ Reject) and a `CallbackQueryHandler`. Call `await query.answer()` immediately at the top of the handler (before any awaits), then send the response as a new rich message with `send_rich_async`. Use `<details>` to collapse full context so the approval prompt stays clean.

### Full command bot
Interactive bot with multiple commands and possibly multiple users.

Add `ConversationHandler` for multi-step flows. `/start` always renders a rich command table. All handlers use the async sending functions.

### Side-car bot (part of a larger project)
Bot lives in its own file (`bot.py`, `notifier.py`), imported by the main app.

Export a `notify()` function (sync). If the main app is synchronous, run the bot in its own thread:

```python
import threading
threading.Thread(target=main, daemon=True).start()
```

---

## Rules

- **Always use `sendRichMessage`** — never `send_message` with `parse_mode` for structured output. Rich output looks dramatically better and supports far more elements.
- **Inside PTB async handlers, always use the `_async` variants** (`send_rich_async`, `send_rich_html_async`). Calling sync httpx/requests inside an async handler blocks the event loop and causes callback query timeouts.
- **`editMessageRichText` does not exist** (404). There is no in-place rich edit. For callback handlers that need to update content, send a new message.
- **Call `await query.answer()` immediately** at the top of every `CallbackQueryHandler` — before any network calls. Telegram's callback timeout is 10 seconds from the tap.
- **`/start` always shows a rich table** of available commands. First impression matters.
- **`<details>`, `<sub>`, `<sup>` require the `_html` variants** — `richify` escapes those tags rather than emitting them.
- **Log every failed API call** with `logger.error`. Never silently swallow errors.
- **LaTeX in Python strings**: double all backslashes (`\\int`, `\\frac`, `\\sqrt`, `\\pi`). Raw strings (`r"""..."""`) allow single backslashes.

---

## Keeping this skill up to date

Telegram ships Bot API updates regularly. This skill reflects what was tested and confirmed working as of Bot API 10.1 (June 2026), but things change — new block types get added, tag names shift, library versions move.

If you encounter anything during a build that contradicts what's written here — an API error, a tag that doesn't render, a `richify` behavior that differs from what the skill describes, a new element type that should be documented — update this file immediately before finishing the task. Don't leave it for later.

When updating:

- **Correct wrong information** in place. Don't append a note saying "this no longer works" — just fix the example or remove the element.
- **Add newly discovered elements** to the Rich element reference section with a working example.
- **Update version references** in this footer if the fix came from a Bot API changelog.
- **Keep the file under 500 lines** — if it's growing too long, move large reference examples to a `references/` subfolder and link from here.

After editing this file, commit and push the change to the repo so every future agent session starts with accurate information:

```bash
cd /Users/nikti/Documents/Projects/.agents
git add skills/telegram-bot/SKILL.md
git commit -m "update telegram-bot skill: <one line describing what changed>"
git push
```