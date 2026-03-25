# TASK.md — Alex: Personal AI Operating System
## Master Build Prompt & Development Specification

**Version:** v1.0
**Date:** 24 March 2026
**Status:** Active — Engineering Handoff
**Project Name:** Antigravity / Alex
**References:** GOAL.md, PRD.md, SYSTEM_DESIGN.md, USER_FLOW.md, FEATURE_LIST.md, TECH_STACK.md, SECURITY.md, AI_INSTRUCTIONS.md

---

> **How to use this document.** This is the master instruction file for building Alex. It tells every tool — Cursor, Codex, Claude, or a human engineer — exactly where to start, what to build in each phase, which tool to use for each task, and what documentation to produce after each phase is complete. Read this document fully before writing a single line of code.

---

## Part 1 — Project Context

### What You Are Building

You are building **Alex**, a personal AI Operating System. Alex is a voice-first, text-capable intelligent assistant that connects to a user's Gmail, Google Calendar, Google Drive, and WhatsApp and allows them to manage their entire digital work life through natural conversation.

Alex can search files, send emails, send WhatsApp messages, book meetings, set reminders, transcribe meetings, generate morning briefings, and execute multi-step automations — all from a single voice or text command.

The system runs as a modular Python backend (FastAPI) with a Next.js web dashboard. The AI layer uses local open-source models (Ollama + Mistral 7B) in free mode and switches to Anthropic Claude or OpenAI in paid mode. All core features must work in free mode. Paid APIs are performance upgrades, not dependencies.

### Source of Truth Documents

Before starting any phase, read the following documents in this order:

1. `GOAL.md` — Final vision and capability list
2. `SYSTEM_DESIGN.md` — Architecture, components, data flows, API design
3. `TECH_STACK.md` — Every technology decision with rationale
4. `FEATURE_LIST.md` — All 70 features (F001–F070) with IDs, priorities, dependencies
5. `SECURITY.md` — Permission system, data handling rules, what Alex can/cannot do
6. `AI_INSTRUCTIONS.md` — System prompt, tool definitions, Alex's behavioural rules
7. `USER_FLOW.md` — All 10 user flows with step-by-step decision trees
8. `DATABASE.md` — Full schema, table definitions, relationships, indexes

### Non-Negotiable Rules for Every Phase

These rules apply to every phase, every tool, every file written:

**Rule 1 — Free mode first.** Every feature must work with local/free tools before any paid API is integrated. Do not write code that requires Claude, OpenAI, or ElevenLabs as a hard dependency. Use the AI Model Router pattern so free and paid modes are interchangeable.

**Rule 2 — Follow the schema exactly.** The database schema in `DATABASE.md` is authoritative. Do not invent new tables or change column names without updating the schema document.

**Rule 3 — Respect the permission system.** Every action that sends an external communication (email, WhatsApp, calendar invite) must pass through the permission check in `SECURITY.md § 6.2`. No external send executes without user confirmation.

**Rule 4 — Document after every phase.** After completing each phase, create the corresponding `Documentation/phase_X.md` file using the exact template in Part 3 of this document. No phase is considered complete until its documentation file exists.

**Rule 5 — Test before moving on.** Each phase has a defined acceptance test. Do not start the next phase until the current phase's acceptance test passes.

---

## Part 2 — Build Phases

The build is divided into eight phases following the dependency chain established in `FEATURE_LIST.md § 4.0`. Each phase builds on the foundation of the last. The total scope is all 51 v1.0 features (F001–F068 per `FEATURE_LIST.md § 5.1`).

---

### Phase 1 — Foundation: Repository, Infrastructure & Database

**Goal:** A clean, running project skeleton with the database schema applied, all environment variables configured, and a working health check endpoint. No AI features. No voice. Just infrastructure.

**Tool to use:** Cursor (repository setup, file scaffolding, Docker configuration)

**What to build:**

Set up the monorepo structure exactly as defined in `STRUCTURE.md § 3.0`:

