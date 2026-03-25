# System Design Document
## Alex — Personal AI Operating System
**Version:** v1.0
**Date:** 24 March 2026
**Status:** Draft
**Author:** Alex Build Team
**References:** PRD.md v1.0, GOAL.md

---

## Table of Contents

1.0 Purpose & Scope
2.0 System Overview
3.0 Architecture Pattern
4.0 Component Breakdown
5.0 Data Flow
6.0 API Design
7.0 Database Schema
8.0 Integration Points
9.0 Scalability Considerations
10.0 Open Questions
11.0 Next Steps

---

## 1.0 Purpose & Scope

### 1.1 Purpose

This System Design Document defines the technical architecture for Alex v1.0 — a personal AI Operating System. It translates the requirements established in PRD.md into a concrete, buildable system design, specifying components, data flows, API contracts, database schemas, and integration points.

Every architectural decision in this document reflects two foundational constraints carried forward from the PRD: (1) all core functionality must operate fully in free/local mode without any paid API dependency, and (2) paid APIs such as OpenAI and Anthropic Claude are optional performance upgrades, activated exclusively by user choice.

### 1.2 Scope

This document covers the complete technical design for the following layers:

- Voice processing pipeline (input and output)
- Intelligence layer supporting both local and paid AI models
- Memory and database subsystem
- File indexing and semantic search engine
- Communication dispatch layer (email and WhatsApp)
- Automation engine for multi-step task execution
- Frontend dashboard
- Monitoring, logging, and observability

### 1.3 PRD Decisions Carried Forward

The following decisions from PRD.md directly shape this architecture:

| PRD Decision | Architectural Implication |
|-------------|--------------------------|
| Free mode must be 100% functional | Every component has a free-mode implementation path; no single point of paid-API dependency |
| Paid APIs are boosters, not replacements | An AI Model Router abstraction decouples the intelligence layer from any specific model provider |
| Voice-first interaction required | A dedicated Voice Layer runs as an independent process, not a UI widget |
| Local file system access only in v1.0 | File indexing operates on local directories; no cloud storage connector is required |
| Single-user system in v1.0 | No multi-tenancy design; all data storage is user-scoped by default |
| Mode switching must be non-disruptive | The AI Model Router handles hot-switching between model providers at runtime |

---

## 2.0 System Overview

### 2.1 High-Level Architecture

Alex is organized as a layered system. User input enters through the Voice or Text Interface, is processed by the Intelligence Layer, and dispatched to one or more Action Modules. Results are returned to the user through the same interface and optionally stored in memory.

