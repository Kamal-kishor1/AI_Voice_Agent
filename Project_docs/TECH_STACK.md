# Tech Stack Requirements Document
## Alex — Personal AI Operating System
**Version:** v1.0
**Date:** 24 March 2026
**Status:** Draft
**Author:** Alex Build Team
**References:** PRD.md v1.0, SYSTEM_DESIGN.md v1.0, GOAL.md

---

## Architecture Reconciliation Note

The System Design Document (v1.0) specified a local-first, single-machine modular monolith using SQLite and ChromaDB for fully offline operation. This Tech Stack Document incorporates confirmed technology decisions from the team — PostgreSQL + pgvector, Supabase, Redis, Railway, and Vercel — which represent a deliberate shift to a cloud-deployed, production-grade architecture.

The hybrid AI principle from the PRD is fully preserved: all core features must function without paid AI API dependency. The infrastructure shift does not violate this constraint, as Supabase, PostgreSQL, and Redis all have free tiers sufficient for v1.0 operation. System Design sections referencing SQLite and ChromaDB are superseded by the decisions recorded here. All other System Design decisions — the AI Model Router, component breakdown, and data flows — remain valid and are carried forward unchanged.

---

## Table of Contents

1.0 Purpose & Scope
2.0 Tech Stack Overview Table
3.0 Detailed Stack Breakdown
4.0 Rejected Alternatives
5.0 Cost Breakdown
6.0 Open Questions
7.0 Next Steps

---

## 1.0 Purpose & Scope

### 1.1 Purpose

This Tech Stack Requirements Document specifies every tool, framework, library, service, and platform required to build, deploy, monitor, and maintain Alex v1.0. It provides the rationale for each technology selection, documents free-tier limits and paid-tier costs, and identifies residual open questions that must be resolved before development begins.

Every selection in this document has been evaluated against three criteria carried forward from the PRD: it must support full functionality in free mode, it must not create a hard dependency on paid services for core operation, and switching between free and paid tiers must be non-disruptive to the running system.

### 1.2 Scope

This document covers the complete technology surface of Alex v1.0 across the following layers: frontend, backend, AI and intelligence, database and storage, communication, automation and integrations, infrastructure and hosting, monitoring and debugging, and development tooling. Security-specific configurations are covered in the Security Document; this document records technology selections and rationale only.

### 1.3 Decisions Carried Forward

| Source Document | Decision |
|----------------|----------|
| PRD.md | Free mode must be 100% functional without paid API dependency |
| PRD.md | Paid APIs are performance boosters, not core dependencies |
| PRD.md | Single-user system in v1.0; no multi-tenancy required |
| SYSTEM_DESIGN.md | AI Model Router abstracts all model providers behind a uniform interface |
| SYSTEM_DESIGN.md | Modular architecture; every layer communicates via the internal REST API |
| SYSTEM_DESIGN.md | WebSocket / SSE for real-time updates to the frontend |
| SYSTEM_DESIGN.md | Google Calendar API v3 for calendar integration in v1.0 |
| SYSTEM_DESIGN.md | Twilio for WhatsApp; SMTP/IMAP for email |
| SYSTEM_DESIGN.md | faster-whisper (local STT), Coqui TTS (local), Porcupine (wake word) |

---

## 2.0 Tech Stack Overview Table