```
antigravity/
├── apps/
│   ├── api/                    ← FastAPI backend
│   │   ├── app/
│   │   │   ├── api/            ← Route handlers
│   │   │   ├── core/           ← Config, auth, security
│   │   │   ├── models/         ← SQLAlchemy ORM models
│   │   │   ├── services/       ← Business logic
│   │   │   └── worker/         ← Celery tasks
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── main.py
│   └── web/                    ← Next.js dashboard
│       ├── src/
│       │   ├── app/            ← App Router pages
│       │   ├── components/     ← React components
│       │   ├── hooks/          ← Custom hooks
│       │   └── lib/            ← API client, utils
│       ├── package.json
│       └── next.config.ts
├── infra/
│   └── docker-compose.yml
├── Documentation/              ← Auto-generated phase docs go here
└── .env.example
```

Apply the complete database schema from `DATABASE.md` to Supabase. Every table listed in `DATABASE.md § 4.0` must be created with the correct columns, types, constraints, and indexes. Enable Row-Level Security on all user-scoped tables using the policies in `SECURITY.md § 3.5`.

Create the `docker-compose.yml` that starts: the FastAPI API server, the Celery worker, the Celery Beat scheduler, and Redis. All four services must come up cleanly with `docker compose up`.

Create `GET /health` endpoint that returns system status and confirms database connectivity.

Configure all environment variables listed in `TECH_STACK.md § 3.2.3` in `.env.example`. No secrets committed to the repository.

**Features covered:** F009 (partial — directory infrastructure), database schema

**Acceptance test:** `docker compose up` starts all four services without errors. `GET /health` returns `{"status": "healthy", "db": "connected"}`. Supabase schema matches `DATABASE.md` exactly.

---

### Phase 2 — Authentication & User Management

**Goal:** A working login system with JWT authentication, Supabase Auth integration, and Google OAuth. Every subsequent API endpoint is secured.

**Tool to use:** Cursor (backend auth logic) + Claude (reviewing security implementation against SECURITY.md)

**What to build:**

Implement Supabase Auth as the authentication provider as specified in `SECURITY.md § 3.1`. The JWT middleware must validate every request to every endpoint (except `GET /health`) against the Supabase public key.

Implement Google OAuth 2.0 (Authorization Code + PKCE) for Google Sign-In and to obtain the access and refresh tokens for Gmail, Calendar, Drive, and Contacts. The OAuth scopes must match exactly those listed in `SECURITY.md § 3.3`: `gmail.send`, `gmail.readonly`, `calendar.events`, `drive.readonly`, `contacts.readonly`.

Store OAuth tokens encrypted using Supabase Vault as specified in `SECURITY.md § 3.3`. No tokens in plaintext in any table column.

Build the `GET /v1/users/me` and `PATCH /v1/users/me` user profile endpoints from `API_ENDPOINTS.md § 5.2`.

Build the onboarding flow backend: the endpoint that receives OAuth grant codes, exchanges them for tokens, stores them, and marks the user as onboarded.

Implement the session management rules from `SECURITY.md § 3.4`: JWT expiry at 1 hour, refresh token at 30 days.

**Features covered:** Authentication system (prerequisite for all features)

**Acceptance test:** A POST to `/v1/auth/login` with valid Google OAuth code returns a JWT. A request to any endpoint without a JWT returns 401. A request with an expired JWT returns 401. User profile endpoint returns correct user data.

---

### Phase 3 — AI Model Router & Core Intelligence

**Goal:** A working AI Model Router that routes requests to either Ollama (free mode) or Claude/OpenAI (paid mode) transparently. The Intent Parser correctly classifies user input and maps it to tool calls. This is the brain of the entire system.

**Tool to use:** Cursor (router implementation) + Claude (writing and testing the prompt templates)

**What to build:**

Implement the AI Model Router (`apps/api/app/services/ai_router.py`) as specified in `SYSTEM_DESIGN.md § 4.2.2`. It must expose a single async interface: `generate(prompt, system, temperature, max_tokens, mode)` that works identically regardless of whether free or paid mode is active. The active mode is read from the user's preferences table on every call — hot-switching must work without a restart.

Free mode: connect to Ollama at `http://localhost:11434` using Mistral 7B Instruct (Q4_K_M). Fallback: LLaMA 3.1 8B.