```
╔══════════════════════════════════════════════════════════════════════╗
║                         USER INTERFACE LAYER                         ║
║   ┌─────────────────────────┐     ┌──────────────────────────────┐   ║
║   │     Voice Interface      │     │     Web Dashboard (UI)       │   ║
║   │  (Mic Input / TTS Output)│     │  (Chat, Tasks, Settings)     │   ║
║   └────────────┬────────────┘     └──────────────┬───────────────┘   ║
╚════════════════╪══════════════════════════════════╪═══════════════════╝
                 │                                  │
╔════════════════╪══════════════════════════════════╪═══════════════════╗
║                │         VOICE LAYER              │                    ║
║   ┌────────────▼────────────┐                     │                   ║
║   │   Wake Word Detection   │                     │                   ║
║   │   (Porcupine / Picovoice│                     │                   ║
║   │    — offline capable)   │                     │                   ║
║   └────────────┬────────────┘                     │                   ║
║   ┌────────────▼────────────┐                     │                   ║
║   │  Speech-to-Text (STT)   │                     │                   ║
║   │  FREE:  Whisper (local) │                     │                   ║
║   │  PAID:  OpenAI Whisper  │                     │                   ║
║   └────────────┬────────────┘                     │                   ║
║   ┌────────────▼────────────┐                     │                   ║
║   │  Text-to-Speech (TTS)   │                     │                   ║
║   │  FREE:  Coqui TTS       │                     │                   ║
║   │  PAID:  ElevenLabs      │                     │                   ║
║   └────────────┬────────────┘                     │                   ║
╚════════════════╪═════════════════════════════════╪════════════════════╝
                 │                                 │
╔════════════════╪═════════════════════════════════╪════════════════════╗
║                │      INTELLIGENCE LAYER         │                    ║
║   ┌────────────▼─────────────────────────────────▼──────────────┐    ║
║   │                     Intent Parser                            │    ║
║   │          (Extracts intent, entities, action steps)           │    ║
║   └──────────────────────────┬──────────────────────────────────┘    ║
║   ┌──────────────────────────▼──────────────────────────────────┐    ║
║   │                   AI Model Router                            │    ║
║   │   FREE MODE:  Ollama → Mistral 7B / LLaMA 3.1 8B            │    ║
║   │   PAID MODE:  Anthropic Claude API / OpenAI GPT-4o           │    ║
║   │   (Hot-switchable; user-controlled; no restart required)     │    ║
║   └──────────────────────────┬──────────────────────────────────┘    ║
║   ┌──────────────────────────▼──────────────────────────────────┐    ║
║   │                   Task Planner                               │    ║
║   │   (Decomposes multi-step commands into ordered action steps) │    ║
║   └──────────────────────────┬──────────────────────────────────┘    ║
╚════════════════════════════════╪═══════════════════════════════════════╝
                                 │
╔════════════════════════════════╪═══════════════════════════════════════╗
║              ACTION LAYER      │                                        ║
║  ┌──────────┐ ┌─────────┐ ┌───▼──────┐ ┌──────────┐ ┌─────────────┐  ║
║  │  File    │ │  Comms  │ │Automation│ │ Calendar │ │   Meeting   │  ║
║  │  Search  │ │ Engine  │ │  Engine  │ │ Manager  │ │   Copilot   │  ║
║  │  Engine  │ │(Email + │ │(Multi-   │ │(Google   │ │ (Whisper +  │  ║
║  │(Whoosh + │ │WhatsApp)│ │step exec)│ │Calendar) │ │  Summary)   │  ║
║  │ Sentence │ │         │ │          │ │          │ │             │  ║
║  │Transformr│ │         │ │          │ │          │ │             │  ║
║  └──────────┘ └─────────┘ └──────────┘ └──────────┘ └─────────────┘  ║
╚════════════════════════════════════════════════════════════════════════╝
                                 │
╔════════════════════════════════╪═══════════════════════════════════════╗
║             MEMORY & DATA LAYER│                                        ║
║  ┌───────────────┐  ┌──────────▼──────────┐  ┌─────────────────────┐  ║
║  │  SQLite DB    │  │  Vector Store        │  │   File Index        │  ║
║  │  (Tasks,      │  │  (ChromaDB — local)  │  │   (Whoosh —         │  ║
║  │  Contacts,    │  │  (Semantic memory,   │  │    local)           │  ║
║  │  Prefs,       │  │   embeddings,        │  │                     │  ║
║  │  Reminders,   │  │   conversation ctx)  │  │                     │  ║
║  │  Logs)        │  │                      │  │                     │  ║
║  └───────────────┘  └──────────────────────┘  └─────────────────────┘  ║
╚═════════════════════════════════════════════════════════════════════════╝
                                 │
╔════════════════════════════════╪═══════════════════════════════════════╗
║         EXTERNAL INTEGRATIONS  │                                        ║
║  ┌──────────┐ ┌────────────┐ ┌─▼──────────┐ ┌────────────────────┐   ║
║  │  Gmail   │ │  WhatsApp  │ │  Google    │ │  Anthropic /       │   ║
║  │  SMTP /  │ │  Business  │ │  Calendar  │ │  OpenAI API        │   ║
║  │  IMAP    │ │  API /     │ │  API       │ │  (Paid Mode Only)  │   ║
║  │          │ │  Twilio    │ │            │ │                    │   ║
║  └──────────┘ └────────────┘ └────────────┘ └────────────────────┘   ║
╚════════════════════════════════════════════════════════════════════════╝
```

### 2.2 Component Connectivity Summary

All components communicate through a central **Internal API Bus** running on localhost. The Voice Layer converts audio to text and passes it to the Intelligence Layer as a plain text string. The Intelligence Layer routes through the AI Model Router, produces an intent object and action plan, and dispatches steps to the appropriate Action Modules. Each Action Module writes results back to the Memory Layer and returns a response string to the Voice or Text interface. The Frontend Dashboard reads state directly from the SQLite database and subscribes to Server-Sent Events for real-time updates.

---

## 3.0 Architecture Pattern

### 3.1 Selected Pattern: Modular Monolith with Service Boundaries

Alex v1.0 is built as a **modular monolith** — a single deployable process composed of clearly separated internal modules, each with defined interfaces and responsibilities.

This pattern was selected over a full microservices architecture for the following reasons:

**Simplicity of local deployment.** Alex must run on a single user's machine without requiring container orchestration, service mesh configuration, or inter-process networking. A monolith with module boundaries achieves the same separation of concerns without that operational overhead.

**Performance for single-user workloads.** Inter-process communication via HTTP adds latency that is unnecessary when all services are serving a single concurrent user. In-process function calls are dramatically faster for the voice response latency target of under two seconds.

**Upgrade path preserved.** The modular design ensures that any individual module — particularly the AI Model Router and the Communication Engine — can be extracted into a standalone service in v1.1 without disrupting the rest of the system.

**Hybrid AI constraint compatibility.** The AI Model Router runs as an in-process abstraction that can call either a local Ollama endpoint or a remote Claude/OpenAI API without requiring an architecture change.

### 3.2 Runtime Process Model

```
alex-core (main process)
  ├── voice_listener        (background thread — mic capture + STT)
  ├── wake_word_detector    (background thread — always on, low CPU)
  ├── api_server            (FastAPI — localhost:8000)
  ├── scheduler             (APScheduler — reminders, briefings, indexing)
  └── file_watcher          (Watchdog — real-time file index updates)
```

The API server is the internal bus. All modules — including the dashboard frontend — communicate exclusively through it. No module holds a direct reference to another module's internal state.

---

