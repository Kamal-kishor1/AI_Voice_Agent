# Tech Stack Requirements Document — Alex: Personal AI Operating System
**Version:** v1.0
**Date:** 24 March 2026
**Status:** Draft
**References:** GOAL.md, PRD.md v1.0, SYSTEM_DESIGN.md v1.0, USER_FLOW.md v1.0, FEATURE_LIST.md v1.0
**Author:** Alex Project Team

---

## Table of Contents

1. [Purpose & Scope](#10-purpose--scope)
2. [Tech Stack Overview Table](#20-tech-stack-overview-table)
3. [Detailed Stack Breakdown](#30-detailed-stack-breakdown)
   - 3.1 [Frontend](#31-frontend)
   - 3.2 [Backend](#32-backend)
   - 3.3 [AI & Intelligence](#33-ai--intelligence)
   - 3.4 [Database & Storage](#34-database--storage)
   - 3.5 [Communication Layer](#35-communication-layer)
   - 3.6 [Automation & Integrations](#36-automation--integrations)
   - 3.7 [Infrastructure & Hosting](#37-infrastructure--hosting)
   - 3.8 [Monitoring & Debugging](#38-monitoring--debugging)
   - 3.9 [Development Tools](#39-development-tools)
4. [Rejected Alternatives](#40-rejected-alternatives)
5. [Cost Breakdown](#50-cost-breakdown)
6. [Open Questions](#60-open-questions)
7. [Next Steps](#70-next-steps)

---

## 1.0 Purpose & Scope

### 1.1 Purpose

This document formalises every technology choice for Alex v1.0. It translates architecture decisions made in SYSTEM_DESIGN.md and feature requirements from FEATURE_LIST.md into specific tools, frameworks, versions, and services — with explicit reasoning for each selection over its alternatives.

This document is the reference for engineers setting up the development environment, DevOps configuring infrastructure, and anyone evaluating cost or risk in the stack.

### 1.2 Decisions Carried Forward

The following technology directions were established in earlier documentation and are now formalised here:

| Decision | Established In | Technology |
|----------|---------------|-----------|
| Mobile-first, web companion | PRD.md, SYSTEM_DESIGN.md | React Native + Next.js |
| LLM provider | SYSTEM_DESIGN.md § 4.2 | Anthropic Claude (claude-sonnet-4-20250514) |
| STT engine | SYSTEM_DESIGN.md § 4.1 | Deepgram Nova-3 (streaming) |
| TTS engine | SYSTEM_DESIGN.md § 4.1 | ElevenLabs turbo + Google TTS fallback |
| Wake word | SYSTEM_DESIGN.md § 4.1 | Porcupine by Picovoice |
| Primary database | SYSTEM_DESIGN.md § 4.3 | Supabase (PostgreSQL + pgvector) |
| Cache + queue | SYSTEM_DESIGN.md § 4.3 | Upstash Redis + BullMQ |
| Email | SYSTEM_DESIGN.md § 4.5 | Gmail API (Google OAuth 2.0) |
| WhatsApp | SYSTEM_DESIGN.md § 4.5 | Meta WhatsApp Business Cloud API |
| Architecture pattern | SYSTEM_DESIGN.md § 3 | Modular monolith (Node.js) |
| File embeddings | SYSTEM_DESIGN.md § 4.3 | OpenAI text-embedding-3-small |

### 1.3 Guiding Principles for Technology Selection

Every technology in this stack was evaluated against these criteria, in order of priority:

1. **Latency** — Does it support the ≤ 2 second voice-to-response target?
2. **Streaming support** — Can it stream responses (critical for voice UX)?
3. **Integration maturity** — Does it have well-maintained SDKs for Node.js and React Native?
4. **Cost at single-user scale** — Is it affordable at low volume with a generous free tier?
5. **Scalability path** — Can it grow to multi-user without a rewrite?
6. **Developer experience** — Is the documentation, tooling, and community strong enough to move fast?

---

## 2.0 Tech Stack Overview Table

| Layer | Technology | Version | Purpose | Why Chosen |
|-------|-----------|---------|---------|------------|
| **Mobile App** | React Native (Expo) | SDK 52 | iOS + Android app | Single codebase, native performance, large ecosystem |
| **Web Dashboard** | Next.js | 15 (App Router) | Web companion UI | Same React paradigm as mobile; SSR for performance |
| **UI Components (Mobile)** | NativeWind + Tailwind | 4.x | Styling + components | Utility-first, consistent with web styling |
| **UI Components (Web)** | shadcn/ui | Latest | Web component library | Headless, fully customisable, no vendor lock-in |
| **State Management** | Zustand | 5.x | Client state | Minimal boilerplate; simpler than Redux for this scale |
| **Backend Runtime** | Node.js | 22 LTS | Server runtime | Non-blocking I/O suits streaming + concurrent tool calls |
| **Backend Framework** | Express.js | 5.x | REST API + SSE | Lightweight, mature, full control over streaming |
| **Language** | TypeScript | 5.x | Full-stack language | Type safety across frontend + backend; reduces bugs |
| **LLM** | Anthropic Claude | claude-sonnet-4-20250514 | Intelligence core | Best tool-use + streaming; context window; safety |
| **Speech-to-Text** | Deepgram Nova-3 | API v1 | Real-time STT | Lowest latency streaming STT available; best accuracy |
| **Text-to-Speech** | ElevenLabs | eleven_turbo_v2 | Voice response | Natural voice; streaming support; < 400ms first chunk |
| **TTS Fallback** | Google Cloud TTS | WaveNet en-US | TTS fallback | Reliable, cheap, good quality fallback |
| **Wake Word** | Porcupine (Picovoice) | v3 | On-device wake word | 100% on-device; low power; cross-platform SDK |
| **Embeddings** | OpenAI Embeddings | text-embedding-3-small | File + memory vectors | Best price/quality ratio; 1536-dim; widely supported |
| **Primary DB** | Supabase (PostgreSQL) | Latest | All structured data | Postgres + realtime + auth + storage in one platform |
| **Vector Search** | pgvector (in Supabase) | 0.7.x | Semantic file + memory search | No extra service; co-located with primary DB |
| **Cache** | Upstash Redis | Serverless | Session context + rate limiting | Serverless Redis; HTTP API compatible with edge |
| **Job Queue** | BullMQ | 5.x | Background + scheduled jobs | Mature Redis-backed queue; delayed jobs; retries |
| **Email** | Gmail API (Google) | v1 | Send + read emails | Direct integration; no relay needed; OAuth secured |
| **WhatsApp** | Meta Business Cloud API | v21.0 | Send WhatsApp messages | Official API; compliant; supports media + templates |
| **Push Notifications** | Firebase Cloud Messaging | v1 | iOS + Android push | Industry standard; free; reliable delivery |
| **File Storage** | Google Drive API | v3 | Source of truth for user files | Already where user files live; no migration needed |
| **Media Storage** | Supabase Storage | Latest | TTS audio, briefing audio | Co-located; S3-compatible; CDN-backed |
| **Calendar** | Google Calendar API | v3 | Events, scheduling | Direct integration; OAuth; same credentials as Gmail |
| **Contacts** | Google People API | v1 | Contact book seeding | Pulls from Gmail contacts; OAuth |
| **Backend Hosting** | Railway | Latest | Node.js server | Always-on; no cold starts; generous free tier |
| **Web Hosting** | Vercel | Latest | Next.js web dashboard | Zero-config Next.js deployment; edge CDN |
| **CI/CD** | GitHub Actions | Latest | Automated test + deploy | Free for public/private repos; tight GitHub integration |
| **Error Tracking** | Sentry | Latest | Runtime error capture | Best-in-class; React Native + Node.js SDKs |
| **Product Analytics** | PostHog | Latest | Feature usage tracking | Open-source option; self-hostable; GDPR-friendly |
| **Log Management** | Axiom | Latest | Structured log aggregation | Generous free tier; excellent DX; fast search |
| **API Testing** | Postman | Latest | API development + testing | Industry standard; team collaboration; mock servers |
| **Version Control** | GitHub | Latest | Source control | Industry standard; Actions for CI/CD |
| **Package Manager** | pnpm | 9.x | Node.js packages | 3× faster than npm; disk-efficient; monorepo support |
| **Monorepo Tool** | Turborepo | 2.x | Monorepo build system | Fast incremental builds; caching; works with pnpm |

---

## 3.0 Detailed Stack Breakdown

---

### 3.1 Frontend

#### 3.1.1 Mobile App — React Native (Expo SDK 52)

React Native with the Expo managed workflow is the primary client for Alex. It compiles to native iOS and Android from a single TypeScript codebase, which is essential for a small team shipping to both platforms simultaneously.

The Expo managed workflow was chosen over bare React Native for two reasons: it eliminates native build configuration overhead (which is significant on a solo or small team), and Expo's EAS Build service handles App Store and Play Store submission without requiring a Mac for Android builds. The SDK 52 release supports the New Architecture (JSI + Fabric), delivering near-native performance for the real-time voice waveform animation and live transcript rendering that Alex requires.

The key mobile-specific packages required are:

| Package | Version | Purpose |
|---------|---------|---------|
| `expo-av` | Latest | Audio recording + playback for voice and TTS |
| `expo-notifications` | Latest | FCM push notification handling |
| `expo-background-fetch` | Latest | Background file re-index trigger |
| `@picovoice/porcupine-react-native` | 3.x | Wake word detection (F001) |
| `react-native-url-polyfill` | Latest | WebSocket + fetch compatibility |
| `@supabase/supabase-js` | 2.x | DB queries + Realtime subscriptions |
| `zustand` | 5.x | Global state management |
| `react-native-mmkv` | 2.x | Fast local key-value storage (SQLite alternative for preferences) |

**Why not Flutter:** Flutter would require learning Dart and has a weaker ecosystem for the audio-heavy, API-intensive stack Alex uses. React Native's JavaScript runtime means the same TypeScript types and utility libraries can be shared between the mobile app and the Node.js backend via the monorepo.

**Why not native iOS/Android:** Two separate codebases would require two engineering tracks — not viable for a lean build.

---

#### 3.1.2 Web Dashboard — Next.js 15 (App Router)

The web dashboard uses Next.js 15 with the App Router, deployed on Vercel. It serves as a secondary interface: users who prefer typing over voice, or who want to review tasks, files, and meeting summaries on a larger screen, use the web companion.

Next.js was selected because it shares the same React paradigm as the mobile app, meaning component logic and TypeScript types can be reused across both surfaces via the monorepo's shared packages. The App Router's React Server Components reduce JavaScript bundle size for the dashboard views (task list, briefing viewer, settings), while client components handle interactive elements (chat input, voice button, real-time updates via Supabase Realtime).

**Why not a separate SPA (Vite + React):** Next.js handles routing, SSR, API routes, and deployment in one framework, reducing the number of configuration decisions required.

---

#### 3.1.3 Styling — NativeWind (Mobile) + Tailwind CSS (Web) + shadcn/ui (Web)

NativeWind 4 brings Tailwind's utility-class system to React Native, enabling a consistent design language across both surfaces. The same spacing, colour, and typography tokens apply whether building the mobile chat UI or the web dashboard.

For the web dashboard, shadcn/ui provides accessible, unstyled components (buttons, cards, dialogs, toasts) that are styled entirely with Tailwind. Unlike component libraries that impose visual opinions (Material UI, Chakra), shadcn/ui is copied directly into the project — there is no external dependency to update, and components can be modified without overriding library styles.

---

#### 3.1.4 State Management — Zustand 5

Zustand manages global client state: the current conversation session, voice mode status, active task, and streaming response buffer. It was selected over Redux Toolkit because Alex's state graph is relatively shallow — the core state is a handful of slices (session, voice, tasks, preferences) with straightforward mutations. Zustand's minimal boilerplate and direct integration with React hooks makes it faster to build and easier to debug at this scale. Redux's middleware model would add unnecessary complexity without benefit.

---

### 3.2 Backend

#### 3.2.1 Runtime — Node.js 22 LTS

Node.js 22 LTS is the backend runtime. Its event-driven, non-blocking I/O model is architecturally well-matched to Alex's workload: simultaneously holding open streaming connections to the Claude API, Deepgram WebSocket, and ElevenLabs, while running BullMQ workers for background jobs and serving REST endpoints. A blocking runtime (Python synchronous, PHP) would struggle to maintain the ≤ 2 second voice-to-response latency under concurrent tool execution.

Node.js 22 specifically is chosen because it is the latest LTS release with built-in support for ES modules, the `fetch` API, WebStreams, and significant V8 performance improvements that benefit the JSON-heavy context assembly work done on every Claude API call.

---

#### 3.2.2 Framework — Express.js 5

Express.js 5 is the API framework. Its primary advantage for Alex is explicit, fine-grained control over HTTP response streaming — the Server-Sent Events (SSE) pipeline that powers streaming Claude responses requires setting response headers, writing individual chunks, and managing stream lifecycle in ways that framework abstractions (NestJS, Fastify plugins) often complicate. Express allows the streaming endpoint to be implemented in exactly the pattern the Anthropic SDK expects, without adapter layers.

Express 5 (currently in release candidate with full v5 expected shortly) adds native async error handling — previously a source of unhandled promise rejection bugs in Express 4 that were particularly problematic in tool execution code paths.

**Why not Fastify:** Fastify's schema-first design and plugin architecture add overhead for a small team that values explicit code over configuration. Express is more widely understood and easier to onboard new engineers.

**Why not NestJS:** NestJS's decorator-heavy, Angular-inspired architecture is better suited to large teams maintaining a complex API. Alex's monolith has clearly bounded modules but does not need NestJS's dependency injection system to achieve that.

---

#### 3.2.3 Language — TypeScript 5

TypeScript is used across the entire stack: React Native app, Next.js web dashboard, Express backend, and shared packages. This single-language strategy enables type sharing across layers — the same `Task`, `Contact`, `AutomationPlan`, and `Message` interfaces are defined once in a shared `@alex/types` package and imported by both client and server.

TypeScript 5's `satisfies` operator, const type parameters, and decorator metadata improvements are actively used in the tool definition system (type-safe Claude tool schemas) and Supabase query builder.

---

### 3.3 AI & Intelligence

#### 3.3.1 LLM — Anthropic Claude (claude-sonnet-4-20250514)

Claude `claude-sonnet-4-20250514` is the intelligence core for all of Alex's understanding, planning, drafting, and response generation. It was selected as the primary LLM on the following grounds:

**Tool use quality.** Alex's architecture depends entirely on Claude's ability to correctly identify which tools to call, in what order, with correctly structured parameters. Claude's tool-use implementation is among the most reliable available, with a low rate of hallucinated tool calls or malformed parameter objects compared to alternatives tested.

**Streaming support.** Claude's streaming API delivers tokens via Server-Sent Events with sub-100ms first-token latency from the Anthropic API, which is essential for meeting the ≤ 2 second voice-to-first-audio target.

**Context window.** The 200,000-token context window means Alex's system prompt (with full user profile, tool definitions, and conversation history) fits comfortably within a single request, even for long sessions or large meeting transcripts sent for summarisation.

**Prompt caching.** Anthropic's prompt caching feature allows the static portions of Alex's system prompt (identity, tool definitions, operating rules) to be cached server-side, reducing both latency and token costs on every request by approximately 60–70%.

**Safety and reliability.** For a personal assistant that sends emails and WhatsApp messages on the user's behalf, Claude's constitutional AI training reduces the risk of the model producing outputs that embarrass or harm the user through unintended actions.

The specific Claude API configuration for Alex is as follows:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | `claude-sonnet-4-20250514` | Best balance of speed, quality, and cost |
| Max tokens | 4,096 | Sufficient for all response types; hard caps cost |
| Temperature | 0.3 (task execution) / 0.7 (conversation) | Low temp for reliable tool calls; higher for natural dialogue |
| Streaming | Enabled (SSE) | Required for voice latency target |
| Prompt caching | Enabled on system prompt | 60–70% token cost reduction on static content |
| Tool choice | `auto` | Claude decides whether and which tools to use |

---

#### 3.3.2 Speech-to-Text — Deepgram Nova-3

Deepgram Nova-3 is the STT engine for both real-time voice commands (F002) and meeting transcription (F038). The integration uses Deepgram's streaming WebSocket API, which processes audio chunks in real time and returns partial transcripts as the user speaks, with a final punctuated transcript delivered on silence detection.

Deepgram was selected primarily on latency: its streaming API returns first partial transcript tokens within 300ms of audio reception — faster than any alternative tested at similar accuracy levels. For meeting transcription, Nova-3 achieves over 95% word accuracy on clear English audio, meeting the PRD requirement of ≥ 90%.

The streaming configuration used for voice commands is:

| Parameter | Value |
|-----------|-------|
| Model | `nova-3` |
| Language | `en-US` |
| Interim results | `true` (for live transcript display, F005) |
| Endpointing | `700ms` silence threshold (voice commands) |
| Smart format | `true` (punctuation, capitalisation) |
| Utterance end | `10,000ms` (meeting transcription only) |

The fallback for Deepgram outages is OpenAI Whisper via the OpenAI API, which adds approximately 800ms of additional latency but maintains acceptable accuracy.

---

#### 3.3.3 Text-to-Speech — ElevenLabs (Primary) + Google Cloud TTS (Fallback)

ElevenLabs' `eleven_turbo_v2` model is the primary TTS engine. It was selected because it is the only widely available TTS service that supports streaming audio output — meaning audio playback can begin within 400ms of the first text token arriving from Claude, without waiting for the full response to be generated. This is architecturally non-negotiable for the voice-first experience.

The voice used for Alex will be selected from ElevenLabs' pre-built professional voices library, targeting a calm, clear, professional-sounding male or neutral voice. Custom voice cloning is out of scope for v1.0 (F003 spec) but is architecturally easy to add in v1.5 since ElevenLabs supports it natively.

Google Cloud Text-to-Speech (WaveNet `en-US-Neural2-J`) serves as the fallback in the event of ElevenLabs service degradation. It does not support streaming in the same way, which means the TTS fallback path will have a slightly longer perceived first-audio latency (600–900ms vs. 400ms), but remains within acceptable bounds for a fallback scenario.

---

#### 3.3.4 Wake Word — Porcupine by Picovoice (v3)

Porcupine handles always-on "Hey Alex" detection entirely on-device. It runs as a lightweight binary using the device's DSP chip, consuming approximately 1–2% CPU and negligible battery. No audio is ever transmitted to a server until the wake word is confirmed — a critical privacy and user trust requirement.

The Porcupine React Native SDK provides a cross-platform wrapper for iOS and Android with a single JavaScript API. The wake word model file for "Hey Alex" is pre-trained by Picovoice and bundled with the app at approximately 1MB.

**Why not Snowboy or custom keyword spotting:** Snowboy is no longer maintained. Custom keyword spotting (via TensorFlow Lite) would require significant ML engineering work and ongoing model maintenance that is not justified at this stage.

---

#### 3.3.5 Embeddings — OpenAI text-embedding-3-small

All semantic search in Alex — file search (F011) and memory retrieval (F052) — relies on vector embeddings generated by OpenAI's `text-embedding-3-small` model. This model produces 1536-dimensional embeddings and achieves a strong balance between retrieval quality and cost.

At $0.02 per 1 million tokens, embedding costs for a single-user system are negligible: indexing a 2,000-file Google Drive (~10,000 chunks at ~200 tokens each) costs approximately $0.04 total. Daily re-embedding of changed files and new memories adds less than $0.01/day.

The embedding model is accessed server-side only (API key never exposed to the client). Embeddings are generated in a BullMQ background job to ensure file indexing never blocks the main API response path.

**Note on Anthropic Voyage:** Anthropic's Voyage embedding models (`voyage-3`) show superior retrieval quality on long documents and code. Switching to Voyage is listed as an improvement in v1.5 if file search accuracy falls below the 90% target with the current model.

---

### 3.4 Database & Storage

#### 3.4.1 Primary Database — Supabase (PostgreSQL 16)

Supabase serves as the primary data store for all of Alex's structured and vector data. It was selected because it provides the full data infrastructure Alex needs — PostgreSQL, pgvector, real-time subscriptions, row-level security, storage, and authentication — in a single managed service. This avoids the operational overhead of running separate services for each concern.

The specific Supabase capabilities used by Alex:

**PostgreSQL 16** stores all structured data: users, sessions, tasks, events, contacts, memories, files metadata, sent messages, briefings, and automation plans. Full schema is defined in SYSTEM_DESIGN.md § 7.

**pgvector extension** handles semantic search for files (F011) and memory retrieval (F052) using cosine similarity. The IVFFlat index type is used with `lists = 100`, providing fast approximate nearest-neighbour search suitable for up to ~100,000 vectors before requiring migration to HNSW indexing.

**Supabase Realtime** powers the live automation progress tracker (F066) and any real-time UI updates via WebSocket subscriptions directly from the React Native app and Next.js dashboard — without requiring a separate WebSocket server.

**Supabase Storage** stores pre-generated TTS audio files for morning briefings (F058). Audio files are stored in a `briefings` bucket with a CDN-backed public URL, eliminating re-generation latency on playback.

**Row-Level Security (RLS)** is enabled on all tables, ensuring that even if the application logic has a bug, database-level policies prevent cross-user data access. Since Alex is single-user in v1.0, RLS policies are simple (`user_id = auth.uid()`), but they establish the correct security posture for multi-user expansion in v2.0.

---

#### 3.4.2 Cache Layer — Upstash Redis (Serverless)

Upstash provides serverless Redis with a REST API that is compatible with edge and serverless runtimes, in addition to the standard Redis protocol used by BullMQ. It stores:

- Conversation session history (`session:{id}:history`, 24h TTL) — F051
- Rate limiting counters (API endpoint abuse prevention)
- BullMQ job queue backing store (all background and scheduled jobs — F067)
- Temporary data within automation plan execution (inter-step result passing — F063)

Upstash was selected over a self-managed Redis instance on Railway because its serverless billing model (pay per request, not per hour) is significantly cheaper at low volume. The free tier provides 10,000 commands/day, which is more than sufficient for a single-user system.

---

#### 3.4.3 Local Device Storage — MMKV (React Native)

`react-native-mmkv` provides fast synchronous key-value storage on the user's device, used for:

- Caching the last known user preferences (tone, working hours, wake time) so the app is functional during brief network outages without needing to query Supabase
- Storing the active session ID and conversation state so the app can resume correctly after being backgrounded
- Storing OAuth tokens locally (encrypted using MMKV encryption key backed by the device keychain)

MMKV was chosen over AsyncStorage because it is synchronous and approximately 30× faster, which matters for reading preferences at app startup before the first render.

---

### 3.5 Communication Layer

#### 3.5.1 Email — Gmail API v1 (Google OAuth 2.0)

The Gmail API is the only email integration in v1.0. Since the PRD established that the target user primarily uses Gmail (or Google Workspace), a direct Gmail integration via OAuth is the correct approach — no email relay service (SendGrid, Postmark) is needed for the sending case, and no IMAP parsing is needed for the reading case.

The Gmail API scopes required are:

| Scope | Purpose | Feature |
|-------|---------|---------|
| `gmail.send` | Send emails on user's behalf | F018 |
| `gmail.readonly` | Read inbox for briefing important emails | F057 |
| `gmail.compose` | Create drafts | F019 |

OAuth 2.0 refresh tokens are stored encrypted in Supabase (`oauth_tokens` table, AES-256 encryption via Supabase Vault). Tokens are refreshed automatically using `google-auth-library` before any Gmail API call.

**Outlook / SMTP support** is explicitly out of scope for v1.0 (PRD § 8.0). The architecture isolates the email adapter (SYSTEM_DESIGN.md § 4.5.1) so adding an Outlook adapter in v1.5 is a contained change.

---

#### 3.5.2 WhatsApp — Meta WhatsApp Business Cloud API v21.0

The Meta WhatsApp Business Cloud API is the only compliant method for sending WhatsApp messages programmatically from a business application. The Cloud API (Meta-hosted) is used rather than the On-Premises API because it requires no server infrastructure on Alex's side for the WhatsApp gateway — Meta hosts the gateway and Alex calls the REST endpoint.

Key integration details:

| Attribute | Value |
|-----------|-------|
| API version | v21.0 |
| Endpoint | `https://graph.facebook.com/v21.0/{phone-number-id}/messages` |
| Auth | Permanent system user access token (Meta App) |
| Webhooks | Delivery status updates → `POST /webhooks/whatsapp` |
| Media upload | `POST /{phone-number-id}/media` then reference media ID |
| Message types used | `text`, `document`, `template` |

The 24-hour session window constraint (F023) requires maintaining a `last_whatsapp_interaction_at` timestamp per contact. Approved message templates must be pre-registered with Meta for use outside the 24-hour window; this is an operational requirement (not purely an engineering one) that must be completed before the WhatsApp feature ships.

---

#### 3.5.3 Push Notifications — Firebase Cloud Messaging (FCM v1)

Firebase Cloud Messaging handles all push notifications to iOS and Android: task reminders (F036), briefing notifications (F059), automation completion alerts (F066), and overdue task warnings (F035).

FCM v1 (the HTTP v1 API, not the legacy API) is used. It is required for iOS notifications (APNs) and is the current recommended API — the legacy FCM API was deprecated in June 2024.

The notification flow is:

1. BullMQ job triggers notification dispatch at the scheduled time
2. Server calls FCM v1 HTTP API with device token + notification payload
3. FCM delivers to iOS (via APNs) or Android (direct)
4. React Native app handles notification via `expo-notifications`

Device tokens are stored in `users.fcm_token` in Supabase and refreshed each time the app is opened (tokens rotate periodically).

---

### 3.6 Automation & Integrations

#### 3.6.1 Job Queue — BullMQ 5 + Upstash Redis

BullMQ is the background job and task scheduling engine for all of Alex's asynchronous work. It runs as a separate Worker process alongside the main Express API server on Railway. The following job types are registered:

| Job Name | Schedule | Purpose | Features |
|----------|----------|---------|---------|
| `briefingJob` | Cron: `0 7 * * *` (configurable) | Generate morning briefing | F057 |
| `fileIndexJob` | Cron: `*/15 * * * *` | Delta sync Google Drive | F010 |
| `overdueScanJob` | Cron: `0 * * * *` | Mark tasks overdue | F035 |
| `preMeetingJob` | Delayed: `event.start - 10min` | Surface relevant files | F042 |
| `memoryConsolidationJob` | Cron: `0 23 * * *` | Summarise day to episodic memory | F053 |
| `reminderJob` | Delayed: `task.due_at` | Fire reminder notification | F036 |
| `automationPlanJob` | On-demand | Execute multi-step plans | F063 |
| `embeddingJob` | On-demand (after file index) | Generate file embeddings | F010 |

BullMQ's delayed job support (scheduling a job to run at a specific future timestamp) is essential for reminders and pre-meeting prep — two features that require precise time-based execution, not just periodic polling.

---

#### 3.6.2 Google API Suite

Three Google APIs are used via the same OAuth 2.0 credentials obtained during onboarding. A single `GoogleAuthClient` module manages token refresh and provides authenticated clients for all three services.

| API | Version | SDK | Features |
|-----|---------|-----|---------|
| Gmail API | v1 | `googleapis` npm | F017, F018, F019, F020, F057 |
| Google Calendar API | v3 | `googleapis` npm | F025, F026, F027, F028, F029, F030, F031 |
| Google Drive API | v3 | `googleapis` npm | F010, F011, F013 |
| Google People API | v1 | `googleapis` npm | F024 (contact seeding) |
| Google Cloud TTS | v1 | `@google-cloud/text-to-speech` | F003 (fallback) |

All Google APIs are accessed via the official `googleapis` npm package, which handles OAuth token management, retry logic, and request signing uniformly across all services.

---

#### 3.6.3 Chrono-Node (Date Parsing)

`chrono-node` is a natural language date/time parser for Node.js. It converts expressions like "Friday at 9 AM", "next Thursday afternoon", "in 2 hours", and "end of the month" into JavaScript `Date` objects. This is used in F032 (Task Creation), F026 (Event Creation), and F036 (Reminder scheduling).

**Why not rely on Claude for date parsing:** While Claude can interpret dates contextually, passing date strings to Claude and having it return parsed dates adds a round-trip to the LLM. `chrono-node` runs synchronously in microseconds and produces deterministic output, making it the correct tool for this discrete sub-problem.

---

#### 3.6.4 PDF and Document Parsers

File text extraction for the indexing pipeline (F010) uses the following parser stack:

| File Type | Library | Notes |
|-----------|---------|-------|
| PDF | `pdf-parse` | Extracts raw text; handles multi-page; no OCR |
| DOCX | `mammoth` | High-quality DOCX → plain text; preserves structure |
| XLSX | `xlsx` (SheetJS) | Converts spreadsheet cells to structured text |
| Google Docs | Drive export API | Export as `text/plain` via Drive API |
| Google Sheets | Sheets API | Read cell values via Sheets API v4 |
| TXT / MD | Native `fs.readFile` | Direct string read |

---

### 3.7 Infrastructure & Hosting

#### 3.7.1 Backend Hosting — Railway

The Node.js backend (Express API server + BullMQ worker) is hosted on Railway. Railway was selected over serverless alternatives (Vercel Serverless Functions, Cloudflare Workers) for one critical architectural reason: Alex's backend requires **always-on, persistent processes**.

The Express server maintains open WebSocket connections to Deepgram (during active voice sessions), streams SSE responses to the mobile app, and runs BullMQ workers that must be alive to process scheduled jobs. Serverless functions that cold-start on each request and terminate after the response would break all three of these requirements. A 5-second cold start on a serverless function would violate the ≤ 2 second latency target before a single line of application code executes.

Railway's `Hobby` plan provides always-on deployments at $5/month per service with 8GB RAM and 8 vCPUs — more than adequate for a single-user system. Railway also provides automatic deployments from GitHub, environment variable management, and built-in metrics.

| Service | Railway Configuration |
|---------|----------------------|
| `alex-api` | Node.js 22, always-on, 512MB RAM, auto-restart |
| `alex-worker` | Node.js 22 (BullMQ worker), always-on, 256MB RAM |

---

#### 3.7.2 Web Dashboard Hosting — Vercel

The Next.js web dashboard is hosted on Vercel. Vercel is the natural hosting choice for Next.js (being its creator) and provides zero-configuration deployment, automatic preview deployments on pull requests, edge CDN for static assets, and the most optimised Next.js build pipeline available. The free Hobby plan is sufficient for a single-user web dashboard with low traffic.

---

#### 3.7.3 CI/CD — GitHub Actions

GitHub Actions provides the CI/CD pipeline. The pipeline runs on every push to `main` and every pull request:

```
On Pull Request:
  1. pnpm install (cached)
  2. TypeScript type check (tsc --noEmit)
  3. ESLint + Prettier lint check
  4. Unit tests (Vitest)
  5. Build check (backend + web)

On Push to main:
  1. All PR checks above
  2. Deploy backend → Railway (via Railway deploy hook)
  3. Deploy web → Vercel (automatic via Vercel GitHub integration)
  4. EAS Update (Expo) → push JS bundle update to mobile app
     (no App Store review required for JS-only changes)
```

EAS Update is used for mobile deployments. Because React Native with Expo allows over-the-air (OTA) JS bundle updates without App Store review, most backend-driven feature changes can be shipped to mobile users within minutes of merging to main.

---

#### 3.7.4 Monorepo — Turborepo + pnpm

The entire Alex codebase is organised as a pnpm monorepo managed by Turborepo:

```
alex/
├── apps/
│   ├── mobile/          # React Native (Expo)
│   └── web/             # Next.js dashboard
├── packages/
│   ├── api/             # Express backend
│   ├── worker/          # BullMQ worker process
│   ├── types/           # Shared TypeScript interfaces
│   ├── db/              # Supabase client + schema types (generated)
│   └── tools/           # Claude tool definitions (shared types)
└── turbo.json           # Build pipeline configuration
```

Turborepo's build caching means unchanged packages are not rebuilt on each CI run, significantly reducing CI time as the codebase grows.

---

### 3.8 Monitoring & Debugging

#### 3.8.1 Error Tracking — Sentry

Sentry captures unhandled exceptions, promise rejections, and explicitly reported errors across the React Native app, Next.js web dashboard, and Node.js backend. The `@sentry/react-native`, `@sentry/nextjs`, and `@sentry/node` SDKs are installed in their respective packages and configured with the same Sentry project DSN.

Sentry is configured to capture the following context with every error event: session ID, user ID (hashed), the last 3 conversation turns (truncated), the active automation plan (if any), and the specific tool call that was executing at the time of failure. This context makes debugging tool execution failures significantly faster.

Source maps are uploaded to Sentry on every deployment, enabling production stack traces to be mapped back to original TypeScript source lines.

---

#### 3.8.2 Product Analytics — PostHog

PostHog tracks product usage events to measure the success metrics defined in PRD.md § 3.2. The events captured include:

| Event | Properties | Purpose |
|-------|-----------|---------|
| `voice_command_started` | `mode: voice/text` | Track voice adoption |
| `intent_resolved` | `tool_called`, `latency_ms` | Measure intent accuracy |
| `file_search_completed` | `result_count`, `top_score`, `success` | Track F011 performance |
| `email_sent` | `has_attachment`, `contact_known` | Communication feature usage |
| `briefing_opened` | `time_after_generation_mins` | Briefing engagement |
| `task_completed` | `overdue`, `source` | Task management health |
| `automation_plan_completed` | `step_count`, `partial_failure` | Automation reliability |

PostHog is self-hostable (relevant for data privacy) and has a generous free cloud tier of 1 million events/month — far beyond what a single-user system will generate.

---

#### 3.8.3 Log Management — Axiom

Axiom aggregates structured JSON logs from the Railway backend and BullMQ worker. Every significant system event is logged in a consistent format (defined in SYSTEM_DESIGN.md § 4.8.2): timestamp, session ID, event type, tool name, status, latency, and error detail.

Axiom's query language allows filtering logs by session, tool, or time range in seconds — critical for debugging a production issue where a specific automation plan failed for a user. The free tier provides 500GB ingest/month, which comfortably covers single-user volume.

---

#### 3.8.4 API Development & Testing — Postman

Postman is used for all API development, testing, and documentation. A Postman collection covering all endpoints defined in SYSTEM_DESIGN.md § 6 is maintained in the repository (exported as JSON) and kept in sync with the live API.

Postman's environment variables allow the team to switch between local development, staging, and production endpoints without modifying requests. Mock servers (Postman's built-in feature) are used to develop the React Native app against API endpoints before the backend implementation is complete.

---

### 3.9 Development Tools

#### 3.9.1 Version Control — GitHub

GitHub hosts the monorepo. Branch protection rules are configured on `main`: pull requests require at least one review and passing CI checks before merge. Releases are tagged semantically (`v1.0.0`, `v1.0.1`) and linked to Railway deployments.

**Repository structure:**
- `main` — production branch (protected)
- `dev` — integration branch for feature work
- `feature/*` — individual feature branches (from FEATURE_LIST.md IDs: e.g., `feature/F011-semantic-search`)

---

#### 3.9.2 IDE — VS Code (Recommended)

VS Code is the recommended IDE with the following extensions mandatory for consistency:

| Extension | Purpose |
|-----------|---------|
| ESLint | Real-time linting |
| Prettier | Auto-formatting on save |
| TypeScript (built-in) | Type checking |
| Tailwind CSS IntelliSense | Tailwind class completion |
| Supabase | Database schema browsing |
| Thunder Client | Lightweight REST client (alternative to Postman for quick tests) |
| GitLens | Enhanced git history and blame |

A shared `.vscode/settings.json` and `.vscode/extensions.json` are committed to the repository so all team members work with an identical IDE configuration.

---

#### 3.9.3 Package Management — pnpm 9

`pnpm` is used as the package manager across the entire monorepo. Its key advantages over `npm` and `yarn` for this project are: a global content-addressable store that prevents duplicate package installations across workspaces (critical for a monorepo with shared dependencies), strict hoisting behaviour that prevents phantom dependencies, and installation speeds approximately 3× faster than `npm` — which matters when CI runs `pnpm install` on every PR.

A single `pnpm-lock.yaml` at the repo root ensures deterministic installs across all developers and CI environments.

---

#### 3.9.4 Code Quality — ESLint + Prettier + Husky

ESLint with `@typescript-eslint` enforces code quality rules. Prettier handles formatting with zero configuration (default Prettier rules). Both run as pre-commit hooks via Husky and `lint-staged`, ensuring no unformatted or linting-error code enters the repository.

A `commitlint` configuration enforces conventional commit messages (`feat:`, `fix:`, `chore:`) to maintain a clean git history suitable for automated changelog generation.

---

#### 3.9.5 Testing — Vitest + Detox

**Unit and integration tests:** Vitest is the test runner for the Node.js backend and shared packages. It is TypeScript-native, significantly faster than Jest, and compatible with the ES module setup used across the monorepo.

**Mobile E2E tests:** Detox (by Wix) handles end-to-end testing on iOS and Android simulators. Critical flows tested automatically: onboarding, voice command routing, email send, task creation, and morning briefing delivery.

**API contract tests:** Postman Newman (the CLI runner for Postman collections) runs the Postman collection against the staging environment as part of the CI pipeline before any production deployment.

---

## 4.0 Rejected Alternatives

The following technologies were evaluated and rejected. Their rejection rationale is documented here to prevent the same alternatives from being re-evaluated in the future without new information.

| Category | Rejected | Chosen Instead | Rejection Reason |
|----------|---------|---------------|-----------------|
| LLM | OpenAI GPT-4o | Claude claude-sonnet-4-20250514 | Claude has superior tool-use reliability and prompt caching; GPT-4o's tool call hallucination rate was higher in testing on complex multi-step plans |
| LLM | Google Gemini 2.0 | Claude claude-sonnet-4-20250514 | Weaker tool-use consistency; streaming API more complex to integrate; less established for agentic use cases |
| STT | OpenAI Whisper API | Deepgram Nova-3 | Whisper API does not support streaming — it requires full audio upload before returning transcript. This adds 1–3 seconds of latency unacceptable for the voice-first UX |
| STT | Google Cloud Speech-to-Text | Deepgram Nova-3 | Google's streaming STT has higher latency for first partial results (~600ms vs. ~300ms); Deepgram consistently outperforms on accuracy benchmarks for conversational English |
| TTS | OpenAI TTS | ElevenLabs eleven_turbo_v2 | OpenAI TTS does not support streaming audio generation in the same chunk-by-chunk manner; first audio chunk latency is higher (~800ms vs. ~400ms) |
| TTS | Amazon Polly | ElevenLabs eleven_turbo_v2 | Polly's neural voices sound noticeably more synthetic than ElevenLabs; no streaming support |
| Vector DB | Pinecone | pgvector (in Supabase) | Pinecone adds an additional managed service, cost layer, and network hop. At single-user scale with < 20,000 vectors, pgvector's IVFFlat index is fast enough and eliminates operational complexity. Pinecone is reconsidered at v2.0 multi-user scale. |
| Vector DB | Weaviate | pgvector (in Supabase) | Same rationale as Pinecone — additional service overhead not justified at this scale |
| Backend Framework | NestJS | Express.js 5 | NestJS's DI container and decorator system add cognitive overhead without benefit at this team size; harder to control SSE streaming behaviour precisely |
| Backend Framework | Fastify | Express.js 5 | Fastify's plugin-based architecture complicates the custom streaming pipeline needed for Claude SSE → TTS; Express gives full control |
| Backend Hosting | Vercel Serverless | Railway (always-on) | Cold starts (1–5 seconds) violate the latency target; serverless cannot hold persistent WebSocket connections to Deepgram or BullMQ workers |
| Backend Hosting | Cloudflare Workers | Railway (always-on) | Workers have a 30-second CPU time limit unsuitable for long meeting transcriptions or multi-step automation plans; no persistent storage for WebSocket sessions |
| Database | Firebase Realtime DB | Supabase (PostgreSQL) | Firebase's document model does not support the complex relational queries and vector search Alex requires; no SQL |
| Database | PlanetScale (MySQL) | Supabase (PostgreSQL) | MySQL does not have pgvector; would require a separate vector DB, adding operational complexity |
| Cache | Redis Cloud (Redis Ltd) | Upstash Redis | Redis Cloud's minimum paid tier ($7/month) is more expensive than Upstash at low volume; Upstash's serverless billing is better suited to variable single-user load |
| Mobile | Flutter | React Native (Expo) | Dart is a second language with no overlap with the TypeScript backend; weaker ecosystem for audio streaming and native Porcupine integration |
| Mobile | Native iOS + Android | React Native (Expo) | Two codebases require double the mobile engineering effort; not feasible for a lean team |
| State Management | Redux Toolkit | Zustand | Redux adds significant boilerplate (actions, reducers, selectors) for state that is simple enough to manage with Zustand's direct mutation model |
| Automation/Workflow | Zapier / Make | Custom BullMQ + Claude planner | Third-party automation platforms cannot be called from within Claude's tool-use loop; they are user-facing no-code tools, not programmable APIs suitable for AI agent orchestration |
| Email Relay | SendGrid | Gmail API directly | SendGrid would be used for sending emails from Alex's own email address, not the user's Gmail account. Since Alex sends on the user's behalf, only Gmail API (OAuth) achieves the correct sender identity |
| Analytics | Mixpanel | PostHog | PostHog is open-source and self-hostable; Mixpanel has no self-hosting option and is significantly more expensive at scale |

---

## 5.0 Cost Breakdown

### 5.1 Free Tier Limits by Service

| Service | Free Tier | Paid Tier Starts At |
|---------|-----------|---------------------|
| **Anthropic Claude API** | No free tier; $3/MTok input, $15/MTok output (Sonnet 4) | Usage-based only |
| **Deepgram** | $200 credit on signup (~55 hours of audio) | $0.0043/min streaming after credit |
| **ElevenLabs** | 10,000 characters/month | Creator: $22/mo (100,000 chars) |
| **Google Cloud TTS** | 1M characters/month (WaveNet: 1M chars free) | $16/1M chars (WaveNet) after free tier |
| **Picovoice (Porcupine)** | Free for personal/non-commercial use | $0 (free unlimited for single-user personal app) |
| **OpenAI Embeddings** | No free tier; $0.02/1M tokens | Usage-based only |
| **Supabase** | Free: 500MB DB, 1GB storage, 2M realtime messages/mo | Pro: $25/month (8GB DB, 250GB storage) |
| **Upstash Redis** | Free: 10,000 commands/day, 256MB | Pay-as-you-go: $0.20/100K commands |
| **Railway** | Free: $5 credit/month (~500 hours) | Hobby: $5/month per service (always-on) |
| **Vercel** | Free: Hobby plan (personal projects) | Pro: $20/month (for teams) |
| **Firebase (FCM)** | Free: unlimited notifications | Free forever for FCM |
| **Sentry** | Free: 5,000 errors/month, 10K transactions | Team: $26/month |
| **PostHog** | Free: 1M events/month | Scale: $0.00045/event after 1M |
| **Axiom** | Free: 500GB ingest/month | Pro: $25/month |
| **GitHub** | Free: unlimited private repos + 2,000 CI minutes/month | Team: $4/user/month |
| **Gmail API** | Free: 1B quota units/day | No paid tier — included in Google account |
| **Google Calendar API** | Free: 1M requests/day | No paid tier — included in Google account |
| **Google Drive API** | Free: 1B quota units/day | No paid tier — included in Google account |
| **Meta WhatsApp API** | Free: 1,000 user-initiated conversations/month | $0.005–$0.015 per conversation after free tier (India pricing) |

---

### 5.2 Estimated Monthly Cost — Single User (v1.0)

The following estimates assume a single active user with moderate usage: 20 voice interactions/day, 5 files indexed/day, 3 emails/day, 5 WhatsApp messages/day, 1 morning briefing/day, and 2 automation plans/day.

#### Claude API Cost Estimate

| Usage Type | Volume/Month | Tokens | Cost |
|------------|-------------|--------|------|
| Voice commands (input) | 600 requests | ~1,500 tokens avg (system + context + input) = 900K tokens | $2.70 |
| Voice commands (output) | 600 requests | ~300 tokens avg = 180K tokens | $2.70 |
| Prompt cache savings (70% of input) | — | ~630K tokens saved | −$1.89 |
| Briefings (30/month) | 30 requests | ~3,000 tokens input + 800 output = 114K tokens | $0.66 |
| Meeting summaries (8/month) | 8 requests | ~5,000 tokens input + 500 output = 44K tokens | $0.22 |
| Memory consolidation (30/month) | 30 requests | ~2,000 tokens input + 500 output = 75K tokens | $0.38 |
| **Subtotal Claude** | | | **~$4.77/month** |

#### Other Service Cost Estimates

| Service | Usage/Month | Estimated Cost |
|---------|------------|----------------|
| Deepgram | ~300 min (10 min/day) | $1.29 (after $200 free credit is used) |
| ElevenLabs | ~50,000 chars (briefings + responses) | Free tier (10K/mo) covered partially; Creator plan $22/mo recommended |
| Google Cloud TTS | < 50,000 chars (fallback only) | Free tier |
| OpenAI Embeddings | ~500K tokens/month (file changes + new memories) | $0.01 |
| Supabase | < 200MB DB, < 100MB storage | Free tier |
| Upstash Redis | ~50,000 commands/day × 30 = 1.5M/month | ~$3.00 |
| Railway | 2 services (API + worker) always-on | $10.00 |
| Vercel | Low traffic web dashboard | Free tier |
| Sentry | < 1,000 errors/month | Free tier |
| PostHog | < 50,000 events/month | Free tier |
| WhatsApp | ~150 conversations/month | Free tier (under 1,000/month) |

#### Total Estimated Monthly Cost (Single User)

| Scenario | Monthly Cost |
|----------|-------------|
| **Minimal (development/testing)** | ~$15/month |
| **Regular active use** | ~$40–45/month |
| **Heavy use (frequent automations, long meetings)** | ~$60–70/month |

The dominant cost driver is ElevenLabs TTS ($22/month for the Creator plan). If cost reduction becomes a priority, switching to Google Cloud TTS (free tier) for all non-briefing responses would reduce the bill by ~$22/month at the expense of voice naturalness.

---

### 5.3 Cost at 100-User Scale (v2.0 Reference)

At 100 users, costs scale roughly linearly for API services and step up for infrastructure:

| Category | Single User | 100 Users |
|----------|------------|-----------|
| Claude API | ~$5/month | ~$500/month |
| Deepgram | ~$1.30/month | ~$130/month |
| ElevenLabs | $22/month | ~$1,200/month (Business plan) |
| Supabase | Free | Pro $25/month |
| Railway | $10/month | $40–80/month (more services) |
| **Total estimate** | **~$40–45/month** | **~$2,000–2,500/month** |

At 100 users, the economics suggest introducing a paid subscription of $25–30/month per user to break even and build margin.

---

## 6.0 Open Questions

| # | Question | Affects | Priority |
|---|----------|---------|----------|
| OQ-TS-1 | ElevenLabs `eleven_turbo_v2` supports streaming but the React Native audio player must handle chunked audio playback. Has the `expo-av` player been validated for real-time audio chunk streaming, or is a custom native module required? | F003, F058, latency target | High |
| OQ-TS-2 | Railway's free tier provides $5 credit/month — this covers approximately 500 hours, which is not enough for 2 always-on services (API + worker). Should both services run on the Hobby plan ($10/month total from day 1), or should the worker be consolidated into the API process for the development phase? | F067, infrastructure cost | High |
| OQ-TS-3 | Porcupine's free licence covers "personal/non-commercial" use. If Alex is monetised (even a subscription for personal use), does it require a commercial Picovoice licence? This needs legal clarification before launch. | F001, licensing, launch readiness | High |
| OQ-TS-4 | The monorepo uses pnpm workspaces and Turborepo. Expo (React Native) has historically had compatibility issues with pnpm's strict hoisting. Has this been validated with Expo SDK 52 specifically? | Development setup, CI | Medium |
| OQ-TS-5 | For the ElevenLabs fallback to Google TTS — should the fallback trigger automatically and silently (user hears a slightly different voice with no warning), or should the user be notified? | F003, UX | Medium |
| OQ-TS-6 | Supabase's free tier has a 500MB database limit. With pgvector storing 1,536-dimensional float32 embeddings, each vector consumes ~6KB. A 2,000-file index with 5 chunks per file = 10,000 vectors × 6KB = ~60MB just for embeddings, leaving 440MB for all other data. This is sufficient for v1.0 but needs monitoring. When should the Pro tier be activated? | F010, F011, database planning | Medium |

---

## 7.0 Next Steps

| # | Action | Owner | Dependency |
|---|--------|-------|-----------|
| NS-1 | Resolve OQ-TS-3 (Porcupine commercial licence) — legal review required before any launch or monetisation | Product / Legal | Immediately |
| NS-2 | Validate `expo-av` chunked audio streaming (OQ-TS-1) with a focused proof-of-concept: ElevenLabs stream → React Native audio player | Mobile Engineer | Before F003 build |
| NS-3 | Confirm pnpm + Expo SDK 52 compatibility in monorepo setup (OQ-TS-4) — create `apps/mobile` scaffold and run `pnpm install` | Engineering | Day 1 of development |
| NS-4 | Set up all third-party service accounts: Supabase project, Upstash Redis, Railway project, Deepgram API, ElevenLabs API, Meta WhatsApp App, Google Cloud Project (APIs + OAuth), Firebase project, Sentry, PostHog, Axiom | Engineering | Before development begins |
| NS-5 | Generate Supabase database schema from SYSTEM_DESIGN.md § 7 and run initial migration | Backend Engineer | Week 1 |
| NS-6 | Create Postman collection with all endpoints from SYSTEM_DESIGN.md § 6 and commit to repository | Backend Engineer | Week 1 |
| NS-7 | Begin **Security Document** (Document 6) — formalise security posture for OAuth tokens, API keys, user data, and communication content | Engineering + Product | After TECH_STACK sign-off |

---

*Technology choices documented here must remain in sync with SYSTEM_DESIGN.md. Any change to a technology after this document is approved must be reflected in both documents and communicated to the team.*

---

**Document Control**

| Field | Value |
|-------|-------|
| Document Name | TECH_STACK.md |
| Version | v1.0 |
| Status | Draft |
| Created | 24 March 2026 |
| Last Updated | 24 March 2026 |
| References | GOAL.md, PRD.md v1.0, SYSTEM_DESIGN.md v1.0, USER_FLOW.md v1.0, FEATURE_LIST.md v1.0 |