Paid mode (primary): Anthropic Messages API with `claude-sonnet-4-20250514`. Paid mode (secondary fallback): OpenAI `gpt-4o`.

Implement the Intent Parser (`apps/api/app/services/intent_parser.py`) using the AI Model Router. The parser must produce the structured intent object defined in `AI_INSTRUCTIONS.md § 4.1` with the following fields: `intent_type`, `confidence`, `ambiguity_score`, `steps[]`, `entities`, `session_context_used`, `clarifying_question`.

Use the exact prompt templates from `AI_INSTRUCTIONS.md § 4.2` (single intent) and `AI_INSTRUCTIONS.md § 4.3` (multi-intent). These are not suggestions — they are the production prompts.

Implement the ambiguity detection logic from `AI_INSTRUCTIONS.md § 4.4`: when `ambiguity_score > 0.4`, return the clarifying question and halt execution. When `ambiguity_score ≤ 0.4`, proceed to tool execution.

Implement session context management: store the last five conversation turns in Redis keyed by `session:{session_id}:context` with a 30-minute TTL. Inject this context into every Intent Parser call.

Implement streaming response delivery using Server-Sent Events (SSE) for the `POST /v1/conversations/{id}/messages` endpoint so that Claude token output streams directly to the frontend.

**Features covered:** F047 (Intent Parsing), F048 (AI Model Router), F049 (Multi-Intent), F050 (Ambiguity Detection), F054 (Session Memory)

**Acceptance test:** Send `"Remind me to call Arjun tomorrow at 3 PM"` to the chat endpoint. The intent parser returns an intent object with `action: "create_reminder"`, `confidence > 0.9`, and the correct `trigger_at` timestamp. Send `"Send it to him"` with no prior context. The parser returns `ambiguity_score > 0.4` and a clarifying question. Free mode (Ollama) and paid mode (Claude) both produce valid intent objects.

---

### Phase 4 — Task & Reminder System

**Goal:** A complete task and reminder management system — the first fully end-to-end feature. Users can create, view, update, and complete tasks and reminders. Reminders deliver as push notifications at the correct time.

**Tool to use:** Cursor (task CRUD and Celery jobs) + Claude (testing edge cases in natural language task parsing)

**What to build:**

Implement all task CRUD endpoints from `API_ENDPOINTS.md § 5.3.3`: `GET /v1/tasks`, `POST /v1/tasks`, `PATCH /v1/tasks/{id}`, `DELETE /v1/tasks/{id}`, `POST /v1/reminders`, `PATCH /v1/reminders/{id}`.

Implement natural language date parsing using `chrono-node` (or Python equivalent `dateparser`) to convert expressions like "Friday at 9 AM", "next week", or "in 2 hours" into ISO 8601 timestamps in the user's timezone.

Implement the Intent Parser tool registration for `create_task` and `create_reminder` with the schemas defined in `AI_INSTRUCTIONS.md § 11.1`. Connect these tools to the Tool Routing Engine so that voice/text commands like "Remind me to follow up with Arjun on Friday" flow all the way through to task creation.

Implement the Celery Beat reminder delivery job (`reminderJob`): a scheduled job that polls the reminders table for entries where `remind_at <= NOW()` and `status = "pending"`, then dispatches push notifications via Firebase Cloud Messaging.

Implement the overdue task detection job (`overdueScanJob`): runs hourly, marks tasks where `due_at < NOW()` and `status = "pending"` as `status = "overdue"`.

**Features covered:** F032 (Task Creation), F033 (Task Status Management), F034 (Task Prioritisation), F035 (Reminder Creation), F036 (Reminder Delivery), F037 (Overdue Task Escalation), F038 (Recurring Reminder Support)

**Acceptance test:** Say "Remind me to call Arjun this Friday at 9 AM." Task appears in database with correct `due_at`. At the scheduled time, an FCM push notification fires. "Mark the Arjun task as done" updates status to `completed`. Overdue scan correctly flags a task past its due date.

---

### Phase 5 — File Search System

**Goal:** Every file in the user's Google Drive is indexed, searchable by keyword and by semantic meaning. The user can find a file by describing what it's about in plain English.