| Layer | Technology | Version | Purpose | Free / Paid |
|-------|-----------|---------|---------|-------------|
| **Frontend Framework** | Next.js | 14.x (App Router) | Dashboard, chat UI, settings, routing | Free |
| **UI Components** | shadcn/ui | Latest | Accessible, composable component library | Free |
| **Styling** | Tailwind CSS | 3.x | Utility-first responsive styling | Free |
| **Client State** | Zustand | 4.x | Lightweight UI state management | Free |
| **Server State** | TanStack Query | 5.x | API caching, background re-fetching | Free |
| **Real-time (Frontend)** | Native WebSocket API | — | Streaming responses, live notifications | Free |
| **Backend Language** | Python | 3.11+ | Primary backend language | Free |
| **Backend Framework** | FastAPI | 0.111.x | REST API, WebSocket server, OpenAPI docs | Free |
| **Task Queue** | Celery | 5.x | Async job processing, scheduled tasks | Free |
| **Message Broker + Cache** | Redis | 7.x | Celery broker, response cache, event bus | Free |
| **Primary Database** | PostgreSQL | 16.x | All structured relational data | Free tier |
| **Vector Extension** | pgvector | 0.7.x | Semantic embeddings stored in Postgres | Free |
| **BaaS Platform** | Supabase | Latest | Managed Postgres, Auth (JWT), File Storage | Free tier |
| **Local LLM Runtime** | Ollama | 0.3.x | Local model server (free mode) | Free |
| **Local LLM — Primary** | Mistral 7B Instruct | Q4_K_M | Intent parsing, generation, summarization | Free |
| **Local LLM — Fallback** | LLaMA 3.1 8B | Q4_K_M | Fallback if Mistral unavailable | Free |
| **Paid AI — Primary** | Anthropic Claude API | claude-sonnet-4-20250514 | Enhanced reasoning and generation | Paid |
| **Paid AI — Secondary** | OpenAI API | GPT-4o | Alternative paid model provider | Paid |
| **Embeddings Model** | all-MiniLM-L6-v2 | 2.x | Text embeddings for semantic search | Free (local) |
| **NLP Support** | spaCy | 3.x | Entity extraction, tokenization | Free |
| **STT — Free** | faster-whisper | 1.x | Local audio transcription | Free |
| **STT — Paid** | OpenAI Whisper API | whisper-1 | Cloud transcription upgrade | Paid |
| **TTS — Free** | Coqui TTS | 0.22.x | Local voice synthesis | Free |
| **TTS — Paid** | ElevenLabs API | Latest | High-quality voice upgrade | Paid |
| **Wake Word** | Porcupine (Picovoice) | 3.x | Offline wake word detection ("Hey Alex") | Free tier |
| **File Search — Keyword** | Whoosh | 2.7.x | Full-text local file index | Free |
| **File Watcher** | Watchdog | 4.x | Real-time file system monitoring | Free |
| **Document Extraction** | Apache Tika (tika-python) | 2.x | Extract text from PDFs, DOCX, XLSX | Free |
| **Email Outbound** | smtplib (Python stdlib) | — | Send emails via SMTP | Free |
| **Email Inbound** | imaplib (Python stdlib) | — | Read inbox via IMAP | Free |
| **WhatsApp — Free** | Twilio WhatsApp Sandbox | — | WhatsApp messaging (dev / personal) | Free tier |
| **WhatsApp — Paid** | Twilio WhatsApp Business API | — | Production WhatsApp messaging | Paid |
| **Workflow Automation** | n8n | 1.x (self-hosted) | Visual workflow builder, 400+ integrations | Free (self-hosted) |
| **Calendar Integration** | Google Calendar API | v3 | Read/write calendar events | Free tier |
| **Frontend Hosting** | Vercel | — | Next.js deployment, global CDN | Free tier |
| **Backend Hosting** | Railway | — | FastAPI + Celery + Redis + n8n | Free tier |
| **Containerization** | Docker + Docker Compose | 26.x | Local dev, production parity | Free |
| **CI/CD** | GitHub Actions | — | Test, build, deploy pipeline | Free tier |
| **Error Tracking** | Sentry | Latest | Exception capture, alerting | Free tier |
| **Metrics** | Prometheus + Grafana | Latest | System metrics and dashboards | Free (self-hosted) |
| **Structured Logging** | structlog | 24.x | JSON log output, audit trail | Free |
| **API Testing** | Postman + Newman | Latest | Endpoint testing, smoke tests | Free tier |
| **API Documentation** | Swagger / OpenAPI | 3.1 | Auto-generated API docs (via FastAPI) | Free |
| **Version Control** | Git + GitHub | — | Source control, pull requests | Free |
| **Python Package Manager** | uv | Latest | Fast dependency resolution and locking | Free |
| **Node Package Manager** | pnpm | Latest | Disk-efficient Node.js package management | Free |
| **Code Quality** | Ruff + mypy + ESLint | Latest | Linting, formatting, type checking | Free |
| **Secret Management** | python-dotenv + Supabase Vault | — | Environment variables, encrypted secrets | Free |

---

## 3.0 Detailed Stack Breakdown

### 3.1 Frontend

**Framework: Next.js 14 (App Router)**

Next.js is selected as the frontend framework. The App Router, stabilized in Next.js 14, introduces React Server Components, which reduce the JavaScript bundle delivered to the browser for the initial dashboard load. For Alex's dashboard — a local web application deployed on Vercel — Next.js's static export mode allows the entire frontend to be built as a set of static files, eliminating any server-side compute cost. Vercel's CI/CD pipeline has zero-configuration support for Next.js, making deployment trivial and automatic on every push to `main`.