## 4.0 Component Breakdown

### 4.1 Voice Layer

The Voice Layer is Alex's primary I/O interface. It operates as two independent background threads — one for capture and transcription, one for synthesis — managed by the main process.

**Wake Word Detection**

| Attribute | Detail |
|-----------|--------|
| Library | Porcupine by Picovoice (free tier) |
| Mode | Always-on, offline, < 5% CPU |
| Trigger | Custom wake word "Hey Alex" |
| Fallback | OpenWakeWord (fully open-source alternative) |
| Output | Binary trigger signal → activates STT listener |

**Speech-to-Text (STT)**

| Attribute | Free Mode | Paid Mode |
|-----------|-----------|-----------|
| Library | OpenAI Whisper (local, `whisper-base` or `whisper-small`) | OpenAI Whisper API |
| Runtime | Python `faster-whisper` for CPU-optimized inference | REST call to OpenAI endpoint |
| Latency | 1–3 seconds for short commands | ~0.5 seconds |
| Language | English (v1.0) | English (v1.0) |
| Output | Plain text transcription |

**Text-to-Speech (TTS)**

| Attribute | Free Mode | Paid Mode |
|-----------|-----------|-----------|
| Library | Coqui TTS (VITS model, local) | ElevenLabs API |
| Voice quality | Natural; slightly robotic | Near-human |
| Latency | ~1 second | ~0.3 seconds |
| Output | WAV audio stream → speakers |

**Voice Layer API Contract**

The Voice Layer exposes two internal events on the event bus:

```
EVENT: voice.transcription_ready
PAYLOAD: { text: string, timestamp: ISO8601, confidence: float }

EVENT: voice.tts_requested
PAYLOAD: { text: string, priority: "normal" | "urgent" }
```

---

### 4.2 Intelligence Layer

The Intelligence Layer is the cognitive core of Alex. It receives text input from either the Voice Layer or the text chat interface, resolves intent, plans multi-step actions, and dispatches those actions to the appropriate modules.

**4.2.1 Intent Parser**

The Intent Parser is responsible for transforming raw user text into a structured intent object. It uses the AI Model Router to perform this classification.

```
Input:  "Find the Q1 report and email it to Priya"

Output (Intent Object):
{
  "intent": "multi_step_task",
  "steps": [
    { "action": "file_search",   "query": "Q1 report" },
    { "action": "send_email",    "recipient": "Priya", "attach": "{{step_1_result}}" }
  ],
  "entities": {
    "contacts": ["Priya"],
    "files":    ["Q1 report"]
  },
  "requires_confirmation": true,
  "ambiguity_score": 0.12
}
```

If `ambiguity_score` exceeds 0.4, the system generates a single clarifying question rather than proceeding. It never refuses an ambiguous command — it always asks one question and continues.

**4.2.2 AI Model Router**

The AI Model Router is the abstraction layer that decouples all other components from any specific AI provider. It is the only component in Alex that is aware of which model is active.

```
┌─────────────────────────────────────────┐
│            AI Model Router              │
│                                         │
│   config.ai_mode = "free" | "paid"      │
│                                         │
│   if free:                              │
│     → POST http://localhost:11434/api   │  (Ollama)
│       model: mistral:7b                 │
│       or:    llama3.1:8b                │
│                                         │
│   if paid:                              │
│     → POST api.anthropic.com/v1/messages│  (Claude)
│       or: api.openai.com/v1/chat        │  (GPT-4o)
│                                         │
│   Interface is identical to callers.    │
│   Hot-switching: config change only.    │
│   No restart required.                  │
└─────────────────────────────────────────┘
```

**Model Selections**

| Mode | Primary Model | Fallback Model | Use Case |
|------|--------------|----------------|----------|
| Free | Mistral 7B (via Ollama) | LLaMA 3.1 8B (via Ollama) | Intent parsing, summarization, generation |
| Paid | Claude claude-sonnet-4-20250514 (Anthropic) | GPT-4o (OpenAI) | Enhanced reasoning, complex multi-step tasks |

**4.2.3 Task Planner**

The Task Planner converts the Intent Parser's output into an ordered execution plan. It handles dependency resolution — ensuring, for example, that a file search completes before an email send that attaches the result.

```
Execution Plan (internal format):
{
  "plan_id": "uuid",
  "steps": [
    { "step_id": 1, "action": "file_search",  "params": {...}, "depends_on": [] },
    { "step_id": 2, "action": "send_email",   "params": {...}, "depends_on": [1] }
  ],
  "confirmation_required": true,
  "created_at": "ISO8601"
}
```

If `confirmation_required` is true, the Task Planner serializes the plan as a human-readable preview and returns it to the user for approval before any action is executed.

---

### 4.3 Memory & Database Layer

Alex uses a two-store memory architecture: a relational store (SQLite) for structured data and a vector store (ChromaDB) for semantic memory and conversation context.

**SQLite** is the source of truth for all structured, queryable data — tasks, contacts, reminders, calendar events, preferences, and audit logs. It requires no server and runs entirely in-process.