**Tool to use:** Cursor (indexing pipeline and search endpoints) + Claude (testing search quality with ambiguous queries)

**What to build:**

Implement the Google Drive file indexing pipeline (`fileIndexJob`) as specified in `FEATURE_LIST.md § F009`. The pipeline must: authenticate to Drive using the stored OAuth token, fetch file metadata via `files.list`, extract text from supported file types (PDF via `pdf-parse`, DOCX via `mammoth`, XLSX via `SheetJS`, Google Docs via export API), chunk content at 512 tokens with 50-token overlap, generate embeddings using `all-MiniLM-L6-v2`, and store results in the `files` table and pgvector column.

Schedule the `fileIndexJob` via Celery Beat to run every 15 minutes as a delta sync (only re-index files where `lastModifiedTime` has changed).

Implement the `POST /v1/files/search` endpoint from `API_ENDPOINTS.md § 5.4`. The search pipeline must: embed the query, perform cosine similarity search via pgvector, apply the recency boost (files modified in last 30 days get +0.05 score), and return the top 5 results. Apply the auto-select threshold from `FEATURE_LIST.md § F011`: if the top result score exceeds 0.75 AND the gap to second result exceeds 0.15, return only the top result. Otherwise return the ranked list.

Register the `search_files` tool with the AI Model Router using the schema in `AI_INSTRUCTIONS.md § 11.1`. Connect voice commands like "Find the Q3 report" through the intent parser to the file search endpoint.

Implement the file disambiguation flow from `USER_FLOW.md § 3.3.1`: when multiple candidates exist below the auto-select threshold, present the top 3 to the user for selection.

**Features covered:** F009 (File Directory Indexing), F010 (Keyword File Search), F011 (Semantic File Search), F012 (Real-Time File Watcher), F013 (File Disambiguation)

**Acceptance test:** Index a Google Drive with at least 20 files. Search for "the report about quarterly sales" — the correct file is returned even if it is named `Q3_Data_Final.xlsx`. A query with multiple near-matches presents a disambiguation list. A re-index request (`POST /v1/files/index`) queues the job and completes without errors.

---

### Phase 6 — Communication: Email & WhatsApp

**Goal:** Alex can send emails and WhatsApp messages on behalf of the user, with file attachments, respecting the full permission system from `SECURITY.md § 6.2`.

**Tool to use:** Cursor (email and WhatsApp adapters, contact resolution) + Claude (testing edge cases in contact resolution and confirmation flows)

**What to build:**

Implement the Contact Resolution Engine (`apps/api/app/services/contact_resolver.py`) as specified in `FEATURE_LIST.md § F023`. It must support: exact name match, fuzzy Levenshtein match (`rapidfuzz`), context-based disambiguation using conversation history, and role-based matching (`contacts.notes` field). When resolution is ambiguous (2+ matches), return the candidate list and the clarifying question template.

Implement the Email Adapter (`apps/api/app/services/email_adapter.py`): integrate the Gmail API for sending (`users.messages.send`) and reading the priority inbox (`users.messages.list` with `is:unread is:important`). Draft email subject and body using the AI Model Router with the email composition prompt template from `AI_INSTRUCTIONS.md § 6.2`.

Implement the email permission gate from `SECURITY.md § 6.2`: send emails to contacts with > 3 prior interactions auto-send (L3); contacts with ≤ 3 prior interactions show draft preview first (L2); emails with file attachments always show confirmation (L1).

Implement the WhatsApp Adapter (`apps/api/app/services/whatsapp_adapter.py`): integrate Meta WhatsApp Business Cloud API v21.0 for sending text messages and document attachments. Implement the 24-hour window check (`FEATURE_LIST.md § F023`): check `contacts.last_whatsapp_at` and route to freeform or template message accordingly.

Implement the webhook handler (`POST /v1/webhooks/whatsapp`) with HMAC-SHA256 signature verification as specified in `SECURITY.md § 5.4`.

Register `send_email` and `send_whatsapp` tools with the AI Model Router using the schemas in `AI_INSTRUCTIONS.md § 11.1`.