The choice of Next.js over a plain Vite + React SPA reflects the need for an integrated routing system, nested layouts (essential for the dashboard's multi-panel structure), and the operational alignment with Vercel as the hosting platform.

**UI Components: shadcn/ui**

shadcn/ui is a collection of accessible, composable UI components built on Radix UI primitives. Unlike Material UI or Chakra UI, shadcn/ui components are copied directly into the project codebase at generation time — there is no runtime dependency on a third-party component library, and every component can be modified freely. This gives Alex's dashboard full design ownership, which is important for building a product with a distinct personality rather than a generic AI-tool aesthetic. shadcn/ui is Tailwind-native, keeping the styling system consistent across every surface.

**Styling: Tailwind CSS 3.x**

Tailwind CSS provides utility-first styling co-located with markup. Its JIT compiler ensures the production CSS bundle contains only the classes actually used, keeping the initial page load lightweight. For a single-developer or small-team project at Alex's stage, Tailwind significantly accelerates UI development compared to writing custom stylesheets.

**State Management: Zustand + TanStack Query**

Client-side UI state — voice input active, modal open, current panel — is managed by Zustand. It is selected over Redux because it requires no boilerplate, has a minimal API surface, and integrates cleanly with React hooks without a provider hierarchy. Server state — task lists, conversation history, calendar events, file search results — is managed by TanStack Query (React Query v5), which provides automatic caching, background re-fetching, stale-while-revalidate semantics, and optimistic updates. Together these two libraries cover every state management scenario in the dashboard without overlap.

**Real-time: Native WebSocket API**

The frontend maintains a persistent WebSocket connection to the FastAPI backend to receive live updates: assistant response tokens streaming in real time, action completion events, reminder triggers, and morning briefing delivery. The browser's native WebSocket API is used directly, wrapped in a custom React hook with automatic reconnection logic. The upgrade from Server-Sent Events (noted in SYSTEM_DESIGN.md) to WebSockets is made here because WebSockets are bidirectional, which is necessary for voice state management — the frontend must send microphone-active signals to the backend, not only receive events.

---

### 3.2 Backend

**Language: Python 3.11+**

Python is the natural choice for Alex's backend. The entire AI/ML ecosystem — Hugging Face Transformers, Sentence Transformers, faster-whisper, Coqui TTS, spaCy, and the Porcupine SDK — is Python-native. Using a different backend language would require bridging to Python for all AI operations, splitting the codebase across two languages unnecessarily. Python 3.11 is specified because it introduced significant performance improvements over 3.10 (10–60% faster in CPython benchmarks) and improved exception messages that accelerate debugging.

**Framework: FastAPI 0.111.x**

FastAPI is selected as the backend framework for three primary reasons. First, it is the fastest Python web framework available, built on Starlette and Uvicorn with full async support. Second, it generates OpenAPI 3.1 documentation automatically from type-annotated route definitions and Pydantic models, which means API documentation is always in sync with the actual implementation. Third, its native WebSocket support and async request handling allow Alex to manage multiple concurrent I/O operations — a database query, an AI model call, and a file search — within a single request lifecycle without blocking.

FastAPI's dependency injection system allows the AI Model Router, database session, and user preference context to be injected into any endpoint handler cleanly, keeping components independently testable and consistent with the modular architecture defined in SYSTEM_DESIGN.md.

**Async Task Queue: Celery 5.x**

Long-running operations — sending emails, processing meeting audio, running file indexing jobs, dispatching WhatsApp messages — must not block the API server's response cycle. Celery handles these deferred operations: the API returns a `202 Accepted` immediately, the task is enqueued in Redis, and one or more Celery worker processes execute it asynchronously. When the task completes, the result is published to a Redis Stream and forwarded to the frontend via WebSocket. Celery Beat is used as the task scheduler, handling recurring jobs such as reminder checks (every minute), calendar sync (every 5 minutes), and the morning briefing generation (daily at the user's configured time). This consolidates the APScheduler mentioned in SYSTEM_DESIGN.md under the same Celery infrastructure.

**Message Broker and Cache: Redis 7.x**

Redis serves two roles simultaneously. As the Celery message broker, it queues tasks from the API server and distributes them to worker processes. As the application cache, it stores frequently accessed data — the user's preference object, recent file search results, and repeated AI model responses — with configurable TTLs to avoid redundant computation. Redis 7.x is specified for its improved multi-threading performance and native Redis Streams support. Redis Streams serve as the internal real-time event bus: action modules publish completion events to a stream, and the WebSocket handler subscribes and forwards those events to the connected frontend client.

Redis is preferred over RabbitMQ as the Celery broker because it simultaneously handles the caching responsibility, reducing the total number of services in the deployment, and is available on Railway's free tier as a managed service.

---

### 3.3 AI & Intelligence

**AI Model Router**

The AI Model Router is the single component through which all intelligence-requiring operations flow. It presents a uniform `async generate(prompt, system, temperature, max_tokens, response_format)` interface to the rest of the system, regardless of which model is active. The router reads the `ai_mode` configuration from the user's preferences at request time — not at startup — enabling hot-switching between free and paid modes without a process restart. No other component in Alex is aware of which model is currently active.

**Free Mode: Ollama + Mistral 7B Instruct (Q4_K_M)**

In free mode, the AI Model Router calls Ollama's OpenAI-compatible local API at `http://localhost:11434`. The primary model is Mistral 7B Instruct at Q4_K_M quantization, chosen because it achieves the best balance of instruction-following capability and hardware efficiency among 7B-class models. It performs reliably on intent parsing, task planning, and summarization — Alex's three primary AI workloads. The Q4_K_M quantization reduces memory consumption to approximately 4.5 GB, making the model runnable on hardware with 8 GB RAM (minimum) or 16 GB RAM (recommended). LLaMA 3.1 8B is configured as the automatic fallback, activated if Mistral fails to load or if the user explicitly selects it in settings.

**Paid Mode: Anthropic Claude API (claude-sonnet-4-20250514)**

In paid mode, the AI Model Router calls the Anthropic Messages API. The `claude-sonnet-4-20250514` model is selected as the primary paid option for its superior instruction-following quality, 200K token context window (critical for meeting transcript summarization), and reliable structured JSON output. The user must provide their own API key, stored encrypted in Supabase Vault. OpenAI GPT-4o is available as a secondary paid option, selectable via the settings panel.

**Embeddings: Sentence Transformers (all-MiniLM-L6-v2)**

Semantic search for files and conversation memory requires text embeddings. The `all-MiniLM-L6-v2` model produces 384-dimensional embeddings at approximately 14,000 sentences per second on CPU, with no GPU requirement and no network dependency. It runs locally after a one-time download from Hugging Face. Embeddings are generated at file index time and at conversation store time, then persisted in PostgreSQL via the pgvector extension. This replaces the ChromaDB collections specified in SYSTEM_DESIGN.md; the data model is equivalent, and the elimination of a separate vector database simplifies the deployment significantly.

**NLP Support: spaCy 3.x**

spaCy handles lightweight, deterministic NLP tasks that do not require a full LLM call: named entity recognition (identifying contact names, dates, and file references within a command), tokenization, and sentence boundary detection for meeting transcript post-processing. Running spaCy on these extractions before invoking the AI Model Router reduces token usage and improves latency in both free and paid modes, since a significant portion of entity extraction can be resolved deterministically without LLM inference.