**ChromaDB** is the local vector database for semantic memory. It stores embeddings of past conversations, user preferences expressed in natural language, and frequently accessed file metadata. This enables Alex to recall context from previous sessions without exact keyword matching.

Both stores reside on the local file system and are never transmitted externally. Full schema is defined in Section 7.0.

---

### 4.4 File & Search Layer

The File & Search Layer provides intelligent retrieval of local files. It operates in two complementary modes.

**Keyword Search (Whoosh)**

Whoosh is a pure-Python full-text search library that indexes file metadata — name, path, extension, creation date, and modification date. It supports case-insensitive queries, wildcard matching, and Boolean operators. The index is persisted to disk and updated in real time by a Watchdog file watcher.

**Semantic Search (Sentence Transformers + ChromaDB)**

For queries where the user does not know the filename, semantic search uses the `all-MiniLM-L6-v2` model from Sentence Transformers to embed the query and retrieve the most semantically similar files by content summary. File content is extracted at index time using Apache Tika (for documents) and stored as embeddings in ChromaDB.

**Search Flow**

```
User query: "the contract I sent to Priya in February"
     │
     ▼
Keyword search (Whoosh) → candidate files by name/date
     │
     ▼
Semantic re-rank (ChromaDB) → top 3 candidates by relevance
     │
     ▼
If score > 0.85 → auto-select and proceed
If score < 0.85 → present top 3 to user for selection
```

**File Watcher**

The Watchdog library monitors the user-configured watched directories. On any file creation, modification, or deletion event, it triggers an incremental index update within two seconds. No manual re-indexing is required.

---

### 4.5 Communication Layer

The Communication Layer dispatches outbound messages across two channels: email and WhatsApp.

**Email**

| Attribute | Detail |
|-----------|--------|
| Outbound | SMTP via `smtplib` (Python standard library) |
| Inbound (read) | IMAP via `imaplib` |
| Default provider | Gmail (configurable to any SMTP/IMAP provider) |
| Attachment handling | Files resolved by the File Search Layer and attached via MIME |
| Credential storage | Encrypted in SQLite using the local encryption key (see Security Document) |
| Contact resolution | `contacts` table in SQLite; fuzzy match on name or alias |

**WhatsApp**

| Attribute | Free Mode | Paid Mode |
|-----------|-----------|-----------|
| Integration | Twilio WhatsApp Sandbox (free tier) | Twilio WhatsApp Business API (paid) |
| Fallback | `whatsapp-web.js` bridge (unofficial; requires Chrome) | — |
| Attachment | Files encoded as media messages | Same |
| Latency | 2–5 seconds | 1–2 seconds |

> **Note on WhatsApp:** The free Twilio sandbox is suitable for development and personal use. For production reliability, the paid Twilio Business API is recommended but not required. The `whatsapp-web.js` bridge provides a zero-cost alternative but depends on the user maintaining an active WhatsApp Web session.

**Contact Resolution Flow**

```
User says: "Send it to Priya"
     │
     ▼
Fuzzy match "Priya" against contacts.display_name and contacts.aliases
     │
     ├── Single match (confidence > 0.9) → proceed automatically
     ├── Multiple matches → ask: "Did you mean Priya Sharma or Priya Nair?"
     └── No match → ask: "I don't have Priya's contact. What's her email?"
```

---

### 4.6 Automation Engine

The Automation Engine is responsible for executing the Task Planner's multi-step execution plans. It runs each step in sequence, passes outputs from one step as inputs to the next, handles errors at each step, and reports the final result.

**Execution Model**

```python
class AutomationEngine:
    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        context = {}
        for step in plan.steps:
            if not all(dep in context for dep in step.depends_on):
                raise DependencyError(step)
            try:
                result = self.dispatch(step, context)
                context[step.step_id] = result
            except ActionError as e:
                return ExecutionResult(
                    status="partial_failure",
                    completed_steps=list(context.keys()),
                    failed_step=step.step_id,
                    error=str(e)
                )
        return ExecutionResult(status="success", context=context)
```

**Error Handling Policy**

On step failure, the Automation Engine does not attempt to guess or retry automatically. It reports exactly which steps succeeded, which failed, and why — then waits for user instruction before attempting any recovery. This ensures the user maintains full control over consequential actions.

**Confirmation Gate**

All plans with `confirmation_required: true` are paused before execution and presented to the user as a plain-language summary. Execution only proceeds on explicit "yes" or equivalent affirmation.

---

### 4.7 Frontend / Dashboard

The dashboard is a web-based interface served locally at `http://localhost:3000`. It provides text-based chat, a task manager view, calendar summary, file search UI, settings, and memory review.

| Attribute | Detail |
|-----------|--------|
| Framework | React (Next.js — static export, no server-side rendering required) |
| Styling | Tailwind CSS |
| State | React Query for server state; Zustand for UI state |
| Real-time updates | Server-Sent Events (SSE) from FastAPI backend |
| Communication with backend | REST calls to `localhost:8000` |
| Voice indicator | Visual waveform showing when Alex is listening or speaking |

The dashboard is accessible only from `localhost`. It is not exposed to the network by default.

---