**Features covered:** F016 (Email Compose & Send), F017 (Email Tone Adjustment), F018 (Email with File Attachment), F019 (Email Inbox Reading), F021 (WhatsApp Message Send), F022 (WhatsApp File Send), F023 (Contact Resolution), F024 (Contact Management)

**Acceptance test:** Say "Email Arjun the Q3 report and tell him it's ready." The intent parser calls `search_files` + `send_email` in sequence. The draft email appears for confirmation (Arjun is a new contact). Confirmed — email is sent via Gmail API and logged to `sent_messages`. Say "WhatsApp Priya that the meeting is moved to 4 PM." Message is sent within the 24-hour window with casual tone. An attempt to send to Priya after the window expires shows the template/email alternative prompt.

---

### Phase 7 — Calendar & Scheduling

**Goal:** Alex can read the user's calendar, create events, check availability, detect conflicts, and send invites — all by voice or text.

**Tool to use:** Cursor (calendar adapter, availability engine) + Claude (testing scheduling logic edge cases)

**What to build:**

Implement the Calendar Adapter (`apps/api/app/services/calendar_adapter.py`): integrate Google Calendar API v3 for `events.list`, `events.insert`, `events.patch`, and `events.delete`. Cache today's events in Redis with a 5-minute TTL to avoid repeated API calls during the briefing and availability checks.

Implement the availability engine: given a date and duration, query the cached calendar events, compute free slots within the user's configured working hours, score slots by preference (avoiding back-to-back meetings), and return the top 2–3 suggestions.

Implement conflict detection (`FEATURE_LIST.md § F029`): before creating any event, check for overlapping events in the user's calendar and surface the conflict before proceeding.

Register the `get_calendar` and `create_event` tools with the AI Model Router using the schemas in `AI_INSTRUCTIONS.md § 11.1`.

Implement `GET /v1/calendar/events`, `POST /v1/calendar/events`, `PATCH /v1/calendar/events/{id}`, and `DELETE /v1/calendar/events/{id}` from `API_ENDPOINTS.md § 5.3.2`.

**Features covered:** F026 (Calendar Event Reading), F027 (Calendar Event Creation), F028 (Availability Check), F029 (Smart Time Slot Suggestion), F030 (Calendar Invite Dispatch)

**Acceptance test:** Ask "When am I free on Thursday afternoon?" — receives correct free slots from live calendar. "Book a 1-hour call with Priya next Thursday at 3 PM" — event created in Google Calendar, invite sent to Priya's email. A second attempt to book the same slot shows the conflict warning and suggests alternatives.

---

### Phase 8 — Memory, Briefing, Automation & Meeting Copilot

**Goal:** The complete Alex experience. Long-term memory persists across sessions. The morning briefing summarises the day. Multi-step automations execute and recover from failures. Meeting transcription and summaries work end-to-end.

**Tool to use:** Cursor (Celery jobs, automation engine, STT/TTS integration) + Claude (writing and testing all Claude prompt templates for briefing, meeting summary, and automation planning)

**What to build:**