**Speech-to-Text: faster-whisper (Free) / OpenAI Whisper API (Paid)**

`faster-whisper` is a CTranslate2-based reimplementation of OpenAI Whisper, achieving 2–4x faster CPU inference than the original implementation with lower peak memory usage. The `base` model is the default; users may configure `small` or `medium` via settings, trading latency for accuracy (addressing SDD-OQ-2 from SYSTEM_DESIGN.md). In paid mode, the OpenAI Whisper API replaces local inference, reducing transcription latency to under 500ms for typical command lengths.

**Text-to-Speech: Coqui TTS (Free) / ElevenLabs API (Paid)**

Coqui TTS provides local voice synthesis using the VITS model (`tts_models/en/ljspeech/vits`), producing natural-sounding speech at approximately one second per sentence on CPU. In paid mode, the ElevenLabs API provides near-human voice quality at under 500ms latency. The ElevenLabs voice ID is user-configurable via settings; a default voice is pre-selected during onboarding.

**Wake Word Detection: Porcupine (Picovoice) 3.x**

Porcupine provides always-on offline wake word detection. It runs on a dedicated background thread consuming under 5% CPU and operates with no network connectivity, satisfying the PRD's requirement for offline voice capability. The free tier supports one custom wake word ("Hey Alex") across up to three platforms. The Python SDK (`pvporcupine`) integrates directly with the Voice Layer background thread defined in SYSTEM_DESIGN.md Section 4.1.

---

### 3.4 Database & Storage

**Primary Database: PostgreSQL 16 via Supabase**

PostgreSQL 16 is the primary relational database, hosted on Supabase's managed platform. It stores all structured data: contacts, tasks, reminders, calendar events, preferences, audit logs, file metadata, and — via the pgvector extension — semantic embeddings. PostgreSQL 16 is chosen for its native `jsonb` column type (used for storing JSON arrays such as meeting participants and action items), row-level security (applicable when multi-user support is added in v1.1), full-text search capabilities, and the pgvector extension compatibility. Supabase provides automatic daily backups, connection pooling via PgBouncer, and a web-based table editor that accelerates development and debugging.

The database schema defined in SYSTEM_DESIGN.md Section 7.0 is carried forward directly, with SQLite data types replaced by PostgreSQL equivalents: `TEXT PRIMARY KEY` becomes `UUID PRIMARY KEY DEFAULT gen_random_uuid()`, and all timestamp columns use `TIMESTAMPTZ` for timezone-aware storage.

**Vector Storage: pgvector 0.7.x**

pgvector is installed as a PostgreSQL extension in the Supabase instance, replacing the separate ChromaDB deployment specified in SYSTEM_DESIGN.md. Two vector columns consolidate what were previously two ChromaDB collections: `conversation_memory.embedding vector(384)` for past interaction embeddings, and `file_semantic_index.content_embedding vector(384)` for file content embeddings. Similarity queries use pgvector's `<=>` cosine distance operator. An IVFFlat index is created on both columns once the row count exceeds 1,000 to maintain query performance as the dataset grows.

The consolidation of vector and relational storage into a single PostgreSQL instance eliminates a second database service to operate, back up, and monitor — a meaningful simplification for a v1.0 deployment.

**File Storage: Supabase Storage**

Supabase Storage provides an S3-compatible object storage API with access control policies integrated with Supabase Auth. Two buckets are provisioned for v1.0: `user-files` (documents explicitly uploaded by the user to Alex, such as attachments for email composition) and `meeting-recordings` (raw audio files from Meeting Copilot sessions, retained for re-transcription). Local file system indexing via Watchdog and Whoosh continues to operate for files that remain on the user's local machine and are not uploaded; these are indexed by metadata only and do not require cloud upload.

**Cache: Redis 7.x**

Redis serves as the application cache in addition to its role as the Celery message broker. Frequently accessed data — the user's preference object, recent file search results (60-second TTL), and calendar event snapshots (5-minute TTL) — is cached in Redis to avoid redundant database queries and AI model calls for repeated or near-identical requests. Redis Streams serve as the real-time event pipeline between action modules and the WebSocket handler.

---

### 3.5 Communication Layer

**Email: Python stdlib (smtplib + imaplib)**

Outbound email uses Python's standard library `smtplib` with STARTTLS encryption over port 587. Inbound email reading — for the morning briefing's priority inbox summary — uses `imaplib` over SSL on port 993. No third-party email library is required for v1.0. Gmail is the default provider; any SMTP/IMAP provider is configurable via the settings panel. Email credentials are stored encrypted in Supabase Vault. For v1.1, SendGrid or Resend are candidates for transactional email with delivery tracking, but this is out of scope for v1.0.

**WhatsApp: Twilio**

Twilio's WhatsApp Sandbox (free tier) provides WhatsApp messaging capability for personal use in v1.0. Messages and file attachments are dispatched via the Twilio Python SDK. The free sandbox requires recipients to send an opt-in message to the sandbox number before they can receive messages — acceptable for v1.0 given the personal-use scope, but acknowledged as a limitation in Section 6.0.

For production-grade messaging without the opt-in limitation, the Twilio WhatsApp Business API is the paid upgrade path. The underlying API client code is identical; only the sender number and account credentials differ, making the upgrade transparent to the rest of the system.

**Push Notifications: WebSocket + Web Notifications API**