### 4.8 Monitoring & Logging

All system activity is logged to the `audit_logs` table in SQLite and simultaneously to a rotating log file on disk.

| Log Type | Content | Retention |
|----------|---------|-----------|
| Command log | Raw input, parsed intent, execution plan, result | 90 days |
| Action log | Each step executed, status, duration | 90 days |
| Error log | Stack traces, failed steps, recovery actions | 180 days |
| Performance log | Latency per component, model inference time | 30 days |

**Metrics Dashboard (v1.0)**

A lightweight metrics endpoint at `GET /metrics` returns a JSON payload with key performance indicators: intent accuracy (user-corrected vs. accepted), task completion rate, average response latency, and model mode (free/paid). This feeds a simple dashboard panel accessible from the frontend.

---

## 5.0 Data Flow

### 5.1 Standard Request → Process → Response Cycle

The following describes the complete lifecycle of a voice command from capture to response.

```
Step 1: CAPTURE
  User speaks "Hey Alex, email the Q1 report to Priya"
  └─ Wake word detector fires → STT listener activates
  └─ Whisper transcribes audio → text string produced

Step 2: PARSE
  Text sent to Intent Parser via internal event
  └─ AI Model Router called with prompt template + user text
  └─ Model returns structured intent JSON
  └─ Intent Parser validates and enriches with entity resolution

Step 3: PLAN
  Intent object passed to Task Planner
  └─ Multi-step plan constructed:
       Step A: file_search("Q1 report")
       Step B: send_email(to="Priya", attach=Step_A_result)
  └─ Plan serialized as human-readable confirmation request

Step 4: CONFIRM
  Confirmation request sent to Voice Layer as TTS:
  "I'll search for the Q1 report and email it to Priya.
   Should I go ahead?"
  └─ User responds "Yes"
  └─ Confirmation captured and validated

Step 5: EXECUTE
  Automation Engine executes plan:
  └─ Step A: File Search Engine queries Whoosh index
             → returns /docs/Q1_Report_2026.pdf (confidence: 0.97)
  └─ Step B: Communication Layer composes email
             → contact resolved: priya@example.com
             → file attached as MIME attachment
             → SMTP send executed
             → delivery confirmation received

Step 6: LOG & MEMORIZE
  └─ Command, plan, and result written to audit_logs
  └─ Interaction summary embedded and stored in ChromaDB
  └─ Contact "Priya" interaction frequency updated in SQLite

Step 7: RESPOND
  └─ TTS synthesizes: "Done. I've emailed the Q1 report to Priya."
  └─ Dashboard updates task history in real time via SSE
```

### 5.2 Morning Briefing Data Flow

```
APScheduler fires at configured briefing time (e.g., 7:30 AM)
  └─ Briefing Composer queries:
       ├─ SQLite: tasks due today + overdue tasks
       ├─ SQLite: reminders for today
       ├─ Google Calendar API: today's events
       └─ IMAP: unread emails flagged as priority
  └─ Briefing Composer sends all data to AI Model Router
  └─ Model generates concise natural-language briefing
  └─ TTS synthesizes and plays briefing audio
  └─ Dashboard displays briefing text simultaneously
```

### 5.3 File Indexing Data Flow

```
Watchdog detects new file: /docs/contract_ACME_2026.pdf
  └─ File metadata extracted (name, path, size, dates)
  └─ Apache Tika extracts text content
  └─ Sentence Transformer generates embedding vector
  └─ Whoosh index updated (keyword metadata)
  └─ ChromaDB updated (semantic embedding)
  └─ Index update logged
Total time: < 2 seconds for typical document
```

---

## 6.0 API Design

Alex's internal API runs on FastAPI at `localhost:8000`. All endpoints are authenticated with a locally generated API key stored in the user's environment. The API is not exposed beyond localhost.

### 6.1 Core Endpoints

**Command Endpoint**

```
POST /api/v1/command

Request:
{
  "input":  "Email the Q1 report to Priya",
  "source": "voice" | "text",
  "session_id": "uuid"
}

Response (pending confirmation):
{
  "status":      "awaiting_confirmation",
  "plan_id":     "uuid",
  "preview":     "I'll search for the Q1 report and email it to Priya.",
  "plan_steps":  [
    { "step": 1, "action": "file_search", "description": "Search for Q1 report" },
    { "step": 2, "action": "send_email",  "description": "Email to Priya (priya@example.com)" }
  ]
}

Response (completed):
{
  "status":    "success",
  "response":  "Done. I've emailed the Q1 report to Priya.",
  "actions":   ["file_search", "send_email"],
  "duration_ms": 1840
}
```

**Confirmation Endpoint**

```
POST /api/v1/confirm

Request:
{
  "plan_id":  "uuid",
  "decision": "confirm" | "cancel" | "modify"
}

Response:
{
  "status":   "executing" | "cancelled",
  "plan_id":  "uuid"
}
```

**File Search Endpoint**

