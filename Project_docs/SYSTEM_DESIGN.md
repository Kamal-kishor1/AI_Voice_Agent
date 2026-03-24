# System Design Document — Alex: Personal AI Operating System
**Version:** v1.0  
**Date:** 24 March 2026  
**Status:** Draft  
**References:** GOAL.md, PRD.md v1.0  
**Author:** Alex Project Team

---

## Table of Contents

1. [Purpose & Scope](#10-purpose--scope)
2. [System Overview](#20-system-overview)
3. [Architecture Pattern](#30-architecture-pattern)
4. [Component Breakdown](#40-component-breakdown)
   - 4.1 [Voice Layer](#41-voice-layer)
   - 4.2 [Intelligence Layer](#42-intelligence-layer-claude-api)
   - 4.3 [Memory & Database Layer](#43-memory--database-layer)
   - 4.4 [File & Search Layer](#44-file--search-layer)
   - 4.5 [Communication Layer](#45-communication-layer)
   - 4.6 [Automation Engine](#46-automation-engine)
   - 4.7 [Frontend / Dashboard](#47-frontenddashboard)
   - 4.8 [Monitoring & Logging](#48-monitoring--logging)
5. [Data Flow](#50-data-flow)
6. [API Design](#60-api-design)
7. [Database Schema](#70-database-schema)
8. [Integration Points](#80-integration-points)
9. [Scalability Considerations](#90-scalability-considerations)
10. [Open Questions](#100-open-questions)
11. [Next Steps](#110-next-steps)

---

## 1.0 Purpose & Scope

### 1.1 Purpose

This System Design Document defines the technical architecture for Alex v1.0. It translates the product requirements from PRD.md into concrete system components, data flows, API contracts, database schemas, and integration patterns.

This document is the definitive reference for engineers building Alex and must remain consistent with all other documentation in the series.

### 1.2 Decisions Inherited from PRD.md

The following key decisions from PRD.md are carried into this design:

| Decision | Value |
|----------|-------|
| Primary deployment platform | Mobile-first (React Native); web companion |
| LLM provider | Anthropic Claude (claude-sonnet-4-20250514) |
| File storage (v1.0) | Google Drive (primary); local filesystem (secondary) |
| WhatsApp integration | Meta Business API (official) |
| Memory strategy | Hybrid — cloud DB (primary) + local cache |
| Interaction languages | English only |
| User model | Single-user, single-instance |
| Latency target | ≤ 2 seconds voice-to-response |
| Transcription mode | Real-time streaming (post-meeting batch as fallback) |
| Briefing delivery | Auto-push at configurable time + on-demand |

---

## 2.0 System Overview

### 2.1 High-Level Architecture

```
╔══════════════════════════════════════════════════════════════════════════╗
║                          USER INTERACTION LAYER                          ║
║                                                                          ║
║   ┌──────────────┐      ┌──────────────┐      ┌──────────────────────┐  ║
║   │  Voice Input  │      │  Text Input  │      │  Wake Word Trigger   │  ║
║   │  (Microphone) │      │  (Chat UI)   │      │  ("Hey Alex")        │  ║
║   └──────┬───────┘      └──────┬───────┘      └──────────┬───────────┘  ║
╚══════════╪═════════════════════╪══════════════════════════╪══════════════╝
           │                     │                          │
           ▼                     ▼                          ▼
╔══════════════════════════════════════════════════════════════════════════╗
║                            VOICE LAYER                                   ║
║                                                                          ║
║   ┌─────────────────────┐        ┌──────────────────────────────────┐   ║
║   │  STT Engine         │        │  TTS Engine                      │   ║
║   │  (Deepgram / Whisper│        │  (ElevenLabs / Google TTS)       │   ║
║   │   streaming)        │        │                                  │   ║
║   └──────────┬──────────┘        └──────────────────────────────────┘   ║
╚══════════════╪═══════════════════════════════════════════════════════════╝
               │  Transcribed text
               ▼
╔══════════════════════════════════════════════════════════════════════════╗
║                         INTELLIGENCE LAYER                               ║
║                                                                          ║
║  ┌────────────────────────────────────────────────────────────────────┐ ║
║  │                      ALEX CORE ENGINE                              │ ║
║  │                                                                    │ ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐   │ ║
║  │  │ Intent Parser │  │ Planner      │  │ Response Generator    │   │ ║
║  │  │ (Claude API) │  │ (multi-step) │  │ (Claude API + stream) │   │ ║
║  │  └──────┬───────┘  └──────┬───────┘  └───────────────────────┘   │ ║
║  │         │                 │                                        │ ║
║  │  ┌──────▼─────────────────▼──────────────────────────────────┐    │ ║
║  │  │                    TOOL ROUTER                             │    │ ║
║  │  │  Routes to: Files | Email | WhatsApp | Calendar | Tasks   │    │ ║
║  │  └────────────────────────────────────────────────────────────┘    │ ║
║  └────────────────────────────────────────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════════════╝
               │
     ┌─────────┼──────────────────────────────────────┐
     │         │                                      │
     ▼         ▼                                      ▼
╔═════════╗ ╔═════════════════════════╗  ╔════════════════════════════════╗
║ MEMORY  ║ ║  FILE & SEARCH LAYER    ║  ║   COMMUNICATION LAYER          ║
║ LAYER   ║ ║                         ║  ║                                ║
║         ║ ║  ┌──────────────────┐   ║  ║  ┌────────────┐  ┌──────────┐ ║
║ Supabase║ ║  │ Google Drive API │   ║  ║  │ Gmail API  │  │WhatsApp  │ ║
║ (Postgres║ ║  │ + Embeddings     │   ║  ║  │            │  │Business  │ ║
║ + pgvec-║ ║  │ (Pinecone/pgvec) │   ║  ║  └────────────┘  │API       │ ║
║ tor)    ║ ║  └──────────────────┘   ║  ║                   └──────────┘ ║
╚═════════╝ ╚═════════════════════════╝  ╚════════════════════════════════╝
               │
     ┌─────────┼─────────────┐
     ▼         ▼             ▼
╔═════════════════════════════════════════════════════════╗
║              AUTOMATION ENGINE                          ║
║                                                         ║
║  ┌───────────────┐  ┌──────────────┐  ┌─────────────┐  ║
║  │ Task Scheduler │  │ Step Runner  │  │ Error Retry │  ║
║  │ (node-cron)   │  │ (sequential) │  │ Handler     │  ║
║  └───────────────┘  └──────────────┘  └─────────────┘  ║
╚═════════════════════════════════════════════════════════╝
               │
               ▼
╔═════════════════════════════════════════════════════════╗
║           FRONTEND / DASHBOARD                          ║
║                                                         ║
║  ┌─────────────────────┐   ┌──────────────────────────┐ ║
║  │ React Native App    │   │ Web Dashboard (Next.js)  │ ║
║  │ (Mobile-first)      │   │ (secondary)              │ ║
║  └─────────────────────┘   └──────────────────────────┘ ║
╚═════════════════════════════════════════════════════════╝
               │
               ▼
╔═════════════════════════════════════════════════════════╗
║           MONITORING & LOGGING                          ║
║                                                         ║
║  ┌──────────────┐  ┌────────────────┐  ┌────────────┐  ║
║  │ Sentry       │  │ PostHog        │  │ Logtail /  │  ║
║  │ (errors)     │  │ (analytics)    │  │ Axiom      │  ║
║  └──────────────┘  └────────────────┘  └────────────┘  ║
╚═════════════════════════════════════════════════════════╝
```

### 2.2 Component Connectivity Summary

```
User ──► Voice Layer ──► Intelligence Layer ──► Tool Router
                                │                    │
                         Memory Layer         ┌──────┴────────┐
                         (context inject)     │               │
                                         File Layer    Comm Layer
                                              │               │
                                         Automation Engine ───┘
                                              │
                                         Frontend (display/notify)
                                              │
                                         Monitoring (observe all)
```

---

## 3.0 Architecture Pattern

### 3.1 Chosen Pattern: Modular Monolith → Microservices-Ready

**Decision:** Alex v1.0 is built as a **modular monolith** with clearly bounded internal modules. Each module is independently testable and has a well-defined interface. The architecture is designed to split into microservices in v2.0 without a rewrite.

### 3.2 Rationale

| Factor | Monolith Advantage | Microservices Risk (v1.0) |
|--------|-------------------|--------------------------|
| Team size | Small team moves faster in a monolith | Microservice orchestration overhead too high |
| Latency | In-process calls = sub-millisecond | Network hops add latency; violates ≤2s target |
| Debugging | Single log stream, simpler tracing | Distributed tracing requires extra tooling |
| Deployment | One deployment unit | Multiple services to manage, monitor, deploy |
| Single user | No concurrency pressure | Microservices shine at scale; overkill here |

### 3.3 Module Boundaries (enforced in code)

```
alex-core/
├── voice/          # STT, TTS, wake word
├── intelligence/   # Claude integration, intent, planner
├── memory/         # DB reads/writes, preference engine
├── files/          # Search, indexing, retrieval
├── communication/  # Email, WhatsApp adapters
├── automation/     # Task scheduler, step runner
├── api/            # REST API layer (Express.js)
└── dashboard/      # Frontend (separate repo, React Native + Next.js)
```

### 3.4 Communication Between Modules

- **Synchronous:** Direct function calls within the monolith process
- **Asynchronous:** BullMQ job queue (Redis-backed) for long-running tasks (transcription, multi-step automation, briefing generation)
- **Events:** Internal EventEmitter for non-blocking side effects (e.g., log after action, update memory after conversation)

---

## 4.0 Component Breakdown

### 4.1 Voice Layer

**Responsibility:** Convert audio to text (STT), text to audio (TTS), and detect the wake word ("Hey Alex").

#### 4.1.1 Speech-to-Text (STT)

| Attribute | Value |
|-----------|-------|
| **Primary Provider** | Deepgram (Nova-3 model) |
| **Fallback** | OpenAI Whisper (self-hosted or API) |
| **Mode** | Streaming (real-time transcription) |
| **Language** | English (en-US) |
| **Latency Target** | First token in ≤ 300ms |
| **Format** | WebSocket stream → transcribed text chunks |

```
Audio stream
    │
    ▼
┌──────────────────────┐
│  Deepgram WebSocket  │  ──► Partial transcripts (live)
│  (Nova-3 streaming)  │  ──► Final transcript (on silence detection)
└──────────────────────┘
    │
    ▼
Text passed to Intelligence Layer
```

#### 4.1.2 Text-to-Speech (TTS)

| Attribute | Value |
|-----------|-------|
| **Primary Provider** | ElevenLabs (custom Alex voice) |
| **Fallback** | Google Cloud TTS (WaveNet) |
| **Streaming** | Yes — audio chunks streamed as text is generated |
| **Latency Target** | First audio chunk in ≤ 400ms |
| **Voice Character** | Calm, clear, professional |

#### 4.1.3 Wake Word Detection

| Attribute | Value |
|-----------|-------|
| **Trigger Phrase** | "Hey Alex" |
| **Engine** | Porcupine (on-device, by Picovoice) |
| **Processing** | 100% on-device — no audio sent to cloud until activated |
| **Platform** | React Native (iOS + Android SDK) |
| **Power Mode** | Always-on low-power mode |

---

### 4.2 Intelligence Layer (Claude API)

**Responsibility:** Understand intent, plan multi-step actions, generate responses, and decide which tools to invoke.

#### 4.2.1 Core Engine Design

```
Input Text
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│                    ALEX CORE ENGINE                         │
│                                                             │
│  Step 1: Context Assembly                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ System Prompt + User Profile + Conversation History │   │
│  │ + Recent Memory + Current Date/Time                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│  Step 2: Claude API Call (with tools)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ claude-sonnet-4-20250514                            │   │
│  │ Tools: search_files, send_email, send_whatsapp,     │   │
│  │        create_task, book_meeting, get_calendar,     │   │
│  │        get_memory, set_memory, run_automation       │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│  Step 3: Tool Router + Executor                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Parse tool_use blocks → Execute → Return results    │   │
│  │ Loop until final text response                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│  Step 4: Response Streaming                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Stream text → TTS → Audio output                   │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

#### 4.2.2 Claude API Configuration

| Parameter | Value |
|-----------|-------|
| Model | `claude-sonnet-4-20250514` |
| Max tokens | 4096 (response) |
| Temperature | 0.3 (for task execution); 0.7 (for conversational) |
| Streaming | Enabled (server-sent events) |
| Context window management | Sliding window — last 20 turns; summarize older turns |
| Prompt caching | Enabled on system prompt (static) |
| Tool choice | `auto` (Claude decides when to use tools) |

#### 4.2.3 Tool Definitions (Claude function-calling schema)

```json
[
  { "name": "search_files",      "description": "Search user's files semantically" },
  { "name": "send_email",        "description": "Draft and send an email" },
  { "name": "send_whatsapp",     "description": "Send a WhatsApp message" },
  { "name": "get_calendar",      "description": "Fetch calendar events and free slots" },
  { "name": "create_event",      "description": "Book a calendar event" },
  { "name": "create_task",       "description": "Create a task or reminder" },
  { "name": "get_tasks",         "description": "Retrieve pending tasks" },
  { "name": "get_memory",        "description": "Retrieve stored user preferences" },
  { "name": "set_memory",        "description": "Store a new preference or fact" },
  { "name": "transcribe_meeting","description": "Start or stop meeting transcription" },
  { "name": "get_briefing",      "description": "Generate the morning briefing" },
  { "name": "run_automation",    "description": "Trigger a multi-step automation plan" }
]
```

#### 4.2.4 System Prompt Architecture

The system prompt is structured in layers:

```
[LAYER 1 - STATIC — CACHED]
Alex identity, personality, operating rules, tool descriptions

[LAYER 2 - SEMI-STATIC — REFRESHED DAILY]
User profile: name, preferences, working hours, tone settings,
top contacts, current projects

[LAYER 3 - DYNAMIC — PER REQUEST]
Current date/time, recent conversation history (last 10 turns),
active tasks, today's calendar, any triggered context
```

---

### 4.3 Memory & Database Layer

**Responsibility:** Persist all user data, conversation history, preferences, embeddings, and task state.

#### 4.3.1 Database Stack

| Store | Technology | Purpose |
|-------|-----------|---------|
| **Primary DB** | Supabase (PostgreSQL) | Structured data: tasks, events, contacts, logs |
| **Vector Store** | pgvector (in Supabase) | Semantic search embeddings for files and memory |
| **Cache** | Redis (Upstash) | Session state, conversation context, rate limiting |
| **Local Cache** | SQLite (on-device) | Offline preferences; syncs to Supabase on reconnect |

#### 4.3.2 Memory Types

```
MEMORY SYSTEM
├── Short-term Memory  →  Redis (conversation context, expires in 24h)
├── Long-term Memory   →  Supabase (preferences, learned facts, never expires)
├── Episodic Memory    →  Supabase (past interactions, summaries, timestamped)
└── Semantic Memory    →  pgvector (embeddings for files, conversations, notes)
```

#### 4.3.3 Embedding Strategy

- **Model:** `text-embedding-3-small` (OpenAI) or `voyage-3` (Anthropic)
- **What gets embedded:** File metadata + preview, conversation summaries, task descriptions, contact interaction summaries
- **When:** On write (background job via BullMQ)
- **Retrieval:** cosine similarity, top-k = 5

---

### 4.4 File & Search Layer

**Responsibility:** Index, search, and retrieve user files from connected storage.

#### 4.4.1 Architecture

```
Google Drive API
      │
      ▼
┌─────────────────────────┐
│   File Indexer Service  │  (runs on schedule + on-demand)
│                         │
│  1. Fetch file metadata │
│  2. Extract text content│  (PDF, DOCX, Sheets via parsers)
│  3. Chunk content       │  (512 token chunks with overlap)
│  4. Generate embeddings │  (text-embedding-3-small)
│  5. Store in pgvector   │
└─────────────────────────┘
      │
      ▼
┌─────────────────────────┐
│   Search Engine         │
│                         │
│  Query → embed query    │
│  → vector similarity    │
│  → rank by recency +    │
│    similarity score     │
│  → return top 3 results │
└─────────────────────────┘
```

#### 4.4.2 File Indexing Schedule

| Trigger | Action |
|---------|--------|
| On app start | Full index sync (delta only) |
| Every 15 minutes | Check for new/modified files |
| After file send/receive action | Immediate re-index of that file |
| On user command ("reindex my files") | Force full re-index |

#### 4.4.3 Supported File Types (v1.0)

| Format | Parser |
|--------|--------|
| PDF | pdf-parse (Node.js) |
| DOCX | mammoth.js |
| XLSX | SheetJS |
| Google Docs | Google Docs export API |
| Google Sheets | Google Sheets API |
| TXT / MD | Native string |
| Images | Out of scope (v1.0) |

---

### 4.5 Communication Layer

**Responsibility:** Send and receive emails and WhatsApp messages on behalf of the user.

#### 4.5.1 Email (Gmail)

```
Alex Intelligence Layer
        │
        ▼ (send_email tool called)
┌────────────────────────────────────┐
│         Email Adapter              │
│                                    │
│  1. Resolve contact → email addr   │
│  2. Draft subject + body (Claude)  │
│  3. Apply tone preferences         │
│  4. Attach file (if requested)     │
│  5. Preview (if first time contact)│
│  6. Send via Gmail API             │
│  7. Log in sent_messages table     │
└────────────────────────────────────┘
```

| Attribute | Value |
|-----------|-------|
| Provider | Gmail API (Google OAuth 2.0) |
| Auth | OAuth 2.0 with refresh token stored in Supabase (encrypted) |
| Draft mode | Enabled by default for new contacts; skippable |
| Rate limit | Gmail: 250 quota units/second |
| File attach | Google Drive link or inline attachment (< 25MB) |

#### 4.5.2 WhatsApp

```
Alex Intelligence Layer
        │
        ▼ (send_whatsapp tool called)
┌────────────────────────────────────┐
│       WhatsApp Adapter             │
│                                    │
│  1. Resolve contact → phone number │
│  2. Select message template or     │
│     freeform (based on 24h window) │
│  3. Attach media (if file)         │
│  4. Send via Meta Business API     │
│  5. Log in sent_messages table     │
└────────────────────────────────────┘
```

| Attribute | Value |
|-----------|-------|
| Provider | Meta WhatsApp Business API (Cloud API) |
| Auth | Permanent access token (Meta App) |
| Message types | Text, document, image |
| Template requirement | Required for messages outside 24h window |
| Webhook | Meta webhook → Alex server → update message status |

#### 4.5.3 Contact Resolution Engine

```
Input: "Priya"
    │
    ▼
┌──────────────────────────────────────────────┐
│  1. Exact match in contacts table            │
│  2. Fuzzy match (Levenshtein distance ≤ 2)  │
│  3. Context match (last discussed contact)   │
│  4. If still ambiguous → ask clarification   │
└──────────────────────────────────────────────┘
```

---

### 4.6 Automation Engine

**Responsibility:** Execute multi-step tasks sequentially, handle dependencies, manage retries, and surface results.

#### 4.6.1 Architecture

```
Intelligence Layer creates an Automation Plan:
{
  "plan_id": "plan_abc123",
  "steps": [
    { "id": 1, "tool": "search_files",  "params": {"query": "Q3 report"} },
    { "id": 2, "tool": "send_email",    "params": {"to": "arjun", "attach": "$step1.result"}, "depends_on": [1] },
    { "id": 3, "tool": "create_task",   "params": {"title": "Follow up with Arjun"}, "depends_on": [2] }
  ]
}
        │
        ▼
┌──────────────────────────────────────────────────┐
│                  Step Runner                      │
│                                                  │
│  For each step (in dependency order):            │
│  1. Resolve parameter references ($step.result)  │
│  2. Execute tool                                 │
│  3. On success → store result, proceed           │
│  4. On failure → retry (max 3) → surface error  │
│  5. On completion → notify user                 │
└──────────────────────────────────────────────────┘
```

#### 4.6.2 Scheduled Jobs (via node-cron + BullMQ)

| Job | Schedule | Description |
|-----|----------|-------------|
| Morning Briefing | 07:00 AM (configurable) | Generate and push daily briefing |
| Pre-meeting prep | 10 min before event | Surface relevant files + context |
| Follow-up suggestions | 30 min after meeting end | Suggest follow-up email |
| File re-index | Every 15 min | Sync new/modified files |
| Memory consolidation | 11:00 PM daily | Summarize day's interactions to long-term memory |
| Overdue task check | Every hour | Flag and notify overdue tasks |

#### 4.6.3 Error Handling Strategy

```
Step fails
    │
    ├─► Retry (max 3 attempts, exponential backoff)
    │
    ├─► On 3rd failure: mark step as failed
    │
    ├─► Continue independent steps if no dependency
    │
    └─► Notify user:
        "I couldn't complete step 2 (send email). 
         The file was found. Want me to retry?"
```

---

### 4.7 Frontend / Dashboard

**Responsibility:** User interface for conversation, task management, settings, and briefing review.

#### 4.7.1 Mobile App (Primary — React Native)

| Screen | Description |
|--------|-------------|
| **Home / Chat** | Conversation interface with voice + text input |
| **Voice Mode** | Full-screen waveform; active listening state |
| **Briefing View** | Scrollable morning briefing with action buttons |
| **Tasks** | List of pending and completed tasks |
| **Calendar** | Day/week view of scheduled events |
| **Files** | Recent and searched files |
| **Settings** | Connected accounts, tone preferences, working hours |

#### 4.7.2 Web Dashboard (Secondary — Next.js)

| Page | Description |
|------|-------------|
| `/` | Dashboard overview — tasks, today's schedule, recent activity |
| `/chat` | Text-based conversation interface |
| `/files` | File browser with semantic search |
| `/settings` | Full settings management |
| `/briefing` | Today's briefing (read-only web view) |

#### 4.7.3 Real-time Updates

- **Technology:** Supabase Realtime (WebSocket subscriptions)
- **What updates live:** Task status changes, incoming messages, automation progress, meeting transcription feed

---

### 4.8 Monitoring & Logging

**Responsibility:** Observe system health, track errors, and capture usage analytics.

#### 4.8.1 Monitoring Stack

| Tool | Purpose | What It Tracks |
|------|---------|---------------|
| **Sentry** | Error tracking | Unhandled exceptions, API failures, crash reports |
| **PostHog** | Product analytics | Feature usage, session events, funnel completion |
| **Axiom / Logtail** | Log management | Structured logs from all modules |
| **Upstash Redis** | Queue monitoring | BullMQ job success/fail rates, queue depth |
| **Supabase Dashboard** | DB monitoring | Query performance, connection pool |

#### 4.8.2 Logging Schema (every action)

```json
{
  "timestamp":   "2026-03-24T07:15:03Z",
  "session_id":  "sess_abc123",
  "event_type":  "tool_call",
  "tool_name":   "send_email",
  "status":      "success",
  "latency_ms":  847,
  "input_hash":  "sha256:...",
  "error":       null
}
```

#### 4.8.3 Alerting Rules

| Condition | Alert |
|-----------|-------|
| Tool call failure rate > 10% in 5 min | PagerDuty / email alert |
| Voice response latency > 3s avg | Warning log + Sentry event |
| BullMQ queue depth > 50 jobs | Slack notification |
| Supabase connection pool > 80% | Warning |
| Claude API error rate > 5% | Immediate alert |

---

## 5.0 Data Flow

### 5.1 Primary Request → Response Cycle

```
[1] USER SPEAKS: "Find the Q3 report and email it to Arjun"
         │
         ▼
[2] WAKE WORD DETECTED (Porcupine on-device)
    → Microphone activated
         │
         ▼
[3] AUDIO STREAMED TO DEEPGRAM
    → Partial transcripts rendered live in UI
    → Final transcript: "Find the Q3 report and email it to Arjun"
         │
         ▼
[4] CONTEXT ASSEMBLED
    ├── System prompt (cached)
    ├── User profile pulled from Supabase
    ├── Last 10 conversation turns from Redis
    └── Current time, today's calendar
         │
         ▼
[5] CLAUDE API CALLED (claude-sonnet-4-20250514, streaming, tools enabled)
    → Claude determines: needs search_files + send_email
         │
         ▼
[6] TOOL: search_files("Q3 report")
    → Query embedded → pgvector similarity search
    → Top result: "Q3_Sales_Report_2025.pdf" (Google Drive)
    → File URL + metadata returned to Claude
         │
         ▼
[7] TOOL: send_email(to="Arjun", subject="...", body="...", attach=file_url)
    → Contact resolved: arjun@company.com
    → Email drafted by Claude
    → Attached via Google Drive link
    → Sent via Gmail API
    → Logged to sent_messages table
         │
         ▼
[8] CLAUDE GENERATES FINAL RESPONSE (streaming text)
    → "Done — I found the Q3 Sales Report and emailed it to Arjun 
       at arjun@company.com with a note that it's ready for review."
         │
         ▼
[9] TEXT STREAMED TO ELEVENLABS TTS
    → Audio chunks streamed back as text is generated
    → User hears response in ≤ 2s from step [3]
         │
         ▼
[10] POST-PROCESSING
    → Conversation turn stored in Redis (short-term)
    → Action logged to Supabase (long-term)
    → Memory updated: "Arjun prefers email for reports"
```

### 5.2 Morning Briefing Flow

```
[1] SCHEDULED JOB fires at 07:00 AM (BullMQ)
         │
         ▼
[2] PARALLEL DATA FETCH
    ├── Google Calendar: today's events
    ├── Tasks DB: pending + overdue tasks
    ├── Gmail: unread important messages (priority inbox)
    └── Memory: active projects, recent decisions
         │
         ▼
[3] CLAUDE GENERATES BRIEFING
    → Structured prompt: "Generate morning briefing for [user]..."
    → Output: prioritized summary, schedule, top 3 action items
         │
         ▼
[4] BRIEFING STORED in Supabase (briefings table)
         │
         ▼
[5] PUSH NOTIFICATION sent to mobile app
         │
         ▼
[6] USER OPENS APP → TTS reads briefing aloud
    → User can interrupt with voice at any point
    → Briefing transitions to live conversation
```

### 5.3 Autonomous Multi-Step Task Flow

```
[1] INPUT: "Schedule a call with Priya for Thursday, 
           send her the contract, and remind me to 
           prepare talking points Wednesday night"
         │
         ▼
[2] CLAUDE CREATES PLAN (3 steps with dependencies)
    Step A: get_calendar(Thursday) → find free slot
    Step B: create_event(Priya, Thursday 2PM) → send invite
    Step C: search_files("contract") → send_whatsapp(Priya, file)
    Step D: create_task("Prepare talking points", due=Wednesday 8PM)
         │
         ▼
[3] AUTOMATION ENGINE executes steps A → B → C → D
    (B depends on A; C runs parallel to B; D is independent)
         │
         ▼
[4] EACH STEP: execute → store result → update UI in real-time
         │
         ▼
[5] COMPLETION NOTIFICATION:
    "All done — call booked for Thursday 2 PM,
     contract sent to Priya on WhatsApp,
     and I've set a reminder for Wednesday at 8 PM."
```

---

## 6.0 API Design

### 6.1 Base Configuration

| Attribute | Value |
|-----------|-------|
| Protocol | HTTPS (REST) |
| Base URL | `https://api.alexos.app/v1` |
| Auth | Bearer token (JWT, 24h expiry + refresh token) |
| Format | JSON (request + response) |
| Streaming | Server-Sent Events (SSE) for voice/chat responses |
| Rate Limiting | 120 requests/minute per user |

### 6.2 Core Endpoints

#### Conversation

```
POST   /v1/chat
       Body: { "input": "string", "session_id": "string", "mode": "text|voice" }
       Response (SSE stream): { "type": "text|tool_call|done", "content": "..." }

GET    /v1/chat/history?session_id=&limit=
       Response: { "messages": [...] }

DELETE /v1/chat/session/:session_id
       Response: { "deleted": true }
```

#### Files

```
POST   /v1/files/search
       Body: { "query": "string", "limit": 5 }
       Response: { "results": [{ "id", "name", "url", "score", "preview" }] }

POST   /v1/files/index
       Body: { "force": false }
       Response: { "job_id": "string", "status": "queued" }

GET    /v1/files/index/status/:job_id
       Response: { "status": "running|complete|failed", "indexed": 234 }
```

#### Communication

```
POST   /v1/email/send
       Body: { "to": "name|email", "subject": "...", "body": "...", "attach_file_id": "..." }
       Response: { "message_id": "...", "status": "sent" }

POST   /v1/whatsapp/send
       Body: { "to": "name|phone", "message": "...", "attach_file_id": "..." }
       Response: { "message_id": "...", "status": "queued" }
```

#### Calendar

```
GET    /v1/calendar/events?date=YYYY-MM-DD&range=day|week
       Response: { "events": [{ "id", "title", "start", "end", "attendees" }] }

GET    /v1/calendar/free-slots?date=YYYY-MM-DD&duration_mins=60
       Response: { "slots": [{ "start", "end" }] }

POST   /v1/calendar/events
       Body: { "title", "start", "end", "attendees": [], "description": "..." }
       Response: { "event_id": "...", "calendar_link": "..." }

PATCH  /v1/calendar/events/:event_id
PUT    /v1/calendar/events/:event_id  (reschedule)
DELETE /v1/calendar/events/:event_id
```

#### Tasks

```
GET    /v1/tasks?status=pending|completed|overdue
POST   /v1/tasks
       Body: { "title", "due_at": "ISO8601", "related_contact": "...", "context": "..." }
PATCH  /v1/tasks/:task_id   Body: { "status": "completed" }
DELETE /v1/tasks/:task_id
```

#### Memory

```
GET    /v1/memory?category=preference|contact|project
POST   /v1/memory
       Body: { "key": "...", "value": "...", "category": "...", "confidence": 0.9 }
DELETE /v1/memory/:memory_id
```

#### Briefing

```
GET    /v1/briefing/today
       Response: { "briefing_id", "generated_at", "content": "...", "tts_url": "..." }

POST   /v1/briefing/generate
       Response: { "job_id": "..." }  (async)
```

#### Automations

```
POST   /v1/automation/run
       Body: { "plan": { "steps": [...] } }
       Response: { "plan_id": "...", "status": "running" }

GET    /v1/automation/:plan_id/status
       Response: { "plan_id", "steps": [{ "id", "status", "result" }] }
```

### 6.3 Standard Response Format

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-03-24T07:15:03Z",
    "latency_ms": 284
  }
}
```

### 6.4 Error Response Format

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "CONTACT_NOT_FOUND",
    "message": "Could not resolve contact 'Priya'. Did you mean Priya Sharma or Priya Mehta?",
    "suggestions": ["Priya Sharma", "Priya Mehta"]
  },
  "meta": { "request_id": "req_abc123", "timestamp": "..." }
}
```

---

## 7.0 Database Schema

### 7.1 Schema Diagram

```
┌─────────────────────┐         ┌─────────────────────────┐
│       users         │         │       sessions           │
├─────────────────────┤         ├─────────────────────────┤
│ id (PK, UUID)       │─────────│ id (PK, UUID)            │
│ name                │  1:many │ user_id (FK → users)     │
│ email               │         │ started_at               │
│ working_hours_start │         │ ended_at                 │
│ working_hours_end   │         │ summary                  │
│ timezone            │         └─────────────────────────┘
│ tone_preference     │
│ created_at          │
└──────────┬──────────┘
           │ 1:many
           │
     ┌─────┼──────────────────────────────────────────────┐
     │     │                                              │
     ▼     ▼                                              ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────────┐
│      memories       │  │       tasks          │  │      contacts         │
├─────────────────────┤  ├─────────────────────┤  ├───────────────────────┤
│ id (PK, UUID)       │  │ id (PK, UUID)        │  │ id (PK, UUID)         │
│ user_id (FK)        │  │ user_id (FK)         │  │ user_id (FK)          │
│ key                 │  │ title                │  │ name                  │
│ value               │  │ description          │  │ email                 │
│ category            │  │ status               │  │ phone                 │
│   (preference,      │  │   (pending,          │  │ preferred_channel     │
│    contact,         │  │    complete,         │  │   (email|whatsapp)    │
│    project,         │  │    overdue)          │  │ interaction_count     │
│    fact)            │  │ due_at               │  │ last_interaction_at   │
│ confidence (0-1)    │  │ related_contact_id   │  │ notes                 │
│ source              │  │   (FK → contacts)   │  └───────────────────────┘
│ embedding (vector)  │  │ created_at           │
│ created_at          │  │ completed_at         │
│ updated_at          │  └─────────────────────┘
└─────────────────────┘
           │
           ▼
┌─────────────────────────┐  ┌─────────────────────────────┐
│    sent_messages        │  │         files               │
├─────────────────────────┤  ├─────────────────────────────┤
│ id (PK, UUID)           │  │ id (PK, UUID)               │
│ user_id (FK)            │  │ user_id (FK)                │
│ channel (email|whatsapp)│  │ name                        │
│ to_contact_id (FK)      │  │ drive_id                    │
│ subject                 │  │ mime_type                   │
│ body_preview            │  │ drive_url                   │
│ has_attachment          │  │ content_preview             │
│ attachment_file_id (FK) │  │ embedding (vector[1536])    │
│ external_message_id     │  │ indexed_at                  │
│ status                  │  │ last_modified               │
│ sent_at                 │  └─────────────────────────────┘
└─────────────────────────┘

┌─────────────────────────────┐  ┌──────────────────────────────┐
│         events              │  │         briefings            │
├─────────────────────────────┤  ├──────────────────────────────┤
│ id (PK, UUID)               │  │ id (PK, UUID)                │
│ user_id (FK)                │  │ user_id (FK)                 │
│ calendar_event_id (external)│  │ date (DATE)                  │
│ title                       │  │ content (TEXT)               │
│ start_at                    │  │ tts_url                      │
│ end_at                      │  │ tasks_snapshot (JSONB)       │
│ attendees (JSONB)           │  │ events_snapshot (JSONB)      │
│ transcript (TEXT)           │  │ generated_at                 │
│ summary                     │  │ opened_at                    │
│ action_items (JSONB)        │  └──────────────────────────────┘
│ meeting_status              │
│   (scheduled,               │  ┌──────────────────────────────┐
│    live, complete)          │  │     automation_plans         │
└─────────────────────────────┘  ├──────────────────────────────┤
                                  │ id (PK, UUID)                │
                                  │ user_id (FK)                 │
                                  │ trigger_text                 │
                                  │ steps (JSONB)                │
                                  │ status                       │
                                  │   (pending,running,          │
                                  │    complete,failed)          │
                                  │ created_at                   │
                                  │ completed_at                 │
                                  └──────────────────────────────┘
```

### 7.2 Key Indexes

```sql
-- Semantic search
CREATE INDEX idx_files_embedding ON files 
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_memories_embedding ON memories 
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Frequent lookups
CREATE INDEX idx_tasks_user_status ON tasks (user_id, status);
CREATE INDEX idx_events_user_date ON events (user_id, start_at);
CREATE INDEX idx_messages_user_channel ON sent_messages (user_id, channel, sent_at);
CREATE INDEX idx_contacts_user_name ON contacts (user_id, name);
```

---

## 8.0 Integration Points

### 8.1 Integration Map

```
Alex Core
    │
    ├── Google Suite
    │     ├── Gmail API (OAuth 2.0)          → Send/read emails
    │     ├── Google Calendar API (OAuth 2.0) → Events, free/busy
    │     └── Google Drive API (OAuth 2.0)    → File index + download
    │
    ├── Meta
    │     └── WhatsApp Business API           → Send messages + media
    │
    ├── AI / ML
    │     ├── Anthropic Claude API            → Intelligence core
    │     ├── Deepgram API                    → STT (streaming)
    │     ├── ElevenLabs API                  → TTS (streaming)
    │     └── OpenAI Embeddings API           → File + memory embeddings
    │
    ├── Infrastructure
    │     ├── Supabase                        → DB + auth + realtime
    │     ├── Upstash Redis                   → Cache + queues
    │     └── Vercel / Railway                → Backend deployment
    │
    └── Monitoring
          ├── Sentry                          → Error tracking
          ├── PostHog                         → Analytics
          └── Axiom                           → Log management
```

### 8.2 Integration Details

#### Google OAuth 2.0 (Gmail, Calendar, Drive)

| Attribute | Detail |
|-----------|--------|
| Scopes | `gmail.send`, `gmail.readonly`, `calendar.events`, `drive.readonly` |
| Token storage | Encrypted in Supabase (`oauth_tokens` table), AES-256 |
| Refresh | Automatic via Google refresh token (never expiring) |
| Quota | Gmail: 1B units/day; Calendar: 1M requests/day; Drive: 1B units/day |
| Revocation | User can disconnect from Settings; tokens deleted immediately |

#### Meta WhatsApp Business API

| Attribute | Detail |
|-----------|--------|
| API Type | Cloud API (Meta-hosted) |
| Auth | Permanent system user access token |
| Message window | Freeform messages only within 24h of last user message |
| Outside 24h | Must use approved message templates |
| Media | Supports documents, images, audio (≤ 100MB) |
| Webhooks | Message status updates (sent/delivered/read) → `/webhooks/whatsapp` |

#### Anthropic Claude API

| Attribute | Detail |
|-----------|--------|
| Model | `claude-sonnet-4-20250514` |
| Auth | API key (env variable; never exposed to client) |
| Features used | Messages API, tool use, streaming, prompt caching |
| Cost control | Prompt caching on system prompt; max_tokens=4096 hard cap |
| Fallback | If Claude API unavailable → queue request, notify user of delay |

#### Deepgram (STT)

| Attribute | Detail |
|-----------|--------|
| Model | Nova-3 (latest, streaming-optimised) |
| Protocol | WebSocket (bidirectional) |
| Features | Interim results, endpointing, smart formatting, punctuation |
| Auth | API key (server-side only) |

#### ElevenLabs (TTS)

| Attribute | Detail |
|-----------|--------|
| Model | `eleven_turbo_v2` (low latency) |
| Voice | Custom Alex voice (cloned or selected from library) |
| Streaming | WebSocket → chunk audio as text is being generated |
| Fallback | Google Cloud TTS (WaveNet en-US Standard) |

---

## 9.0 Scalability Considerations

> Note: Alex v1.0 is single-user. These considerations document how the system is designed to scale when needed, without requiring a rewrite.

### 9.1 Horizontal Scaling Path

| Component | v1.0 | v2.0 Scale Path |
|-----------|------|-----------------|
| API Server | Single Node.js process (Railway) | Horizontal pod autoscaling (Kubernetes) |
| Database | Single Supabase project | Read replicas + connection pooler (PgBouncer) |
| Cache | Single Upstash Redis instance | Redis Cluster |
| Queue | BullMQ (single worker) | Multiple BullMQ workers, partitioned queues |
| File indexer | Single scheduled job | Distributed indexing workers per user |
| LLM calls | Sequential | Parallel requests + request batching |

### 9.2 Performance Optimisations in v1.0

| Optimisation | Implementation |
|-------------|---------------|
| Prompt caching | Static system prompt cached in Claude API (saves ~70% tokens) |
| Streaming responses | SSE from Claude → TTS → user (no waiting for full response) |
| Redis session cache | Conversation context in Redis (< 1ms read vs. DB) |
| Embedding cache | File embeddings stored; only re-embed on file change |
| Lazy file indexing | Delta sync only (not full re-index every time) |
| DB connection pool | Supabase pooler (max 10 connections for single-user) |

### 9.3 Data Volume Estimates (Single User, 12 Months)

| Data Type | Estimated Volume |
|-----------|-----------------|
| Conversation turns | ~7,000 turns (20/day × 365) |
| Files indexed | ~2,000 files |
| Embeddings (files) | ~10,000 vectors (1536-dim each) |
| Tasks | ~2,000 records |
| Sent messages | ~1,500 records |
| Calendar events | ~500 records |
| Memory records | ~500 records |
| **Total DB size** | **< 2 GB** |

---

## 10.0 Open Questions

| # | Question | Impact | Decision Needed By |
|---|----------|--------|-------------------|
| OQ-SD-1 | Should the Node.js backend be deployed on Railway or Vercel (serverless)? Serverless has cold start latency risk for voice. | Latency target of ≤ 2s may be violated with cold starts | Before engineering begins |
| OQ-SD-2 | Use pgvector (in Supabase) or a dedicated vector DB (Pinecone) for embeddings? | Pinecone is faster at scale; pgvector simpler for v1.0 | Before file layer build |
| OQ-SD-3 | OpenAI `text-embedding-3-small` or Anthropic Voyage for embeddings? Voyage is better for code/documents; OpenAI is cheaper | Quality vs. cost | Before file indexer build |
| OQ-SD-4 | How should the system handle the WhatsApp 24h message window for proactive messages (briefing shares, follow-ups)? | May require pre-approved templates for all proactive sends | Before comm layer build |
| OQ-SD-5 | Should conversation history be summarised (compressed) automatically after N turns, or use full history with sliding window? | Affects token cost and context quality | Before intelligence layer build |
| OQ-SD-6 | Is a settings UI required in v1.0 or can all preferences be set by voice ("Alex, change my tone to casual")? | Affects frontend scope | Before dashboard build |

---

## 11.0 Next Steps

| # | Action | Owner | Dependency |
|---|--------|-------|-----------|
| NS-1 | Resolve OQ-SD-1 through OQ-SD-3 (infrastructure + embedding decisions) | Engineering Lead | Immediately |
| NS-2 | Set up Supabase project, define schemas, run migrations | Backend Engineer | After OQ-SD-2 resolved |
| NS-3 | Configure Claude API key, test tool-use + streaming | Backend Engineer | Immediately |
| NS-4 | Set up Meta WhatsApp Business API sandbox + test messaging | Backend Engineer | Immediately |
| NS-5 | Scaffold `alex-core` monolith with module boundaries defined | Engineering Lead | After NS-1 |
| NS-6 | Begin **User Flow Document** (Document 3) — map all user journeys to this architecture | Product + Engineering | After SYSTEM_DESIGN sign-off |
| NS-7 | Review SYSTEM_DESIGN.md with all stakeholders and resolve open questions | All | Within 2 days |

---

*Decisions from this document will be referenced in all subsequent documentation: User Flows, Feature List, Tech Stack, Security, and AI Instructions.*

---

**Document Control**

| Field | Value |
|-------|-------|
| Document Name | SYSTEM_DESIGN.md |
| Version | v1.0 |
| Status | Draft |
| Created | 24 March 2026 |
| Last Updated | 24 March 2026 |
| References | GOAL.md, PRD.md v1.0 |