In-app notifications — reminder alerts, action completion confirmations, briefing availability — are delivered to the frontend via the persistent WebSocket connection. For browser notifications when the dashboard is not in the foreground, the Web Notifications API (requiring one-time user permission grant) is used, requiring no external notification service.

---

### 3.6 Automation & Integrations

**Workflow Automation: n8n 1.x (Self-Hosted)**

n8n is deployed as a self-hosted Docker container on Railway alongside the FastAPI backend. It provides a visual workflow builder with over 400 pre-built integrations, enabling Alex to trigger external workflows — posting a Slack summary after a meeting is processed, creating a linear task from an extracted action item, or updating a Notion page — without writing custom integration code for each service.

n8n is chosen over Zapier and Make because it is fully open-source and self-hostable at zero per-execution cost. The FastAPI backend triggers n8n workflows by sending HTTP webhook events when specific actions complete. n8n handles all downstream integration logic. Workflow definitions are exported as JSON files and committed to the repository under `n8n-workflows/`, ensuring version control of automation logic.

A critical deployment note: n8n defaults to a local SQLite file for workflow and execution history persistence. On Railway's ephemeral filesystem, this data would be lost on redeploy. n8n must be configured to use the Supabase PostgreSQL instance as its backing store (addressed in Section 6.0, TS-OQ-3).

**Google Calendar API v3**

Calendar integration uses the Google Calendar API v3 with OAuth 2.0 authentication. The `google-auth` and `google-api-python-client` Python libraries handle authentication token management and API calls. The OAuth refresh token is stored encrypted in Supabase Vault. A Celery Beat task polls calendar events every 5 minutes and caches the result in the `calendar_events` PostgreSQL table. Event creation (booking meetings) uses the `events.insert` method. Google Calendar is the only provider in v1.0; multi-provider support (Outlook Calendar, iCal) is deferred to v1.1 as specified in SYSTEM_DESIGN.md.

**API Testing: Postman + Newman**

Postman is used for endpoint testing, collection management, and post-deployment smoke testing. A Postman collection is maintained for every API endpoint group defined in SYSTEM_DESIGN.md Section 6.0: Command & Confirmation, File Search, Tasks & Reminders, Calendar, Communication, Memory & Preferences, Settings, and Health. The collection is exported as `postman_collection.json` and committed to the repository. Newman, Postman's CLI runner, executes this collection in the GitHub Actions pipeline after each deployment as the final smoke test stage, ensuring every critical endpoint is functional before traffic is routed to the new build.

---

### 3.7 Infrastructure & Hosting

**Frontend Hosting: Vercel**

The Next.js frontend is deployed to Vercel. Vercel provides zero-configuration CI/CD for Next.js, automatic HTTPS, a global CDN, and preview deployments for every pull request (enabling design review before merging). The frontend is built in Next.js static export mode (`output: 'export'`), producing a fully static HTML/JS/CSS bundle with no server-side compute required. This keeps the deployment entirely within Vercel's free tier regardless of traffic volume. Environment variables — Supabase URL, Supabase anon key, WebSocket endpoint — are configured in Vercel's environment variable manager and injected at build time.

**Backend Hosting: Railway**

The FastAPI backend, Celery workers, Redis, and n8n are deployed on Railway as separate services within a single project. Railway is chosen over Render because it provides native Docker Compose support, private internal networking between services (eliminating inter-service data transfer costs and reducing latency), persistent volumes for Redis and n8n data, and a more developer-friendly deployment dashboard. The five-service deployment model is:

```
Railway Project: alex-backend
  ├── Service: api      (FastAPI + Uvicorn)
  ├── Service: worker   (Celery worker)
  ├── Service: beat     (Celery beat scheduler)
  ├── Service: redis    (Redis 7-alpine)
  └── Service: n8n      (n8nio/n8n:latest)
```

All services communicate over Railway's private internal network. Only the `api` service is exposed to the public internet, on the Railway-assigned HTTPS URL.

**Containerization: Docker + Docker Compose**

All backend services are containerized with Docker. A `docker-compose.yml` at the repository root defines the complete local development environment, enabling any developer to run the full Alex stack with a single `docker compose up` command. The same Docker images used in local development are pushed to GitHub Container Registry and deployed to Railway, ensuring complete development-to-production environment parity.

Ollama is included in the Docker Compose configuration for local development (where free-mode AI runs locally) but is excluded from the Railway deployment. This distinction — and its implications for free-mode users accessing Alex via the hosted web frontend — is addressed in Section 6.0, TS-OQ-1.

**CI/CD: GitHub Actions**