```
GET /api/v1/files/search?q={query}&limit={n}&mode=keyword|semantic|hybrid

Response:
{
  "results": [
    {
      "file_id":    "uuid",
      "name":       "Q1_Report_2026.pdf",
      "path":       "/Users/user/Documents/Q1_Report_2026.pdf",
      "relevance":  0.97,
      "modified":   "2026-02-14T10:00:00Z",
      "size_bytes": 204800
    }
  ],
  "total": 1,
  "mode_used": "hybrid"
}
```

**Task Endpoints**

```
GET    /api/v1/tasks?status=pending|completed|overdue
POST   /api/v1/tasks          { title, due_date, priority, notes }
PATCH  /api/v1/tasks/{id}     { status, due_date, notes }
DELETE /api/v1/tasks/{id}

GET    /api/v1/reminders
POST   /api/v1/reminders      { message, trigger_at, repeat }
DELETE /api/v1/reminders/{id}
```

**Memory & Preferences Endpoints**

```
GET    /api/v1/memory/preferences
PATCH  /api/v1/memory/preferences   { key, value }
DELETE /api/v1/memory/preferences/{key}

GET    /api/v1/memory/history?limit=50
DELETE /api/v1/memory/history        (wipes conversation memory)
```

**Settings Endpoint**

```
GET   /api/v1/settings
PATCH /api/v1/settings

Patchable fields:
{
  "ai_mode":          "free" | "paid",
  "paid_provider":    "anthropic" | "openai",
  "briefing_time":    "HH:MM",
  "watched_dirs":     ["/path/one", "/path/two"],
  "voice_enabled":    true | false,
  "tts_voice":        "default" | "custom_id",
  "confirm_actions":  true | false
}
```

**System-Sent Events Stream**

```
GET /api/v1/events   (text/event-stream)

Event types:
  alex.response_ready     → new assistant message available
  alex.action_completed   → an action step finished
  alex.action_failed      → an action step failed
  alex.briefing_ready     → morning briefing generated
  alex.reminder_triggered → a reminder is due
```

---

## 7.0 Database Schema

### 7.1 SQLite Schema

All tables reside in a single SQLite file: `~/.alex/alex.db`.

**contacts**
```sql
CREATE TABLE contacts (
  id           TEXT PRIMARY KEY,          -- UUID
  display_name TEXT NOT NULL,
  aliases      TEXT,                      -- JSON array of nicknames
  email        TEXT,
  phone        TEXT,
  whatsapp_id  TEXT,
  frequency    INTEGER DEFAULT 0,         -- interaction count for ranking
  notes        TEXT,
  created_at   TEXT NOT NULL,
  updated_at   TEXT NOT NULL
);
```

**tasks**
```sql
CREATE TABLE tasks (
  id           TEXT PRIMARY KEY,
  title        TEXT NOT NULL,
  description  TEXT,
  status       TEXT DEFAULT 'pending',    -- pending | in_progress | completed | overdue
  priority     TEXT DEFAULT 'normal',     -- low | normal | high | urgent
  due_date     TEXT,                      -- ISO8601
  source       TEXT,                      -- "voice" | "meeting" | "manual"
  meeting_id   TEXT,                      -- FK → meetings.id (nullable)
  created_at   TEXT NOT NULL,
  updated_at   TEXT NOT NULL
);
```

**reminders**
```sql
CREATE TABLE reminders (
  id           TEXT PRIMARY KEY,
  message      TEXT NOT NULL,
  trigger_at   TEXT NOT NULL,             -- ISO8601
  repeat       TEXT DEFAULT 'none',       -- none | daily | weekly
  status       TEXT DEFAULT 'active',     -- active | triggered | dismissed
  task_id      TEXT,                      -- FK → tasks.id (nullable)
  created_at   TEXT NOT NULL
);
```

**meetings**
```sql
CREATE TABLE meetings (
  id               TEXT PRIMARY KEY,
  title            TEXT,
  started_at       TEXT NOT NULL,
  ended_at         TEXT,
  transcript_path  TEXT,                  -- path to raw transcript file
  summary          TEXT,                  -- AI-generated summary
  action_items     TEXT,                  -- JSON array of extracted action items
  participants     TEXT,                  -- JSON array of names
  created_at       TEXT NOT NULL
);
```

**calendar_events**
```sql
CREATE TABLE calendar_events (
  id              TEXT PRIMARY KEY,
  external_id     TEXT,                   -- Google Calendar event ID
  title           TEXT NOT NULL,
  description     TEXT,
  start_time      TEXT NOT NULL,
  end_time        TEXT NOT NULL,
  location        TEXT,
  attendees       TEXT,                   -- JSON array
  provider        TEXT DEFAULT 'google',
  synced_at       TEXT NOT NULL
);
```

**preferences**
```sql
CREATE TABLE preferences (
  key          TEXT PRIMARY KEY,
  value        TEXT NOT NULL,             -- JSON-encoded value
  category     TEXT,                      -- "communication" | "voice" | "search" | "system"
  updated_at   TEXT NOT NULL
);
```

**file_index**
```sql
CREATE TABLE file_index (
  id            TEXT PRIMARY KEY,
  name          TEXT NOT NULL,
  path          TEXT NOT NULL UNIQUE,
  extension     TEXT,
  size_bytes    INTEGER,
  content_hash  TEXT,                     -- SHA256 for change detection
  indexed_at    TEXT NOT NULL,
  modified_at   TEXT NOT NULL
);
```