Implement the Long-Term Memory system (`FEATURE_LIST.md § F055`): the `memories` table CRUD, the embedding pipeline for memory entries, the pgvector retrieval query (top 3 by cosine similarity, injected into Claude's context as Layer 2 of the system prompt from `AI_INSTRUCTIONS.md § 11.0`).

Implement the nightly memory consolidation job (`memoryConsolidationJob`): calls Claude with the day's interaction logs, generates a 3–5 sentence episodic summary, stores it in the `memories` table with `category: "episodic"`.

Implement the Morning Briefing generation job (`briefingJob`): runs at the user's configured wake time via Celery Beat, fetches data from Calendar + Tasks + Gmail priority inbox, calls Claude with the briefing composition prompt from `AI_INSTRUCTIONS.md § 6.5`, stores the result in the `briefings` table, generates TTS audio via Coqui TTS (free mode) or ElevenLabs (paid mode), and sends a push notification.

Implement the STT pipeline: integrate `faster-whisper` (free mode) as a streaming audio transcription service that receives audio chunks from the frontend WebSocket and returns real-time partial transcripts.

Implement the TTS pipeline: integrate Coqui TTS (free mode) and ElevenLabs (paid mode) with streaming audio output.

Implement the Automation Engine (`apps/api/app/services/automation_engine.py`) as specified in `SYSTEM_DESIGN.md § 4.6`: the Step Sequencer with dependency graph (topological sort), parallel execution for independent steps (`asyncio.gather`), step result passing via template variables (`{{step_N_result}}`), and partial failure recovery with retry logic (exponential backoff, max 3 attempts).

Implement the Meeting Transcription pipeline: `faster-whisper` in continuous mode (no endpointing) for real-time meeting transcription, saving chunks to the `events.transcript` field on a 5-minute rolling basis.

Implement the Meeting Summary generation: after the user stops transcription, call Claude with the full transcript using the meeting summary prompt from `AI_INSTRUCTIONS.md § 6.4`. Store structured output (key points, decisions, action items) in `events.summary` and `events.action_items`.

**Features covered:** F054 (Session Memory), F055 (Long-Term Semantic Memory), F056 (User Preference Learning), F057 (Preference Review & Correction), F058 (Contact Frequency Ranking), F060 (Morning Briefing Generation), F061 (Briefing Scheduling), F062 (Voice Briefing Delivery), F063 (Priority Inbox Summary), F065 (Multi-Step Task Execution), F066 (Execution Plan Preview), F067 (Step Dependency Resolution), F068 (Partial Failure Recovery), F040 (Meeting Audio Capture), F041 (Real-Time Meeting Transcription), F042 (Meeting Summary Generation), F043 (Action Item Extraction), F044 (Action Item to Task Conversion)

**Acceptance test:** Morning briefing generates correctly at the configured time and contains today's events, overdue tasks, and priority emails. A 5-step automation plan executes all steps in dependency order and reports completion. A failed step in a plan does not cascade — the user receives a partial completion report with retry options. Meeting transcription runs for 5 minutes and produces an accurate summary with correctly extracted action items.

---

## Part 3 — Documentation System (Mandatory After Every Phase)

After completing each phase and confirming its acceptance test passes, create the following file:

```
Documentation/
├── phase_1.md
├── phase_2.md
├── phase_3.md
├── phase_4.md
├── phase_5.md
├── phase_6.md
├── phase_7.md
└── phase_8.md
```

Each file must be created using the exact template below. No phase is marked complete without its documentation file existing and being accurate.

---

## Part 4 — Documentation Template

Every `phase_X.md` file must contain all seven sections below, in this order, with no sections omitted.

---

```markdown
# Phase [N] — [Phase Name]
**Date Completed:** [YYYY-MM-DD]
**Status:** Complete
**Features Covered:** [List Feature IDs, e.g. F032, F033, F035]

---

## 1. Phase Overview

### What This Phase Is
[2–3 sentences describing what was built in this phase and where it fits in the overall system.]

### Why It Is Important
[2–3 sentences explaining what becomes possible after this phase that was impossible before it.
What do later phases depend on this phase for?]

---

## 2. What Was Built

[List every component, service, file, endpoint, job, and integration created in this phase.]

- Component name — one-line description
- Component name — one-line description
- ...

---

## 3. File-by-File Explanation

[For every file created or significantly modified in this phase, provide the following block:]

### `path/to/filename.ext`
**Purpose:** [What role does this file play in the system?]
**What it does:** [What specifically does the code in this file accomplish? 2–4 sentences.]
**Key functions/classes:** [List the main exported functions, classes, or routes with a one-line description each.]

[Repeat this block for every file.]

---

## 4. Flow Explanation (Technical)

[Walk through the complete data flow for the primary feature built in this phase.
Use a numbered step-by-step format. Be specific about which files, functions, and services
are involved at each step.]

**Example: How a reminder is created and delivered**

1. User says "Remind me to call Arjun on Friday at 9 AM"
2. Voice is transcribed by `faster-whisper` in `stt_service.py`
3. Transcript passed to `intent_parser.py` → Claude identifies `create_reminder` intent
4. `tool_router.py` calls `tasks_service.create_reminder(title, due_at, contact_id)`
5. Record inserted into `reminders` table with `status: "pending"`
6. `reminder_job.py` (Celery Beat, runs every minute) detects `remind_at <= NOW()`
7. FCM push notification dispatched to user's device token
8. `reminders.status` updated to `"triggered"`

---

## 5. Non-Technical Explanation

[Explain this phase in plain language that a non-technical stakeholder or a new team member
with no technical background could fully understand. No code terms, no jargon.
Use an analogy if it helps.]

**Example framing:**
"Before this phase, Alex had no memory of what you needed to do. Now it works like a
personal assistant with a notepad — you tell it once, and it reminds you at exactly the
right time. You can say 'remind me on Friday morning' and it handles everything: no app
to open, no calendar to check. Alex simply tells you when the time comes."

---

## 6. Key Learnings

[Document the important technical decisions, concepts introduced, and lessons learned
during this phase. This section is for engineers who will maintain or extend this code.]

- **Concept/Decision:** [Explanation of why this approach was taken and what alternatives were considered.]
- **Concept/Decision:** [...]

---

## 7. What's Next

[2–4 sentences describing what Phase [N+1] builds on top of this phase.
What new capabilities become possible? What dependency does the next phase have on this phase?]

**Next phase:** [Phase N+1 name and one-sentence description.]
```

---

## Part 5 — Tool Assignment by Phase

The following table specifies which tool should be used for each type of task in each phase. Use the correct tool for the task type — do not use Cursor to design prompts, and do not use Claude to scaffold boilerplate files.

| Task Type | Primary Tool | Notes |
|-----------|-------------|-------|
| Repository scaffolding, file creation, boilerplate | **Cursor** | Use Cursor with `STRUCTURE.md` as the reference |
| Backend logic, service layer, API endpoints | **Cursor** | Reference `API_ENDPOINTS.md` and `DATABASE.md` exactly |
| Docker, CI/CD, infrastructure config | **Cursor** | Reference `TECH_STACK.md § 3.7` |
| Database schema, migrations, RLS policies | **Cursor** | Reference `DATABASE.md` exactly — do not deviate from schema |
| Writing and tuning AI prompt templates | **Claude** | Use templates from `AI_INSTRUCTIONS.md § 4–6 and § 11` |
| Testing prompt quality and edge cases | **Claude** | Feed test inputs and verify intent objects match expected output |
| Security review of each phase | **Claude** | Cross-check implementation against `SECURITY.md` checklist |
| Writing `phase_X.md` documentation | **Claude** | Use the template in Part 4 of this document |
| Complex algorithmic logic (e.g., availability engine) | **Codex / Cursor** | Reference `USER_FLOW.md § 3.6` for the decision logic |
| Large code generation tasks (>200 lines) | **Codex** | Provide the relevant spec section as context |
| Refactoring and code review | **Claude** | Provide the relevant `SECURITY.md` or `FEATURE_LIST.md` section |

---

## Part 6 — Decisions Already Made

The following decisions are locked. They must not be re-evaluated during any build phase. If circumstances change, update the relevant source document and version it — do not quietly deviate from it in code.

**Architecture:** Modular monolith. Python 3.11 + FastAPI backend. Next.js 14 frontend. No microservices in v1.0.

**Database:** PostgreSQL 16 via Supabase with pgvector extension. This replaces any prior mention of SQLite or ChromaDB. See `TECH_STACK.md — Architecture Reconciliation Note`.

**AI Model approach:** Hybrid — free/local first, paid as optional upgrade. The AI Model Router (`F048`) is the single abstraction layer. All AI calls go through the router. No module calls Claude or Ollama directly.

**Development approach:** Phase-based, with mandatory documentation after each phase. No phase is skipped. No feature is built out of dependency order.

**Free mode stack:** Ollama + Mistral 7B (LLM), faster-whisper (STT), Coqui TTS (TTS), Porcupine (wake word), all-MiniLM-L6-v2 (embeddings), Whoosh (keyword search).

**Paid mode stack:** Anthropic Claude claude-sonnet-4-20250514 (primary LLM), OpenAI Whisper API (STT), ElevenLabs (TTS), OpenAI text-embedding-3-small (embeddings).

**Communication:** Gmail API (email), Meta WhatsApp Business Cloud API v21.0 (WhatsApp), Google Calendar API v3 (calendar). Twilio WhatsApp Sandbox is acceptable for development only.

**Infrastructure:** Railway (backend + worker + Redis), Vercel (frontend), Supabase (DB + storage + auth), GitHub Actions (CI/CD).

**Permission model:** The four-level system (L0 Prohibited, L1 Always Confirm, L2 Confirm First Time, L3 Auto-Execute) from `SECURITY.md § 6.1` applies to all actions. It is not optional.

**Documentation:** Mandatory after every phase. Template in Part 4. No exceptions.

---

## Part 7 — Open Questions

The following questions must be answered before or during the relevant phase. Mark each as resolved by updating this section with the decision and the date it was made.

| # | Question | Relevant Phase | Status |
|---|----------|---------------|--------|
| OQ-1 | **Backend final choice: FastAPI or Node.js?** The TECH_STACK.md document specifies Python 3.11 + FastAPI. This is the current decision. This question is retained here in case a technical blocker during Phase 1 or 3 requires revisiting. | Phase 1 | Decided: FastAPI ✅ (TECH_STACK.md v1.0) |
| OQ-2 | **Local vs cloud AI balance — when does Ollama become a bottleneck?** On a machine with less than 8 GB RAM, Mistral 7B cannot run. If the user's hardware does not support free mode, what is the fallback? Should the onboarding flow include a hardware check that offers to start in paid mode? | Phase 3 | Open — resolve before Phase 3 begins |
| OQ-3 | **Deployment scale: personal vs multi-user?** v1.0 is single-user. Supabase Row-Level Security is in place for multi-user expansion. What is the trigger for opening the system to multiple users — a specific revenue threshold, a user request, or a v2.0 milestone? This affects infrastructure sizing decisions in Phase 1. | Phase 1 | Open — product decision needed |
| OQ-4 | **WhatsApp message template registration.** The Meta WhatsApp Business API requires pre-approved templates for messages sent outside the 24-hour window. Templates must be submitted to Meta for review (1–3 business day turnaround). When should template submission happen — before Phase 6 begins or as part of Phase 6? | Phase 6 | Open — submit templates at Phase 6 start |
| OQ-5 | **n8n persistence on Railway.** Railway's filesystem is ephemeral — n8n's default SQLite store will be lost on redeploy. n8n must be configured to use the Supabase PostgreSQL instance as its backend. Has this configuration been validated with n8n 1.x? | Phase 8 | Open — validate before Phase 8 |
| OQ-6 | **Meeting transcription chunk size.** `faster-whisper` processes audio in chunks. Smaller chunks (10s) give faster feedback but higher CPU load; larger chunks (60s) are more efficient but less real-time. What is the default chunk size and should it be user-configurable? | Phase 8 | Open — resolve before F040/F041 development |
| OQ-7 | **Porcupine commercial licence.** Porcupine's free licence covers personal non-commercial use. If Alex is monetised (even a personal subscription), a commercial Picovoice licence may be required. This must be legally clarified before any paid launch. | Phase 8 | Open — legal review required |

---

## Part 8 — Phase Completion Checklist

Use this checklist to verify a phase is complete before beginning the next one.

```
PHASE [N] COMPLETION CHECKLIST
────────────────────────────────────────────────────────
□  All features listed for this phase are implemented
□  Acceptance test passes cleanly
□  No hardcoded secrets in any file (all in .env)
□  All new endpoints are documented in API_ENDPOINTS.md
□  All new DB tables/columns match DATABASE.md exactly
□  RLS policies applied to any new user-scoped table
□  All new AI calls go through the AI Model Router
□  Permission system respected for any new actions
□  Free mode tested (Ollama path) — not just paid mode
□  Docker Compose still starts cleanly after this phase
□  Documentation/phase_N.md created using Part 4 template
□  phase_N.md reviewed for accuracy — no placeholder text
────────────────────────────────────────────────────────
Signed off by: _________________   Date: _______________
```

---

*This document is the build authority for Alex v1.0. All phases, tool assignments, and documentation requirements in this document are mandatory. Questions about why a decision was made belong in the relevant source document — TECH_STACK.md, SECURITY.md, SYSTEM_DESIGN.md — not in the code.*