GitHub Actions orchestrates the complete build and deploy pipeline. On every push to `main`, the pipeline runs in seven sequential stages: lint (Ruff, mypy, ESLint), test (pytest, Vitest), Docker build, image push to GitHub Container Registry, Railway API deployment, Vercel frontend deployment (via Vercel's GitHub integration, triggered automatically), and Newman smoke test. On pull requests, only lint and test stages run — no deployment is triggered. This prevents broken builds from reaching production while keeping the deployment process fully automated for validated changes.

---

### 3.8 Monitoring & Debugging

**Error Tracking: Sentry**

Sentry is integrated into both the FastAPI backend and the Next.js frontend. The Python `sentry-sdk` package is initialized with FastAPI and Celery integrations, capturing unhandled exceptions, slow database queries, and Celery task failures with full stack traces and request context. The `@sentry/nextjs` package captures JavaScript errors and Core Web Vitals on the frontend. Sentry is configured to alert via email (and optionally Slack, via n8n) when the error rate exceeds five errors per hour for any endpoint, when a Celery task fails more than three consecutive times, or when API response time exceeds three seconds.

**Metrics: Prometheus + Grafana (Self-Hosted on Railway)**

Prometheus scrapes metrics from the FastAPI application every 15 seconds via the `/metrics` endpoint, exposed by the `prometheus-fastapi-instrumentator` library. Metrics collected include: HTTP request count and latency by endpoint (p50, p95, p99), active WebSocket connections, Celery task queue depth by queue name, Redis memory usage, and AI model inference latency segmented by provider (free vs. paid). Grafana is deployed alongside Prometheus on Railway, connected as a Prometheus data source. Four dashboards are provisioned out-of-the-box: System Overview, API Performance, AI Model Performance, and Communication Delivery (email and WhatsApp success rates). Grafana is accessible only on an authenticated internal URL not exposed publicly.

**Structured Logging: structlog**

All backend logging uses `structlog` for structured JSON output, replacing Python's standard `logging` module. Every log entry includes `timestamp`, `level`, `service`, `session_id`, `action`, `duration_ms`, and `error` fields, making logs machine-parseable and queryable. Logs are written to stdout (captured by Railway's 7-day log retention) and simultaneously to the `audit_logs` PostgreSQL table, where they persist for 90 days (general logs) and 180 days (error logs), as specified in SYSTEM_DESIGN.md.

**API Documentation: Swagger / OpenAPI 3.1**

FastAPI generates OpenAPI 3.1 documentation automatically from route definitions and Pydantic schemas, available at `GET /docs` (Swagger UI) and `GET /redoc` (ReDoc). In production, these endpoints are protected by the internal API key to prevent public exposure. The OpenAPI JSON schema at `GET /openapi.json` is consumed by the Postman collection sync script to keep test collections current with the actual API contract.

---

### 3.9 Development Tools

**Version Control: Git + GitHub**

The repository is hosted on GitHub (private) and follows GitHub Flow: `main` is always deployable, feature work is developed on short-lived branches, and pull requests require passing CI before merge. The repository is structured as a monorepo:

```
alex/
  ├── frontend/           (Next.js application)
  ├── backend/            (FastAPI application)
  │   ├── api/            (route handlers)
  │   ├── services/       (business logic modules)
  │   ├── models/         (Pydantic + SQLAlchemy models)
  │   ├── workers/        (Celery task definitions)
  │   └── ai/             (AI Model Router and sub-components)
  ├── n8n-workflows/      (exported n8n workflow JSON files)
  ├── docker-compose.yml
  ├── .github/workflows/  (CI/CD pipeline definitions)
  └── docs/               (all 7 documentation files)
```

**Package Management: uv (Python) + pnpm (Node.js)**

Python packages are managed with `uv`, a Rust-based package manager that resolves and installs dependencies 10–100x faster than pip and produces a `uv.lock` file for deterministic installs. Node.js packages are managed with `pnpm`, chosen for its disk-efficient `node_modules` structure and strict dependency isolation that prevents phantom dependencies. Both lock files are committed to the repository and used in CI for reproducible builds.

**Code Quality: Ruff + mypy + ESLint**

Python code is linted and formatted by Ruff, which replaces both flake8 and black in a single, significantly faster tool. Type checking is enforced by mypy in strict mode. TypeScript strict mode is enabled for all frontend code. ESLint is configured with the `next/core-web-vitals` ruleset. All linting runs in pre-commit hooks (via the `pre-commit` framework) and in the CI pipeline, ensuring no unformatted or type-unsafe code reaches `main`.

**Secret Management: python-dotenv + Supabase Vault**

Development secrets are stored in a `.env` file loaded by `python-dotenv` and are never committed to version control (enforced by `.gitignore` and a pre-commit hook that scans for accidental secret commits). Production secrets are managed in two places: Railway's environment variable manager for infrastructure secrets (DATABASE_URL, REDIS_URL, SENTRY_DSN), and Supabase Vault for user-specific sensitive data (email credentials, WhatsApp API keys, paid AI API keys). This distinction is important: infrastructure secrets belong to the deployment environment; user secrets belong to the user's data layer and must be encrypted at rest, as specified in SYSTEM_DESIGN.md.

**IDE: VS Code (Recommended)**

VS Code is the recommended IDE. The following extensions are configured in `.vscode/extensions.json`: Pylance (Python language server), Ruff (inline linting and formatting), ESLint + Prettier, Tailwind CSS IntelliSense, Docker, GitLens, and the Postman VS Code extension for inline API testing without leaving the editor. A shared `.vscode/settings.json` configures format-on-save, the Python interpreter path, and TypeScript strict mode, ensuring a consistent development experience across the team.

---

## 4.0 Rejected Alternatives