**audit_logs**
```sql
CREATE TABLE audit_logs (
  id            TEXT PRIMARY KEY,
  session_id    TEXT NOT NULL,
  input_text    TEXT,
  intent        TEXT,                     -- JSON intent object
  plan          TEXT,                     -- JSON execution plan
  result        TEXT,                     -- JSON result
  status        TEXT,                     -- success | partial_failure | failure | cancelled
  duration_ms   INTEGER,
  ai_mode       TEXT,                     -- free | paid
  model_used    TEXT,
  created_at    TEXT NOT NULL
);
```

### 7.2 ChromaDB Collections

ChromaDB runs locally at `~/.alex/chroma/`. Two collections are maintained.

**collection: `conversation_memory`**

Stores embeddings of past interactions for semantic recall across sessions.

```
document:  Full text of past interaction (input + response)
metadata:  { session_id, timestamp, intent, actions_taken }
embedding: all-MiniLM-L6-v2 vector (384 dimensions)
```

**collection: `file_semantic_index`**

Stores embeddings of file content summaries for semantic file search.

```
document:  Extracted text content or summary (first 512 tokens)
metadata:  { file_id, name, path, extension, modified_at }
embedding: all-MiniLM-L6-v2 vector (384 dimensions)
```

### 7.3 Entity Relationships

```
contacts ──────────────── audit_logs
    │                         │
    │                         │ (session tracing)
    ▼                         ▼
tasks ────── reminders    meetings
    │                         │
    └─────────────────────────┘
              (action items from meetings → tasks)

calendar_events ← (synced from Google Calendar API)
preferences     ← (read by all components at runtime)
file_index      ← (maintained by File & Search Layer)
```

---

## 8.0 Integration Points

### 8.1 Google Calendar

| Attribute | Detail |
|-----------|--------|
| API | Google Calendar API v3 |
| Auth | OAuth 2.0 (user grants access during onboarding) |
| Scope | `calendar.readonly` for read; `calendar.events` for write |
| Sync direction | Bidirectional (read availability, write new events) |
| Refresh | Polled every 5 minutes by the APScheduler background job |
| Local cache | Stored in `calendar_events` SQLite table |
| Provider scope | Google Calendar only in v1.0; multi-provider deferred |

### 8.2 Email (Gmail / SMTP-IMAP)

| Attribute | Detail |
|-----------|--------|
| Outbound | SMTP via port 587 with STARTTLS |
| Inbound | IMAP over SSL port 993 |
| Default provider | Gmail |
| Extensibility | Any SMTP/IMAP provider configurable via settings |
| Auth | App password or OAuth 2.0 (Gmail) |
| Credential storage | AES-256 encrypted in SQLite |
| Priority inbox | IMAP search for `FLAGGED` or `UNSEEN` messages for briefing |

### 8.3 WhatsApp

| Attribute | Free Mode | Paid Mode |
|-----------|-----------|-----------|
| Provider | Twilio WhatsApp Sandbox | Twilio Business API |
| Fallback | `whatsapp-web.js` (Chrome bridge) | — |
| Message types | Text, document, image | Same |
| Auth | Twilio account SID + auth token | Same |
| Rate limits | Sandbox: 1 message/second | Business: higher limits |

### 8.4 Local AI — Ollama (Free Mode)

| Attribute | Detail |
|-----------|--------|
| Runtime | Ollama (local model server at `http://localhost:11434`) |
| Primary model | Mistral 7B Instruct (`mistral:7b-instruct`) |
| Fallback model | LLaMA 3.1 8B Instruct (`llama3.1:8b`) |
| Hardware requirement | 8 GB RAM minimum for 7B models; 16 GB recommended |
| Quantization | Q4_K_M (4-bit quantized for CPU inference) |
| API format | OpenAI-compatible REST endpoint |

### 8.5 Paid AI APIs (Upgrade Mode)

| Provider | Model | Endpoint |
|----------|-------|----------|
| Anthropic | claude-sonnet-4-20250514 | `https://api.anthropic.com/v1/messages` |
| OpenAI | GPT-4o | `https://api.openai.com/v1/chat/completions` |

Both providers are accessed through the AI Model Router using a shared interface. API keys are stored encrypted in SQLite and never written to environment variables or config files in plaintext.

### 8.6 Speech Processing

| Function | Free Mode | Paid Mode |
|----------|-----------|-----------|
| STT | `faster-whisper` (local) | OpenAI Whisper API |
| TTS | Coqui TTS (local) | ElevenLabs API |
| Wake word | Porcupine (offline) | Porcupine (same) |
| Meeting transcription | `faster-whisper` (local) | OpenAI Whisper API |

### 8.7 Integration Health Monitoring

Each integration point is registered in a health registry checked every 60 seconds by the APScheduler. If an integration fails (e.g., SMTP timeout, Google Calendar auth expiry), the user is notified via the dashboard and, if voice is active, a brief TTS alert. The system continues operating in degraded mode for unaffected components.

