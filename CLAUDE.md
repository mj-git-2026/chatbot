# CLAUDE.md — System Support Chatbot

## Project Overview

A Korean-language system support chatbot that uses a RAG (Retrieval-Augmented Generation) pattern. An admin manages a Q&A knowledge base via a web UI; user questions are answered by Claude (claude-sonnet-4-6) augmented with the most relevant Q&A entries retrieved from SQLite.

**Stack:** Python · FastAPI · aiosqlite · Jinja2 · Anthropic Python SDK · Vanilla JS

---

## Repository Structure

```
chatbot/
├── app.py            # FastAPI app — all route definitions
├── database.py       # Async SQLite layer (aiosqlite)
├── rag.py            # Claude integration + RAG pipeline
├── requirements.txt  # Python dependencies
├── templates/
│   ├── chat.html     # End-user chat UI (vanilla JS + marked.js)
│   └── admin.html    # Admin Q&A management UI
├── .gitignore        # Ignores __pycache__, *.pyc, *.db, .env
└── CLAUDE.md
```

`chatbot.db` (SQLite file) is gitignored and created at startup.

---

## Running the App

```bash
pip install -r requirements.txt
ANTHROPIC_API_KEY=sk-... python app.py
```

The server starts on **port 8000**. `app.py` calls `uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)` when run directly, or use uvicorn directly:

```bash
ANTHROPIC_API_KEY=sk-... uvicorn app:app --reload
```

`ANTHROPIC_API_KEY` is **required**. The app checks for it at request time in `/api/chat/stream` and returns a user-visible error if missing — no crash at startup.

---

## Architecture

### RAG Pipeline (`rag.py`)

1. `stream_answer(question, db)` calls `db.search_qa(question, limit=8)` to retrieve up to 8 relevant Q&A pairs.
2. Retrieved pairs are formatted into a context block and injected into the Claude system prompt.
3. A streaming request is sent to Claude via `async_client.messages.stream(...)`.
4. Text tokens are yielded as they arrive.

The system prompt uses **prompt caching** (`cache_control: {"type": "ephemeral"}`) on the system message to reduce latency and cost for repeated queries against the same knowledge base snapshot.

### Streaming Transport (`app.py`)

`POST /api/chat/stream` returns a `StreamingResponse` with `media_type="text/event-stream"` (SSE). Each chunk is formatted as:

```
data: {"text": "<token>"}\n\n
```

The stream terminates with:

```
data: [DONE]\n\n
```

The `X-Accel-Buffering: no` header is set to prevent nginx from buffering the stream.

### Database Layer (`database.py`)

All methods are `async` using `aiosqlite`. A new connection is opened and closed for every operation (no connection pooling). The `Database` class is instantiated once at module level in `app.py` and shared across requests.

**Table schema:**

```sql
CREATE TABLE IF NOT EXISTS qa_pairs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category    TEXT    NOT NULL DEFAULT '일반',
    question    TEXT    NOT NULL,
    answer      TEXT    NOT NULL,
    keywords    TEXT    NOT NULL DEFAULT '',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**Search algorithm (`_search`):**
- Splits query on whitespace into terms
- For each term, does `LIKE %term%` across `question`, `answer`, and `keywords` columns
- De-duplicates by `id`
- Scores each result: question hit = +3, keywords hit = +2, answer hit = +1, exact full-query in question = +5
- Returns top `limit` results sorted by score descending

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Chat UI |
| GET | `/admin` | Admin Q&A management UI |
| POST | `/api/chat/stream` | SSE streaming chat response |
| GET | `/api/qa` | List Q&A pairs (query params: `category`, `search`) |
| POST | `/api/qa` | Create Q&A pair (status 201) |
| PUT | `/api/qa/{id}` | Update Q&A pair |
| DELETE | `/api/qa/{id}` | Delete Q&A pair |
| GET | `/api/categories` | List distinct category strings |
| GET | `/api/stats` | `{ total: int, category_count: int }` |

**QAPair schema (request body for POST/PUT):**
```json
{ "category": "일반", "question": "...", "answer": "...", "keywords": "" }
```

All validation errors return `400` with `{ "detail": "..." }`. Missing records return `404`.

---

## Frontend

Both pages are single-file self-contained HTML with inlined CSS and JS — no build step, no external frameworks.

- **chat.html**: Auto-resizing textarea, SSE stream consumer, markdown rendering via CDN-loaded `marked.js`. Enter submits; Shift+Enter inserts newline. Suggestion buttons are populated from `/api/categories`.
- **admin.html**: Full CRUD table with search (debounced 300 ms), category filter, collapsible add form, modal edit dialog, toast notifications.

All UI text is in **Korean**.

---

## Key Conventions

- **Async throughout**: Every function that touches the DB or network is `async def`. Do not introduce synchronous DB calls.
- **No auth**: The `/admin` route has no authentication. Do not assume any user identity — add auth if exposing publicly.
- **Language**: All user-visible strings (API error messages, UI copy, AI system prompt) are in Korean. Keep new user-facing text in Korean.
- **Model**: Hardcoded as `"claude-sonnet-4-6"` in `rag.py:9`. Change there to switch models.
- **No ORM**: Raw SQL via aiosqlite. Keep queries simple and parameterized (never interpolate user input into SQL strings).
- **No test suite**: There are currently no automated tests. Manual verification against the running server is the test workflow.
- **Gitignore**: `*.db` and `.env` are ignored. Never commit the SQLite database or API keys.

---

## Development Branch

All changes should be developed on branch `claude/claude-md-docs-HK0Lp` and pushed with:

```bash
git push -u origin claude/claude-md-docs-HK0Lp
```