| Technology | Category | Reason for Rejection |
|-----------|----------|----------------------|
| Flask | Backend framework | No native async support; additional libraries (Flask-Async, Flask-SocketIO) required to match FastAPI's built-in capabilities, adding complexity without benefit. |
| Django | Backend framework | ORM, admin, and middleware overhead is unnecessary for Alex's API-first, single-user architecture. FastAPI provides equivalent routing and validation at a fraction of the footprint. |
| Express.js / Node.js | Backend language + framework | All AI/ML dependencies are Python-native. Node.js would require a Python subprocess or sidecar for AI operations, splitting the codebase across two languages unnecessarily. |
| ChromaDB | Vector store | Superseded by pgvector. Consolidating vector and relational storage in a single PostgreSQL instance eliminates a separate database to operate, back up, and monitor, simplifying the deployment significantly. |
| SQLite | Primary database | Appropriate for local-only single-user systems but lacks the concurrent connections, row-level security, vector extensions, and managed hosting required for the cloud-deployed architecture. Superseded by PostgreSQL via Supabase. |
| Pinecone | Vector database | Managed vector-only database with no free production tier. pgvector achieves equivalent functionality within the existing PostgreSQL infrastructure at zero additional cost. |
| Firebase (Firestore) | BaaS | Firebase uses NoSQL (Firestore), which is a poor fit for Alex's highly relational data model — tasks linked to meetings, reminders linked to tasks, contacts linked to interaction history. Supabase provides PostgreSQL with equivalent developer experience. |
| Zapier / Make | Workflow automation | Both are cloud-only SaaS platforms with per-task pricing that escalates with volume. n8n self-hosted provides identical integration capabilities at zero per-execution cost, consistent with the free-mode-first principle. |
| Render | Backend hosting | Railway is preferred for its native Docker Compose support, private internal networking, persistent volumes, and more generous free compute allowance. Render's free tier suspends inactive services, which would disrupt Celery workers and scheduled briefing delivery. |
| RabbitMQ | Message broker | A capable Celery broker but requires a separate deployment with its own management overhead. Redis serves both the broker and cache roles simultaneously, reducing service count. |
| LangChain | LLM orchestration | Adds significant abstraction overhead and has historically had frequent breaking changes between minor versions. Alex's AI Model Router is a simple, stable abstraction that does not require LangChain's full agent and chain framework. Direct API calls are more maintainable and performant for Alex's specific workloads. |
| Vite + plain React | Frontend | Lacks the integrated routing, layout system, and Vercel deployment optimization that Next.js provides. Assembling an equivalent setup with React Router and manual CI/CD configuration adds unnecessary setup work. |
| Chakra UI | UI components | Requires a JavaScript runtime CSS-in-JS dependency and theme provider. shadcn/ui is Tailwind-native with no runtime overhead, and ships component source code directly into the project for full customization control. |
| Deepgram | Speech-to-Text | Cloud-only with no free production tier. faster-whisper runs locally at zero cost and matches Deepgram's accuracy on English transcription at the `small` model size. |
| ElevenLabs (free mode) | Text-to-Speech | Requires an API key and internet connectivity, violating the free-mode offline-capable requirement. Coqui TTS provides equivalent functionality locally at no cost. |
| ARQ | Task queue | A simpler async Redis queue for Python, but lacks Celery Beat's mature scheduling capabilities, which are required for reminder firing, calendar sync, and briefing generation. |

---

## 5.0 Cost Breakdown

### 5.1 Free Tier Limits by Service

| Service | Free Tier Limits | Notes |
|---------|-----------------|-------|
| Supabase | 500 MB database, 1 GB file storage, 50,000 MAU, 2 GB bandwidth/month, daily backups | Well within single-user v1.0 requirements |
| Vercel | 100 GB bandwidth/month, unlimited deployments, 6,000 build minutes/month | Single-user frontend needs are a fraction of this limit |
| Railway | $5 free credit/month (~500 compute hours at shared CPU) | Covers API + Celery + Redis + n8n for low-traffic personal use |
| Redis (Railway) | Included within Railway's free credit | No separate Redis hosting cost |
| Sentry | 5,000 errors/month, 10,000 performance transactions/month | Sufficient for v1.0 |
| GitHub Actions | 2,000 CI/CD minutes/month (private repository) | Sufficient for moderate deployment frequency |
| Google Calendar API | 1,000,000 requests/day | No practical limit for single-user |
| Twilio WhatsApp Sandbox | Free; recipients must opt-in first | Acceptable for personal use in v1.0 |
| Gmail SMTP/IMAP | Free with a standard Google account | Standard Gmail rate limits apply |
| Porcupine (Picovoice) | 1 wake word, up to 3 platforms | Sufficient for v1.0 |
| Ollama | Fully open-source; no usage limits | Requires adequate user hardware (8 GB RAM minimum) |
| all-MiniLM-L6-v2 | Free; runs locally after one-time download | No API call or ongoing cost |
| faster-whisper | Fully open-source; no usage limits | Runs locally |
| Coqui TTS | Fully open-source; no usage limits | Runs locally |
| n8n (self-hosted) | Unlimited workflows; no per-execution charges | Hosted on Railway within the free credit |
| Postman | Unlimited collections, 25 monitors/month, unlimited manual runs | Sufficient for v1.0 development and testing |
| Prometheus + Grafana | Free; self-hosted on Railway | Consumes a portion of the Railway free credit |

### 5.2 Paid Tier Costs at Scale

| Service | Paid Trigger | Estimated Monthly Cost |
|---------|-------------|----------------------|
| Supabase Pro | Database exceeds 500 MB or storage exceeds 1 GB | $25/month (8 GB DB, 100 GB storage) |
| Railway (Hobby) | Free credit exhausted (~$5) | $5/month base + ~$0.000463/vCPU-minute used |
| Vercel Pro | >100 GB bandwidth or team features required | $20/month per user |
| Sentry Team | >5,000 errors/month | $26/month |
| Anthropic Claude API | Per token; user-activated paid mode | ~$3–15/month at typical assistant usage (claude-sonnet-4-20250514: $3.00/MTok input, $15.00/MTok output) |
| OpenAI API | Per token; user-activated paid mode | ~$5–20/month (GPT-4o: $2.50/MTok input, $10.00/MTok output) |
| OpenAI Whisper API | Per minute of audio | $0.006/minute — approximately $0.50–2.00/month at typical use |
| ElevenLabs | Per character synthesized | Starter $5/month (30K chars); Creator $22/month (100K chars) |
| Twilio WhatsApp Business | Per message | ~$0.005/message outbound — negligible at personal use volume |