---

## 9.0 Scalability Considerations

### 9.1 v1.0 Scope

Alex v1.0 is a single-user, local system. Traditional horizontal scalability is not a concern. The scalability considerations below address performance headroom and the v1.1 extraction path.

### 9.2 Performance Limits & Mitigations

| Component | Limit in v1.0 | Mitigation |
|-----------|--------------|------------|
| Ollama inference (7B model) | 5–15 tokens/sec on CPU | Response streaming; confirm UI shows progress |
| File index size | Up to ~100,000 files | Whoosh index is efficient to this scale; ChromaDB handles up to 1M vectors |
| SQLite concurrency | Single writer | All writes serialized through the API server; no concurrent user issue in v1.0 |
| SMTP send throughput | Rate-limited by provider | Queue-based dispatch; no burst sending scenario in v1.0 |
| Memory (ChromaDB) | Up to 5 GB on disk for embeddings at scale | Configurable retention; older embeddings pruned after 90 days by default |

### 9.3 v1.1 Extraction Path

The modular monolith design ensures each component can be independently extracted:

- The **AI Model Router** can be wrapped in a FastAPI microservice with a stable interface.
- The **File & Search Layer** can be moved to a dedicated process using the same internal REST API contract.
- **SQLite** can be migrated to PostgreSQL by changing the database URL — the ORM layer (SQLAlchemy) abstracts all SQL dialect differences.
- The **frontend** is already decoupled via REST and SSE; it can be deployed independently with no changes.

---

## 10.0 Open Questions

The following questions from PRD.md (OQ-1 through OQ-8) are resolved by this document where applicable, with residual items noted.

| # | Question | Resolution |
|---|----------|------------|
| OQ-1 | Default local AI model | **Resolved:** Mistral 7B via Ollama (primary); LLaMA 3.1 8B (fallback) |
| OQ-2 | WhatsApp integration mechanism | **Resolved:** Twilio Sandbox (free); Twilio Business API (paid upgrade); `whatsapp-web.js` as zero-cost fallback |
| OQ-3 | Meeting transcription without paid service | **Resolved:** `faster-whisper` running locally |
| OQ-4 | Memory storage format | **Resolved:** SQLite (structured data) + ChromaDB (vector/semantic memory) |
| OQ-5 | Offline wake word detection | **Resolved:** Porcupine by Picovoice (offline, CPU-efficient) |
| OQ-6 | Calendar integration scope | **Partially resolved:** Google Calendar API v3 in v1.0; multi-provider deferred to v1.1 |
| OQ-7 | Security model for credentials | **Open:** Addressed at architecture level (AES-256 in SQLite); full treatment in Security Document |
| OQ-8 | Desktop vs. web delivery | **Resolved:** Web-based frontend at localhost:3000; no native app in v1.0 |

**New Open Question from this document:**

| # | Question | Owner | Resolution Target |
|---|----------|-------|-------------------|
| SDD-OQ-1 | What is the minimum hardware specification for running Mistral 7B locally? Should a hardware check run during onboarding? | Engineering | Before Tech Stack Document |
| SDD-OQ-2 | Should Whisper model size (base vs. small vs. medium) be user-configurable, given the latency vs. accuracy trade-off? | Product | Before Feature List Document |
| SDD-OQ-3 | What is the data migration path if the user's SQLite database grows beyond practical size in long-term use? | Architecture | Before v1.1 planning |

---

## 11.0 Next Steps

With the System Design Document complete, the following decisions are now locked and available to downstream documents:

- Architecture pattern: modular monolith
- Local AI: Mistral 7B via Ollama; LLaMA 3.1 8B as fallback
- Paid AI: Anthropic Claude (primary); OpenAI GPT-4o (secondary)
- STT: faster-whisper (free); OpenAI Whisper API (paid)
- TTS: Coqui TTS (free); ElevenLabs (paid)
- Wake word: Porcupine (offline)
- Storage: SQLite + ChromaDB + Whoosh
- Frontend: Next.js at localhost:3000
- WhatsApp: Twilio Sandbox / whatsapp-web.js (free); Twilio Business (paid)
- Calendar: Google Calendar API v3 (v1.0 only)

The following documents are to be authored next, in order:

1. **User Flow Document (v1.0)** — map all user journeys using the component architecture defined here. Reference the Request → Process → Response cycle from Section 5.0.
2. **Feature List Document (v1.0)** — enumerate every feature with acceptance criteria, the specific components involved, and delivery estimates.
3. **Tech Stack Requirements Document (v1.0)** — enumerate all libraries, frameworks, and services. Clearly mark each as free-mode, paid-mode, or both.
4. **Security Document (v1.0)** — address OQ-7 fully: credential encryption, access control, local data protection, and action permission model.
5. **AI Instructions Document (v1.0)** — define prompt templates for the Intent Parser, Task Planner, Briefing Composer, and all other AI-powered sub-components.

---

*Document maintained by the Alex Build Team. All decisions in this document supersede architectural assumptions made elsewhere. Version history tracked in the project changelog.*