### 5.3 Total Monthly Cost by Scenario

| Scenario | Monthly Cost | Description |
|----------|-------------|-------------|
| Full free mode (v1.0 launch) | $0 | All free tiers; local AI via Ollama; Twilio sandbox |
| Free infrastructure + paid AI | $15–35 | Claude API + ElevenLabs + OpenAI Whisper; free hosting tiers |
| Partial paid infrastructure | $30–60 | Supabase Pro + Railway Hobby + paid AI APIs |
| Full production (all paid tiers) | $80–120 | All paid tiers across every service |

The most common operating scenario for the target user is expected to be **free infrastructure with selective paid AI**: the user keeps Supabase and Railway on free tiers and activates Claude API and ElevenLabs when they want higher-quality responses and voice output. Estimated cost in this scenario is $15–35/month, consistent with the PRD's cost-conscious user profile.

---

## 6.0 Open Questions

| # | Question | Owner | Resolution Target |
|---|----------|-------|-------------------|
| TS-OQ-1 | Ollama is excluded from the Railway deployment. In free mode, AI inference requires Ollama running on the user's local machine. How does free-mode AI work for users who access Alex through the hosted Vercel/Railway frontend rather than running everything locally? Should the onboarding flow detect whether Ollama is available and guide users accordingly? | Architecture | Before development begins |
| TS-OQ-2 | Supabase's free tier supports pgvector, but IVFFlat index creation requires specific PostgreSQL grants. Does Supabase's shared free-tier instance allow IVFFlat index creation, or does this require the Supabase Pro plan? | Engineering | Before database provisioning |
| TS-OQ-3 | n8n defaults to a local SQLite file for workflow and execution history persistence. Railway's filesystem is ephemeral — this data will be lost on redeploy. n8n must be configured to use the Supabase PostgreSQL instance as its backing store. Is this configuration supported on n8n 1.x, and does it require any schema migrations? | Engineering | Before n8n deployment |
| TS-OQ-4 | The Twilio WhatsApp Sandbox requires recipients to opt in before receiving messages from Alex. Is this acceptable for v1.0, or should the team apply directly for a Twilio WhatsApp Business API account from the start to avoid this limitation for all contacts? | Product | Before Communication Layer development |
| TS-OQ-5 | Should the onboarding flow include an automated hardware compatibility check that verifies the user's machine meets the 8 GB RAM minimum for Ollama and offers to switch to paid AI mode if the check fails? | Product | Before onboarding flow design (User Flow Document) |
| TS-OQ-6 | The five-service Railway deployment (API, Celery worker, Celery beat, Redis, n8n) may consume the $5 monthly free credit quickly under continuous use. Should ARQ (a simpler async Redis queue) be evaluated as an alternative to Celery that would consolidate three services into two (API + Redis), reducing compute consumption? | Engineering | Before backend development begins |

---

## 7.0 Next Steps

With the Tech Stack Requirements Document complete, the following decisions are locked for all downstream development work.

The backend is Python 3.11 + FastAPI 0.111 + Celery 5 + Redis 7, hosted on Railway. The database is PostgreSQL 16 with pgvector, hosted on Supabase, replacing the SQLite + ChromaDB design from SYSTEM_DESIGN.md. File storage uses Supabase Storage. The frontend is Next.js 14 with shadcn/ui and Tailwind CSS, deployed on Vercel. All services are containerized with Docker and deployed via GitHub Actions. The AI Model Router connects to Ollama (free mode) or Anthropic Claude / OpenAI (paid mode). Monitoring uses Sentry, Prometheus, and Grafana. Workflow automation uses self-hosted n8n on Railway. API testing uses Postman with Newman in CI.

The three remaining documents to be authored are:

1. **Security Document (v1.0)** — credential encryption strategy using Supabase Vault, Supabase Row Level Security configuration, JWT validation in FastAPI, API key management, action permission model, and data retention enforcement.
2. **User Flow Document (v1.0)** — all major user journeys mapped end-to-end, specifying which API endpoint, which Celery task, and which WebSocket event is involved at each step. The Request → Process → Response cycle from SYSTEM_DESIGN.md Section 5.0 is the structural template for every flow.
3. **AI Instructions Document (v1.0)** — prompt templates for the Intent Parser, Task Planner, Briefing Composer, Meeting Summarizer, and Smart Suggestions engine. Each template must specify which model it is optimized for (free vs. paid), the expected output schema, and the fallback behavior when the model returns malformed structured output.

Open questions TS-OQ-1 (Ollama in the hosted deployment) and TS-OQ-3 (n8n persistence on Railway) are the most critical blockers and should be resolved before any backend development work begins.

---

*Document maintained by the Alex Build Team. This document supersedes SYSTEM_DESIGN.md decisions on database technology (SQLite → PostgreSQL via Supabase), vector storage (ChromaDB → pgvector), and real-time transport (SSE → WebSocket). All other SYSTEM_DESIGN.md decisions remain in force. Version history tracked in the project changelog.*
