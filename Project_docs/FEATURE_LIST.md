# Feature List Document — Alex: Personal AI Operating System
**Version:** v1.0
**Date:** 24 March 2026
**Status:** Draft
**References:** GOAL.md, PRD.md v1.0, SYSTEM_DESIGN.md v1.0, USER_FLOW.md v1.0
**Author:** Alex Project Team

---

## Table of Contents

1. [Purpose & Scope](#10-purpose--scope)
2. [Feature Overview Table](#20-feature-overview-table)
3. [Detailed Feature Breakdown](#30-detailed-feature-breakdown)
4. [Feature Dependencies Map](#40-feature-dependencies-map)
5. [Phase Release Plan](#50-phase-release-plan)
6. [Open Questions](#60-open-questions)
7. [Next Steps](#70-next-steps)

---

## 1.0 Purpose & Scope

### 1.1 Purpose

This document provides the complete, granular breakdown of every feature in Alex v1.0 through v2.0. Each feature is assigned a unique ID, a priority level, a phase, a complexity rating, and a detailed specification covering what it does, what it does NOT do, its technical requirements, and its dependencies.

This document is the authoritative reference for sprint planning, QA test creation, and product roadmap decisions.

### 1.2 Priority Definitions

| Level | Label | Meaning |
|-------|-------|---------|
| P1 | Must Have | Alex is not shippable without this in v1.0 |
| P2 | Should Have | High value; included in v1.0 or v1.5 if timeline allows |
| P3 | Nice to Have | Deferred to v1.5 or v2.0; does not block launch |

### 1.3 Complexity Definitions

| Level | Meaning |
|-------|---------|
| Low | < 3 days engineering effort; minimal external dependencies |
| Medium | 3–10 days; 1–2 external integrations |
| High | 10+ days; multiple integrations, AI pipeline, or novel logic |

### 1.4 Status Definitions

| Status | Meaning |
|--------|---------|
| 📋 Planned | Specified; not started |
| 🔨 In Progress | Under active development |
| ✅ Done | Built, tested, deployed |
| ⏸️ Deferred | Pushed to later phase |

---

## 2.0 Feature Overview Table

| ID | Feature Name | Category | Priority | Complexity | Phase | Status |
|----|-------------|----------|----------|------------|-------|--------|
| F001 | Wake Word Detection | Voice | P1 | Medium | v1.0 | 📋 Planned |
| F002 | Speech-to-Text (Streaming) | Voice | P1 | Medium | v1.0 | 📋 Planned |
| F003 | Text-to-Speech (Streaming) | Voice | P1 | Medium | v1.0 | 📋 Planned |
| F004 | Text Input Mode | Conversation | P1 | Low | v1.0 | 📋 Planned |
| F005 | Voice ↔ Text Mode Switch | Conversation | P1 | Low | v1.0 | 📋 Planned |
| F006 | Context-Aware Conversation | Conversation | P1 | High | v1.0 | 📋 Planned |
| F007 | Live Transcript Display | Voice | P2 | Low | v1.0 | 📋 Planned |
| F008 | Noise Handling / Retry | Voice | P2 | Low | v1.0 | 📋 Planned |
| F009 | File Indexing (Google Drive) | Files | P1 | High | v1.0 | 📋 Planned |
| F010 | Semantic File Search | Files | P1 | High | v1.0 | 📋 Planned |
| F011 | File Result Ranking | Files | P1 | Medium | v1.0 | 📋 Planned |
| F012 | File Preview in Chat | Files | P2 | Low | v1.0 | 📋 Planned |
| F013 | File Re-index on Demand | Files | P2 | Low | v1.0 | 📋 Planned |
| F014 | Multi-format File Parsing | Files | P1 | Medium | v1.0 | 📋 Planned |
| F015 | Local File Search | Files | P3 | Medium | v1.5 | ⏸️ Deferred |
| F016 | Dropbox / OneDrive Indexing | Files | P3 | Medium | v1.5 | ⏸️ Deferred |
| F017 | Send Email (Gmail) | Communication | P1 | High | v1.0 | 📋 Planned |
| F018 | Email Draft Preview | Communication | P1 | Low | v1.0 | 📋 Planned |
| F019 | Email with File Attachment | Communication | P1 | Medium | v1.0 | 📋 Planned |
| F020 | Tone-Matched Email Drafting | Communication | P2 | Medium | v1.0 | 📋 Planned |
| F021 | Send WhatsApp Message | Communication | P1 | High | v1.0 | 📋 Planned |
| F022 | WhatsApp File Attachment | Communication | P1 | Medium | v1.0 | 📋 Planned |
| F023 | WhatsApp 24h Window Handling | Communication | P1 | Medium | v1.0 | 📋 Planned |
| F024 | Contact Resolution Engine | Communication | P1 | Medium | v1.0 | 📋 Planned |
| F025 | Sent Message Logging | Communication | P1 | Low | v1.0 | 📋 Planned |
| F026 | Read / Summarise Emails | Communication | P2 | Medium | v1.5 | ⏸️ Deferred |
| F027 | Check Calendar Availability | Calendar | P1 | Medium | v1.0 | 📋 Planned |
| F028 | Create Calendar Event | Calendar | P1 | Medium | v1.0 | 📋 Planned |
| F029 | Reschedule / Edit Event | Calendar | P1 | Medium | v1.0 | 📋 Planned |
| F030 | Delete Calendar Event | Calendar | P1 | Low | v1.0 | 📋 Planned |
| F031 | Conflict Detection | Calendar | P1 | Low | v1.0 | 📋 Planned |
| F032 | Multi-attendee Scheduling | Calendar | P2 | High | v1.5 | ⏸️ Deferred |
| F033 | Google Meet Link Auto-gen | Calendar | P2 | Low | v1.0 | 📋 Planned |
| F034 | Create Task | Tasks | P1 | Low | v1.0 | 📋 Planned |
| F035 | Set Reminder (Time-based) | Tasks | P1 | Low | v1.0 | 📋 Planned |
| F036 | View Pending Tasks | Tasks | P1 | Low | v1.0 | 📋 Planned |
| F037 | Mark Task Complete | Tasks | P1 | Low | v1.0 | 📋 Planned |
| F038 | Overdue Task Detection | Tasks | P1 | Low | v1.0 | 📋 Planned |
| F039 | Task Snooze | Tasks | P2 | Low | v1.0 | 📋 Planned |
| F040 | Contact-linked Tasks | Tasks | P2 | Low | v1.0 | 📋 Planned |
| F041 | Recurring Tasks | Tasks | P3 | Medium | v1.5 | ⏸️ Deferred |
| F042 | Real-time Meeting Transcription | Meeting | P2 | High | v1.0 | 📋 Planned |
| F043 | Meeting Summary Generation | Meeting | P2 | Medium | v1.0 | 📋 Planned |
| F044 | Action Item Extraction | Meeting | P2 | Medium | v1.0 | 📋 Planned |
| F045 | Summary Share to Attendees | Meeting | P2 | Medium | v1.0 | 📋 Planned |
| F046 | Pre-meeting File Suggestions | Meeting | P2 | Medium | v1.0 | 📋 Planned |
| F047 | Post-meeting Follow-up Prompt | Meeting | P2 | Low | v1.0 | 📋 Planned |
| F048 | Meeting Transcript Storage | Meeting | P2 | Low | v1.0 | 📋 Planned |
| F049 | Speaker Identification | Meeting | P3 | High | v2.0 | ⏸️ Deferred |
| F050 | Intent Recognition (NLU) | Intelligence | P1 | High | v1.0 | 📋 Planned |
| F051 | Multi-intent Parsing | Intelligence | P1 | High | v1.0 | 📋 Planned |
| F052 | Single Clarifying Question | Intelligence | P1 | Medium | v1.0 | 📋 Planned |
| F053 | Tool Selection / Routing | Intelligence | P1 | High | v1.0 | 📋 Planned |
| F054 | Smart Channel Selection | Intelligence | P2 | Medium | v1.0 | 📋 Planned |
| F055 | Proactive Follow-up Suggestion | Intelligence | P2 | Medium | v1.0 | 📋 Planned |
| F056 | Pre-meeting Context Suggestion | Intelligence | P2 | Medium | v1.0 | 📋 Planned |
| F057 | Calendar Overload Detection | Intelligence | P3 | Medium | v1.5 | ⏸️ Deferred |
| F058 | Emotion-aware Responses | Intelligence | P3 | High | v2.0 | ⏸️ Deferred |
| F059 | Short-term Memory (Session) | Memory | P1 | Medium | v1.0 | 📋 Planned |
| F060 | Long-term Preference Storage | Memory | P1 | Medium | v1.0 | 📋 Planned |
| F061 | Episodic Memory (Past Actions) | Memory | P2 | Medium | v1.0 | 📋 Planned |
| F062 | Memory Correction by User | Memory | P1 | Low | v1.0 | 📋 Planned |
| F063 | Contact Interaction Tracking | Memory | P2 | Low | v1.0 | 📋 Planned |
| F064 | Tone Preference per Contact | Memory | P2 | Low | v1.0 | 📋 Planned |
| F065 | Nightly Memory Consolidation | Memory | P2 | Medium | v1.0 | 📋 Planned |
| F066 | Behavioral Learning Engine | Memory | P3 | High | v2.0 | ⏸️ Deferred |
| F067 | Morning Briefing Generation | Briefing | P1 | High | v1.0 | 📋 Planned |
| F068 | Briefing TTS Playback | Briefing | P1 | Low | v1.0 | 📋 Planned |
| F069 | Briefing Push Notification | Briefing | P1 | Low | v1.0 | 📋 Planned |
| F070 | Briefing → Live Conversation | Briefing | P1 | Medium | v1.0 | 📋 Planned |
| F071 | Configurable Briefing Time | Briefing | P2 | Low | v1.0 | 📋 Planned |
| F072 | Briefing History View | Briefing | P3 | Low | v1.5 | ⏸️ Deferred |
| F073 | Multi-step Automation Engine | Automation | P1 | High | v1.0 | 📋 Planned |
| F074 | Step Dependency Resolution | Automation | P1 | High | v1.0 | 📋 Planned |
| F075 | Automation Error Handling | Automation | P1 | Medium | v1.0 | 📋 Planned |
| F076 | Automation Progress Tracker (UI) | Automation | P1 | Medium | v1.0 | 📋 Planned |
| F077 | Completion Notification | Automation | P1 | Low | v1.0 | 📋 Planned |
| F078 | Pre-execution Plan Preview | Automation | P1 | Low | v1.0 | 📋 Planned |
| F079 | Retry Failed Steps | Automation | P1 | Low | v1.0 | 📋 Planned |
| F080 | Saved Automation Templates | Automation | P3 | Medium | v2.0 | ⏸️ Deferred |

**Total features:** 80 | **v1.0:** 60 | **v1.5:** 7 | **v2.0:** 5 | **Deferred:** 20 (8+)

---

## 3.0 Detailed Feature Breakdown

---

### 3.1 Voice & Conversation Features

---

#### F001 — Wake Word Detection

| Field | Detail |
|-------|--------|
| **Feature ID** | F001 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Always-on, on-device listening for the trigger phrase "Hey Alex". Runs entirely on-device using Porcupine (Picovoice). No audio transmitted to cloud before wake word fires.

**What it does:**
- Continuously monitors device mic in low-power background mode
- Detects "Hey Alex" with < 500ms latency
- Activates full microphone and shows listening UI on detection

**What it does NOT do:**
- Does NOT stream audio to cloud before wake word detection
- Does NOT support custom wake words in v1.0
- Does NOT work when app is force-closed

**User Benefit:** Hands-free activation at any time without touching the phone.

**Technical Requirements:**
- Porcupine SDK (iOS + Android, Picovoice)
- Background app refresh permission
- Always-on low-power wake word model (< 2% battery/hour)

**Dependencies:** F002 (STT triggered on activation), device microphone permission

---

#### F002 — Speech-to-Text (Streaming)

| Field | Detail |
|-------|--------|
| **Feature ID** | F002 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Converts user speech to text in real time using Deepgram Nova-3 via WebSocket streaming. Partial transcripts display live in the UI. Final transcript locked on silence detection.

**What it does:**
- Streams audio to Deepgram via WebSocket
- Returns partial transcripts during speech (shown live via F007)
- Delivers final, punctuated transcript on 500ms silence
- Strips filler words ("um", "uh") by default

**What it does NOT do:**
- Does NOT support non-English speech in v1.0
- Does NOT operate offline
- Does NOT support multiple simultaneous speakers

**User Benefit:** User sees words appear as they speak; no wait time for processing.

**Technical Requirements:**
- Deepgram Nova-3, WebSocket endpoint
- API key server-side only
- Config: `smart_format: true`, `punctuate: true`, `interim_results: true`, endpointing 500ms

**Dependencies:** F001 (wake word activates), F006 (processes transcript), internet required

---

#### F003 — Text-to-Speech (Streaming)

| Field | Detail |
|-------|--------|
| **Feature ID** | F003 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Converts Alex's text responses to audio using ElevenLabs `eleven_turbo_v2`. Audio streamed in chunks as text generates, minimising perceived latency. Fallback to Google Cloud TTS (WaveNet).

**What it does:**
- Streams first audio chunk ≤ 400ms of first text token
- Plays audio while text is still being generated
- Stops immediately if user interrupts (wake word or tap)
- Single consistent Alex voice identity

**What it does NOT do:**
- Does NOT support multiple voice options in v1.0
- Does NOT generate audio for responses > 500 words (truncates to key points; full text shown in UI)

**User Benefit:** Alex feels responsive — no awkward silence waiting for full response.

**Technical Requirements:**
- ElevenLabs API, `eleven_turbo_v2`, WebSocket streaming
- Fallback: Google Cloud TTS WaveNet en-US
- Audio: MP3, 22kHz; player: `expo-av`
- Interruption: Porcupine detection → immediate stop

**Dependencies:** F006 (produces text to speak), F001 (wake word for interruption)

---

#### F004 — Text Input Mode

| Field | Detail |
|-------|--------|
| **Feature ID** | F004 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Full-featured chat interface for typing commands to Alex. Identical intelligence as voice mode without STT/TTS layers.

**What it does:**
- Standard keyboard input with send button
- All features available as in voice mode
- Markdown rendering for structured responses
- Maintains full conversation context

**What it does NOT do:**
- Does NOT read responses aloud unless user taps the speaker icon explicitly

**User Benefit:** Usable in quiet environments, meetings, or when mic is unavailable.

**Technical Requirements:**
- React Native TextInput, same API pipeline as voice, markdown renderer

**Dependencies:** F006 (conversation context), F050 (intent recognition)

---

#### F005 — Voice ↔ Text Mode Switch

| Field | Detail |
|-------|--------|
| **Feature ID** | F005 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Seamlessly switch between voice and text mid-conversation without losing context. Mic and keyboard icons toggle modes.

**What it does:**
- Mic button activates voice; keyboard shows text field
- Full conversation history visible in both modes
- No context reset on mode switch

**What it does NOT do:** Does NOT change Alex's behavior based on input mode

**Technical Requirements:** UI state toggle; no context reset; both inputs feed same pipeline

**Dependencies:** F002, F003, F004, F006

---

#### F006 — Context-Aware Conversation

| Field | Detail |
|-------|--------|
| **Feature ID** | F006 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
Alex maintains full conversational context across a session — resolving pronouns, implicit references, and prior actions correctly. Powered by Claude with Redis session state and Supabase long-term memory injection.

**What it does:**
- Retains last 20 conversation turns in Redis (sliding window)
- Injects history into every Claude API call
- Resolves pronouns and implicit references ("that file", "him")
- Summarises older turns into Supabase when window fills (> 20 turns)
- New session pre-loaded with long-term memory from F060

**What it does NOT do:**
- Does NOT retain full verbatim history beyond 20 turns in active context
- Does NOT retain context across Redis TTL expiry (24h session)

**User Benefit:** Natural conversation — user never has to repeat themselves.

**Technical Requirements:**
- Redis session store: `session:{id}:history`, 20-turn sliding window, 24h TTL
- Context injection into Claude dynamic Layer 3
- Session summary job on turn > 20

**Dependencies:** F059 (Redis), F060 (Supabase), F050 (intent recognition)

---

#### F007 — Live Transcript Display

| Field | Detail |
|-------|--------|
| **Feature ID** | F007 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
Deepgram partial transcripts appear in the UI in real time as the user speaks. Final punctuated text replaces partials on silence.

**What it does:** Animated greyed partial text → final confirmed text on silence detection

**What it does NOT do:** Does NOT allow editing of transcript before submission in v1.0

**Technical Requirements:** WebSocket listener for Deepgram `is_final: false` events; React Native Animated API

**Dependencies:** F002 (STT streaming)

---

#### F008 — Noise Handling / Retry

| Field | Detail |
|-------|--------|
| **Feature ID** | F008 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
When STT returns empty or low-confidence transcript, Alex prompts retry. After 2 failures, offers text fallback.

**What it does:**
- Detects: empty transcript or confidence < 0.4
- Retry 1: "I didn't catch that — could you say it again?"
- Retry 2 (final): "Having trouble hearing you — you can type instead." → highlights text field

**What it does NOT do:** Does NOT re-prompt more than twice (prevents frustration loops)

**Technical Requirements:** Deepgram confidence score threshold, retry counter max 2 per turn

**Dependencies:** F002 (STT), F004 (text fallback)

---

### 3.2 File Management Features

---

#### F009 — File Indexing (Google Drive)

| Field | Detail |
|-------|--------|
| **Feature ID** | F009 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
Crawls and indexes the user's Google Drive automatically. Extracts text from supported file types, generates semantic embeddings, stores in pgvector. Runs on setup and incrementally every 15 minutes.

**What it does:**
- Full index on first setup; delta sync every 15 minutes thereafter
- Extracts text from: PDF, DOCX, XLSX, Google Docs, Google Sheets, TXT, MD
- Generates 1536-dim embeddings (text-embedding-3-small)
- Stores: file name, Drive ID, MIME type, URL, content preview (2000 chars), embedding, last modified

**What it does NOT do:**
- Does NOT index images, video, audio, or Google Slides in v1.0
- Does NOT index "Shared with me" by default (opt-in setting)
- Does NOT store full file content — only first 2000 chars as preview
- Does NOT index files > 50MB (skipped with log warning)

**User Benefit:** Everything in Google Drive becomes findable by meaning, not just file name.

**Technical Requirements:**
- Google Drive API v3: `files.list`, `files.get`, `files.export`
- OAuth scope: `drive.readonly`
- BullMQ indexing pipeline
- pgvector in Supabase
- Parsers: pdf-parse, mammoth.js, SheetJS
- Chunking: 512 tokens, 50-token overlap

**Dependencies:** F014 (parsing), Google OAuth, Supabase pgvector, OpenAI Embeddings API

---

#### F010 — Semantic File Search

| Field | Detail |
|-------|--------|
| **Feature ID** | F010 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
Finds files by meaning using cosine similarity between query embedding and indexed file embeddings. Returns ranked results in ≤ 3 seconds. Case-insensitive.

**What it does:**
- Embeds natural language query → cosine similarity vs pgvector index
- Returns top 5 results: name, date, preview snippet, similarity score
- Filters results below score 0.5
- Recency boost: `final_score = similarity * 0.7 + recency * 0.3`

**What it does NOT do:**
- Does NOT search within file content for specific passages in v1.0
- Does NOT search non-indexed platforms (Dropbox, OneDrive — v1.5)
- Does NOT support boolean operators — all queries are semantic

**User Benefit:** Find files by description ("the contract I sent Priya") even with wrong file name.

**Technical Requirements:**
- pgvector `<=>` cosine operator; top-k=5; threshold=0.5
- Same embedding model as F009 (text-embedding-3-small)
- Recency score: exponential decay by days since last_modified

**Dependencies:** F009 (indexing must run first), F011 (ranking), OpenAI Embeddings API

---

#### F011 — File Result Ranking

| Field | Detail |
|-------|--------|
| **Feature ID** | F011 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Composite ranking formula: semantic similarity (70%) + recency (20%) + interaction frequency (10%). Auto-selects single top result if score gap > 0.15; otherwise presents list of top 3.

**What it does:**
- Applies composite score formula to search results
- Auto-selects if #1 score gap over #2 is > 0.15
- Presents top 3 list if scores are clustered
- Boosts files previously opened or sent by user

**What it does NOT do:** Does NOT learn per-query click-through in v1.0 (static formula)

**Technical Requirements:**
- Composite score formula in file search service
- `files_accessed` counter column in files table
- Recency: exponential decay

**Dependencies:** F010 (search results to rank), F063 (access frequency signal)

---

#### F012 — File Preview in Chat

| Field | Detail |
|-------|--------|
| **Feature ID** | F012 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
Compact file card in chat UI after any search result. Shows: file type icon, name, last modified date, 100-char content snippet. [Open] deep-links to Google Drive; [Send] initiates send flow.

**What it does NOT do:** Does NOT render file content inline; no PDF viewer in chat

**Technical Requirements:** File card UI component (React Native), Drive deep-link URL construction

**Dependencies:** F010 (search result), F009 (content preview data)

---

#### F013 — File Re-index on Demand

| Field | Detail |
|-------|--------|
| **Feature ID** | F013 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
User triggers full Drive re-index via voice ("Alex, reindex my files") or Settings. Shows progress, notifies on complete. Rate-limited to once per hour.

**Technical Requirements:**
- `POST /v1/files/index { force: true }` endpoint
- BullMQ job progress tracking; push notification on completion

**Dependencies:** F009 (indexing), F069 (push notification)

---

#### F014 — Multi-format File Parsing

| Field | Detail |
|-------|--------|
| **Feature ID** | F014 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Extracts readable text from all supported file formats during indexing. Outputs plain text chunks for embedding.

**Supported formats and parsers:**

| Format | Parser |
|--------|--------|
| PDF | pdf-parse (Node.js) |
| DOCX | mammoth.js |
| XLSX / Google Sheets | SheetJS (first 3 sheets, 100 rows) |
| Google Docs | Drive export API (text/plain) |
| TXT / MD | Native string |

**What it does NOT do:** Does NOT parse images in documents (OCR = v2.0); does NOT parse password-protected files

**Technical Requirements:**
- Node.js: pdf-parse@1.x, mammoth@1.x, xlsx@0.x
- Chunking: 512-token segments, 50-token overlap (tiktoken)

**Dependencies:** F009 (calls this service during indexing)

---

### 3.3 Communication Features

---

#### F017 — Send Email (Gmail)

| Field | Detail |
|-------|--------|
| **Feature ID** | F017 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
Alex drafts and sends email via Gmail API. Subject and body generated by Claude. Auto-sends for frequent contacts; shows draft preview for new contacts. Supports file attachments.

**What it does:**
- Resolves contact name → email address (F024)
- Claude drafts: subject + body, tone-matched (F020)
- Auto-send for contacts with > 3 prior emails; preview for new contacts (F018)
- Attaches files as Google Drive shareable links (F019)
- Confirms: "Sent to [name] at [email]."
- Logs to sent_messages (F025)

**What it does NOT do:**
- Does NOT read or reply to received emails in v1.0 (F026, deferred)
- Does NOT send to multiple recipients simultaneously in v1.0
- Does NOT use HTML email templates — plain text only
- Does NOT handle CC/BCC in v1.0

**User Benefit:** Sends emails completely hands-free; no app-switching.

**Technical Requirements:**
- Gmail API: `users.messages.send`; OAuth scope: `gmail.send`
- MIME message construction (nodemailer / googleapis)
- Retry on 5xx: max 3 attempts, exponential backoff

**Dependencies:** F018 (preview), F019 (attach), F020 (tone), F024 (contact), F025 (log), Google OAuth

---

#### F018 — Email Draft Preview

| Field | Detail |
|-------|--------|
| **Feature ID** | F018 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Before sending to a new or rare contact, shows full draft in a modal: To, Subject, Body. Actions: [Send ✓] [Edit] [Cancel ✗]. [Edit] opens inline editing before send. Remembers user's "always send" preference per contact.

**What it does NOT do:**
- Does NOT show preview for contacts with > 3 prior emails (auto-send mode)

**Technical Requirements:**
- Modal overlay (React Native)
- Inline edit fields for subject + body
- `skip_preview: boolean` flag in contacts table

**Dependencies:** F017 (email send), F064 (contact preferences)

---

#### F019 — Email with File Attachment

| Field | Detail |
|-------|--------|
| **Feature ID** | F019 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Searches Drive for the file, asks user to confirm correct file, generates a Google Drive view-only shareable link, inserts into email body as "Attached: [file name]".

**What it does NOT do:**
- Does NOT attach files as binary inline attachments (uses Drive links for deliverability)
- Does NOT manage Drive permissions beyond "view"

**Technical Requirements:**
- Google Drive API: `permissions.create` (role: reader, type: anyone)
- Always confirms correct file before attaching (USER_FLOW § 5.1)

**Dependencies:** F010 (file search), F017 (email send), Google Drive API

---

#### F020 — Tone-Matched Email Drafting

| Field | Detail |
|-------|--------|
| **Feature ID** | F020 |
| **Priority** | P2 — Phase v1.0 — Complexity: Medium |

**Description:**
Adjusts email tone (Formal / Balanced / Casual) based on global user preference and per-contact override (F064). Passed as instruction to Claude during email drafting.

**What it does NOT do:**
- Does NOT modify tone after user has edited the draft
- Does NOT infer relationship type automatically in v1.0

**Technical Requirements:**
- Tone prompt injection: "Draft this email in [tone] style."
- Tone value from: memory (contact-level) or user profile (global fallback)

**Dependencies:** F060 (preferences), F064 (per-contact tone), F017 (email)

---

#### F021 — Send WhatsApp Message

| Field | Detail |
|-------|--------|
| **Feature ID** | F021 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
Sends WhatsApp message via Meta Business Cloud API. Claude drafts message content. Handles 24h window policy (F023). Registers webhook for delivery status.

**What it does:**
- Resolves contact → phone number (F024)
- Claude drafts message content, tone-matched
- 24h window check before send (F023)
- Logs to sent_messages (F025)
- Webhook: delivery/read status updates

**What it does NOT do:**
- Does NOT send to groups in v1.0
- Does NOT support WhatsApp voice messages
- Does NOT read incoming WhatsApp messages in v1.0

**Technical Requirements:**
- Meta WhatsApp Business Cloud API
- Permanent system user access token (encrypted in Supabase)
- Webhook: `POST /webhooks/whatsapp`
- Phone format: E.164

**Dependencies:** F023 (24h window), F024 (contact), F025 (logging)

---

#### F022 — WhatsApp File Attachment

| Field | Detail |
|-------|--------|
| **Feature ID** | F022 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Downloads file from Google Drive to server (temp), uploads to Meta media API, attaches media_id to message. Cleans up temp file after send. Files > 100MB: offers Drive link or email alternative.

**Technical Requirements:**
- Meta Media API: `POST /media` → media_id
- Google Drive: `files.get?alt=media`
- Temp file cleanup: 60s post-send
- Size check before download

**Dependencies:** F010 (file search), F021 (WhatsApp send)

---

#### F023 — WhatsApp 24h Window Handling

| Field | Detail |
|-------|--------|
| **Feature ID** | F023 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Enforces Meta's 24-hour messaging policy. Checks last interaction timestamp per contact. Outside 24h: presents email alternative or approved template. Never sends freeform outside window.

**What it does NOT do:** Does NOT attempt freeform messages outside the 24h window (violates Meta ToS)

**Technical Requirements:**
- Window check: `Date.now() - last_interaction_at > 86400000ms`
- Pre-approved template IDs in environment config
- `last_interaction_at` updated on every send

**Dependencies:** F021 (WhatsApp send), F025 (message logging for timestamp)

---

#### F024 — Contact Resolution Engine

| Field | Detail |
|-------|--------|
| **Feature ID** | F024 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Resolves spoken/typed names to contact records. Multi-step resolution: exact match → fuzzy match (Levenshtein ≤ 2) → context inference (pronouns) → role match ("my lawyer") → disambiguation list.

**What it does:**
- 5-step resolution pipeline (see above)
- Presents up to 3 candidates if still ambiguous after all steps
- Stores new contacts when user provides email/phone for unknown names

**What it does NOT do:**
- Does NOT pull from phone address book in v1.0 (Gmail-sourced + manually added contacts only)
- Does NOT guess if > 3 matches with equal likelihood

**Technical Requirements:**
- Levenshtein: `fast-levenshtein` (Node.js)
- Contacts table: name, email, phone, tags, last_interaction_at
- Disambiguation UI: inline list in chat

**Dependencies:** F059 (pronoun resolution from context), F063 (recency boost)

---

#### F025 — Sent Message Logging

| Field | Detail |
|-------|--------|
| **Feature ID** | F025 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Logs every sent email and WhatsApp message to `sent_messages` table. Enables 24h window checks, interaction tracking, conversation history, and audit trail. Stores only 200-char body preview (privacy).

**Technical Requirements:**
- Supabase insert on every successful send
- WhatsApp webhook handler updates `status` field (sent/delivered/read)

**Dependencies:** F017 (email), F021 (WhatsApp)

---

### 3.4 Calendar & Scheduling Features

---

#### F027 — Check Calendar Availability

| Field | Detail |
|-------|--------|
| **Feature ID** | F027 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Queries Google Calendar for free time slots on a given date. Respects configured working hours. Used as a standalone query and as a dependency for event creation.

**What it does NOT do:**
- Does NOT check other attendees' availability in v1.0 (F032, v1.5)

**Technical Requirements:**
- Google Calendar API: `events.list` with `timeMin`, `timeMax`, `singleEvents: true`
- Free/busy computation in application layer
- Working hours from user profile (F060)

**Dependencies:** Google Calendar OAuth, F060 (working hours preference)

---

#### F028 — Create Calendar Event

| Field | Detail |
|-------|--------|
| **Feature ID** | F028 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Creates a new Google Calendar event with title, time, attendees, description, and auto-generated Google Meet link. Sends calendar invites to all attendees. Always requires confirmation before sending if attendees included.

**Technical Requirements:**
- Google Calendar API: `events.insert` with `sendUpdates: 'all'`
- conferenceData: `createRequest` with UUID
- Mandatory confirmation for events with attendees (USER_FLOW § 5.1)

**Dependencies:** F027 (availability), F031 (conflict), F033 (Meet link), F024 (contact resolution for attendees)

---

#### F029 — Reschedule / Edit Event

| Field | Detail |
|-------|--------|
| **Feature ID** | F029 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Updates an existing event's time, title, or attendees. Notifies all attendees of changes. Always requires user confirmation before patching.

**What it does NOT do:** Does NOT reschedule recurring events in v1.0

**Technical Requirements:**
- Google Calendar API: `events.patch` with `sendUpdates: 'all'`
- Event ID identified from title + date in conversation context

**Dependencies:** F027 (new slot availability), F031 (conflict at new time)

---

#### F030 — Delete Calendar Event

| Field | Detail |
|-------|--------|
| **Feature ID** | F030 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Cancels and deletes a calendar event. Sends cancellation emails to all attendees. Always requires explicit two-step confirmation (irreversible action).

**What it does NOT do:** Does NOT support undo after confirmation

**Technical Requirements:**
- Google Calendar API: `events.delete` with `sendUpdates: 'all'`
- Mandatory destructive confirmation UI (USER_FLOW § 5.2)

**Dependencies:** F028 (event context)

---

#### F031 — Conflict Detection

| Field | Detail |
|-------|--------|
| **Feature ID** | F031 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Before creating or rescheduling, checks if proposed time overlaps with an existing event. Surfaces conflict and suggests next available slot. Allows user to override and double-book if they choose.

**Technical Requirements:**
- Time overlap check: `(new_start < existing_end) && (new_end > existing_start)`
- Alternative slot: next free slot in same day within working hours

**Dependencies:** F027 (availability), F028 (event creation)

---

#### F033 — Google Meet Link Auto-generation

| Field | Detail |
|-------|--------|
| **Feature ID** | F033 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
Automatically attaches a Google Meet video link when creating a calendar event. Link included in invite and confirmed to user.

**Technical Requirements:**
- `conferenceData: { createRequest: { requestId: uuid() } }` in event payload
- `conferenceDataVersion: 1` parameter required

**Dependencies:** F028 (event creation)

---

### 3.5 Task & Reminder Features

---

#### F034 — Create Task

| Field | Detail |
|-------|--------|
| **Feature ID** | F034 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Creates a task in Supabase with title, optional due date, optional related contact, and source (voice / auto / meeting). Auto-confirms immediately.

**What it does NOT do:**
- Does NOT integrate with Notion, Todoist, or external task managers in v1.0
- Does NOT support subtasks in v1.0

**Technical Requirements:** Supabase `tasks` insert; `POST /v1/tasks` endpoint

**Dependencies:** F024 (contact for related_contact_id), F035 (reminder if due_at set)

---

#### F035 — Set Reminder (Time-based)

| Field | Detail |
|-------|--------|
| **Feature ID** | F035 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Schedules a push notification at a specified date/time. On notification tap: opens Alex with task context and offers contextual shortcuts: [Send email] [Send WhatsApp] [Mark done] [Snooze 2h].

**What it does NOT do:** Does NOT support location-based reminders in v1.0

**Technical Requirements:**
- `expo-notifications` for local push scheduling
- Server-side backup via node-cron to catch missed local notifications
- Notification payload includes: task_id, title, contact_id

**Dependencies:** F034 (task), F069 (push notifications)

---

#### F036 — View Pending Tasks

| Field | Detail |
|-------|--------|
| **Feature ID** | F036 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Returns task list filtered by status. Voice: reads top 5 aloud (overdue first). UI: Tasks screen with filters (All / Overdue / Today / Upcoming). Each task card: title, due date, contact, status.

**Technical Requirements:**
- `GET /v1/tasks?status=pending,overdue`
- Supabase query ORDER BY: overdue first, then due_at ASC

**Dependencies:** F034 (task creation), F038 (overdue detection)

---

#### F037 — Mark Task Complete

| Field | Detail |
|-------|--------|
| **Feature ID** | F037 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Marks task complete by voice, UI tap, or notification shortcut. Sets `status: 'completed'`, `completed_at: now()`. Confirms immediately.

**Technical Requirements:**
- `PATCH /v1/tasks/:id { status: 'completed' }`
- Fuzzy name match for voice command

**Dependencies:** F036 (task list for name matching)

---

#### F038 — Overdue Task Detection

| Field | Detail |
|-------|--------|
| **Feature ID** | F038 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Hourly cron job flags tasks past their due date. Overdue tasks surfaced in morning briefing and on demand. Batched — not per-task push notifications every hour.

**Technical Requirements:**
- node-cron: `0 * * * *`
- `UPDATE tasks SET status='overdue' WHERE due_at < NOW() AND status='pending'`

**Dependencies:** F034 (task creation), F067 (briefing includes overdue)

---

#### F039 — Task Snooze

| Field | Detail |
|-------|--------|
| **Feature ID** | F039 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
Snooze a reminder from notification or task list. Options: 2h (default), tomorrow morning, or custom. Re-schedules notification and updates `due_at`.

**Technical Requirements:**
- Notification action buttons (expo-notifications)
- `PATCH /v1/tasks/:id { due_at: new_time }`

**Dependencies:** F034, F035

---

#### F040 — Contact-linked Tasks

| Field | Detail |
|-------|--------|
| **Feature ID** | F040 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
Tasks linked to a contact surface contact-specific action shortcuts on reminder notifications (e.g., [Send email to Arjun]).

**Technical Requirements:**
- FK: `tasks.related_contact_id → contacts.id`
- Notification payload includes contact_id for action routing

**Dependencies:** F034, F024, F035

---

### 3.6 Meeting Features

---

#### F042 — Real-time Meeting Transcription

| Field | Detail |
|-------|--------|
| **Feature ID** | F042 |
| **Priority** | P2 — Phase v1.0 — Complexity: High |

**Description:**
Records and transcribes a meeting in real time via Deepgram streaming (separate WebSocket instance from voice commands). User activates/deactivates manually. Live transcript scrolls in app. Full transcript saved to Supabase on session end.

**What it does NOT do:**
- Does NOT identify individual speakers in v1.0 (F049, v2.0)
- Does NOT transcribe audio from other apps (Zoom, Meet) — device mic only
- Does NOT run transcription and voice commands simultaneously on the same mic

**Technical Requirements:**
- Dedicated Deepgram WebSocket instance; `diarize: false`, `smart_format: true`
- Transcript buffered in Redis; flushed to Supabase on session end
- Full-screen transcript panel UI with [End] button

**Dependencies:** F002 (Deepgram infrastructure), F048 (transcript storage)

---

#### F043 — Meeting Summary Generation

| Field | Detail |
|-------|--------|
| **Feature ID** | F043 |
| **Priority** | P2 — Phase v1.0 — Complexity: Medium |

**Description:**
Claude processes full transcript post-meeting and generates a 5–10 point summary of key decisions and discussions. Delivered within 2 minutes of meeting end via push notification. Stored in `events.summary`.

**What it does NOT do:** Does NOT generate summaries for meetings < 2 minutes

**Technical Requirements:**
- BullMQ job triggered on transcription end
- Claude API call with full transcript (max 100k tokens)
- Push notification on job completion

**Dependencies:** F042 (transcript), F069 (push)

---

#### F044 — Action Item Extraction

| Field | Detail |
|-------|--------|
| **Feature ID** | F044 |
| **Priority** | P2 — Phase v1.0 — Complexity: Medium |

**Description:**
Claude identifies all explicitly stated action items, assignments, and commitments from the transcript. Creates tasks for user-assigned items. Flags ambiguous items for review.

**What it does NOT do:**
- Does NOT auto-notify other participants of their action items (user approves first)
- Does NOT create calendar events for deadlines — tasks only

**Technical Requirements:**
- Claude prompt → JSON output: `[{owner, action, due_date_if_mentioned}]`
- `POST /v1/tasks` for each user-assigned item, `source: 'meeting'`

**Dependencies:** F042 (transcript), F043 (runs in same BullMQ job), F034 (task creation)

---

#### F045 — Summary Share to Attendees

| Field | Detail |
|-------|--------|
| **Feature ID** | F045 |
| **Priority** | P2 — Phase v1.0 — Complexity: Medium |

**Description:**
Offers to share meeting summary to all attendees via email after user approval. Never auto-sends. Subject: "Meeting Summary — [Date] — [Event Title]".

**Technical Requirements:**
- Attendee list from `events.attendees` JSONB
- One `send_email` call per attendee
- Draft preview for new-contact attendees

**Dependencies:** F043 (summary content), F017 (email), F018 (draft preview)

---

#### F046 — Pre-meeting File Suggestions

| Field | Detail |
|-------|--------|
| **Feature ID** | F046 |
| **Priority** | P2 — Phase v1.0 — Complexity: Medium |

**Description:**
10 minutes before a calendar event with attendees, surfaces top 2 relevant files and recent communication. Push notification with quick-access file cards and 3-sentence context summary.

**Technical Requirements:**
- Scheduler: BullMQ delayed job per upcoming event (fires at event.start_at - 10min)
- File search query: event title + attendee names
- Claude synthesises into 3-sentence context brief

**Dependencies:** F010 (file search), F027 (calendar), F069 (push)

---

#### F047 — Post-meeting Follow-up Prompt

| Field | Detail |
|-------|--------|
| **Feature ID** | F047 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
30 minutes after meeting end, Alex suggests drafting a follow-up email. Pre-drafts using meeting context (summary if available). User reviews and sends or dismisses.

**What it does NOT do:** Does NOT send follow-up automatically without user approval

**Technical Requirements:**
- BullMQ delayed job: delay = 30min from event `end_at`
- Claude drafts using: event title + summary (if available) + attendees

**Dependencies:** F027 (calendar events), F043 (summary), F017 (email)

---

#### F048 — Meeting Transcript Storage

| Field | Detail |
|-------|--------|
| **Feature ID** | F048 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
Stores full transcript text in `events.transcript`. Accessible in-app for 90 days, then soft-archived. [View Full Transcript] button on meeting summary screen.

**Technical Requirements:**
- `events.transcript TEXT` column in Supabase
- Soft archive flag after 90 days (no deletion)

**Dependencies:** F042 (transcription), F043 (summary references this)

---

### 3.7 Intelligence & Decision Features

---

#### F050 — Intent Recognition (NLU)

| Field | Detail |
|-------|--------|
| **Feature ID** | F050 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
Core AI engine that maps user input to actionable intent and tool calls. Powered entirely by Claude (no separate NLU model). Target accuracy: ≥ 88%.

**What it does:**
- Receives raw input + full conversation context
- Claude identifies: intent, entities (contacts, files, dates), action type
- Maps to tool call(s) via `tool_choice: auto`
- Triggers F052 if confidence is insufficient

**What it does NOT do:** Does NOT operate offline

**Technical Requirements:**
- Claude API with tool use; `auto` tool choice mode
- System prompt includes all 12 tool definitions and behavioral rules
- Confidence heuristic: Claude returns uncertainty markers → trigger F052

**Dependencies:** F006 (context), F053 (tool routing)

---

#### F051 — Multi-intent Parsing

| Field | Detail |
|-------|--------|
| **Feature ID** | F051 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
Identifies compound commands with multiple distinct intents and generates a structured automation plan for the Automation Engine. Max 8 steps per plan in v1.0.

**Technical Requirements:**
- Claude system prompt rule: "If the input contains multiple actions, return a JSON plan array."
- Plan schema: `[{ step_id, tool, params, depends_on }]`

**Dependencies:** F050 (intent recognition), F073 (automation engine executes the plan)

---

#### F052 — Single Clarifying Question

| Field | Detail |
|-------|--------|
| **Feature ID** | F052 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
When intent is ambiguous (< 80% confidence), Alex asks exactly ONE targeted question — the minimum needed to proceed. Never asks multiple questions per turn.

**Technical Requirements:**
- System prompt rule: "If you need clarification, ask ONLY ONE question."
- Clarification turn stored in conversation context (F006)

**Dependencies:** F050 (intent), F006 (context)

---

#### F053 — Tool Selection / Routing

| Field | Detail |
|-------|--------|
| **Feature ID** | F053 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
After intent recognition, Claude selects and executes the correct tool(s) from the 12-tool library. Handles chained calls (result of one tool feeds next). Max chain: 5 tool calls per request.

**Technical Requirements:**
- `switch(tool_name)` dispatch in tool executor
- Tool result injection: `tool_result` message appended before next Claude call
- Max 5 tool calls per request to prevent loops

**Dependencies:** F050 (intent), all tool implementations

---

#### F054 — Smart Channel Selection

| Field | Detail |
|-------|--------|
| **Feature ID** | F054 |
| **Priority** | P2 — Phase v1.0 — Complexity: Medium |

**Description:**
When channel not specified ("message Priya"), uses contact's preferred_channel or most recent channel from sent_messages. Defaults to email with notification to user. Learns from corrections.

**Technical Requirements:**
- Channel preference logic in contact resolution service
- `preferred_channel` updated on user correction

**Dependencies:** F024 (contact), F063 (interaction tracking), F060 (memory)

---

#### F055 — Proactive Follow-up Suggestion

| Field | Detail |
|-------|--------|
| **Feature ID** | F055 |
| **Priority** | P2 — Phase v1.0 — Complexity: Medium |

**Description:**
After key events (meeting end, email sent to important contact, task completed), proactively suggests relevant next actions. Non-intrusive, dismissible. Max 2 suggestions per hour.

**Technical Requirements:**
- Event listeners on: meeting_end, email_sent, task_completed
- Suggestion cooldown in Redis (TTL: 1h per type)
- Declined suggestions tracked for 24h (not repeated)

**Dependencies:** F006 (context), F043 (meeting summary), F065 (memory for past declines)

---

#### F056 — Pre-meeting Context Suggestion

| Field | Detail |
|-------|--------|
| **Feature ID** | F056 |
| **Priority** | P2 — Phase v1.0 — Complexity: Medium |

**Description:**
10 minutes before an event, surfaces: top 2 relevant files, last communication with attendees, and open tasks linked to attendees. Compact notification + in-app context panel.

**Technical Requirements:**
- Same scheduler as F046
- Combines: file search + sent_messages query + tasks query
- Claude synthesises into 3-sentence brief

**Dependencies:** F046, F036, F025

---

### 3.8 Memory & Personalization Features

---

#### F059 — Short-term Memory (Session)

| Field | Detail |
|-------|--------|
| **Feature ID** | F059 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Active conversation context (last 20 turns) stored in Redis with 24h TTL. Injected into every Claude call. Sliding window: turn 21 triggers summarisation of turns 1–10 into Supabase.

**Technical Requirements:**
- Redis (Upstash): LPUSH + LTRIM for sliding window
- Session key: `session:{session_id}:history`
- Serialisation: JSON; TTL: 24h

**Dependencies:** Redis (Upstash), F006 (conversation)

---

#### F060 — Long-term Preference Storage

| Field | Detail |
|-------|--------|
| **Feature ID** | F060 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Persistent user preferences and learned facts in Supabase `memories` table. Injected into Claude system prompt Layer 2 (refreshed daily). Never expires unless deleted by user.

**Stores:** name, working hours, tone, preferred apps, wake time, timezone, learned facts
**Categories:** `preference`, `contact`, `project`, `fact`

**What it does NOT do:**
- Does NOT store sensitive personal data (financial, health) in v1.0

**Technical Requirements:**
- Supabase `memories` table; `POST /v1/memory`, `GET /v1/memory`
- System prompt Layer 2 rebuilt from memories every 24h

**Dependencies:** Supabase

---

#### F061 — Episodic Memory (Past Actions)

| Field | Detail |
|-------|--------|
| **Feature ID** | F061 |
| **Priority** | P2 — Phase v1.0 — Complexity: Medium |

**Description:**
Nightly consolidation creates episodic summaries from today's actions (sent_messages, events, completed tasks). Enables: "Last time you emailed Arjun was 3 days ago about the contract."

**Technical Requirements:**
- Claude prompt → 5–10 episodic memory entries per day
- Stored as `memories` records with `category: 'episode'`

**Dependencies:** F065 (nightly job), F025 (messages), F034 (tasks)

---

#### F062 — Memory Correction by User

| Field | Detail |
|-------|--------|
| **Feature ID** | F062 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
User corrects or deletes any stored memory by voice or via Settings → Memory screen. Updates take immediate effect.

**Voice example:** "Alex, that's wrong — Priya's email is priya@newcompany.com"
**Settings:** View / edit / delete any memory record. "Forget everything about [contact]" → deletes all related records.

**Technical Requirements:**
- `PATCH /v1/memory/:id`, `DELETE /v1/memory/:id`
- Claude identifies relevant memory from correction context

**Dependencies:** F060 (memory storage)

---

#### F063 — Contact Interaction Tracking

| Field | Detail |
|-------|--------|
| **Feature ID** | F063 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
Tracks interaction frequency and recency per contact. Piggybacks on existing write operations — no extra API calls. Used by ranking, channel selection, and follow-up suggestions.

**Technical Requirements:**
- `contacts.interaction_count` incremented on every send/meeting
- `contacts.last_interaction_at` updated on every interaction

**Dependencies:** F025 (message log), F028 (calendar events)

---

#### F064 — Tone Preference per Contact

| Field | Detail |
|-------|--------|
| **Feature ID** | F064 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
Stores tone preference per contact, overriding global tone. Auto-learned from draft edits (Alex prompts: "Should I always use this tone for Priya?"). Applied in email drafting (F020).

**Technical Requirements:**
- Memory record: `key: 'tone_for_{contact_id}'`, `value: 'casual|balanced|formal'`
- Tone inference on significant draft edit

**Dependencies:** F060 (memory), F020 (tone drafting)

---

#### F065 — Nightly Memory Consolidation

| Field | Detail |
|-------|--------|
| **Feature ID** | F065 |
| **Priority** | P2 — Phase v1.0 — Complexity: Medium |

**Description:**
11:00 PM nightly job: processes day's conversation history, sent messages, completed tasks, and calendar events into 5–10 episodic memories and preference learnings. Compresses Redis session data.

**Technical Requirements:**
- node-cron: `0 23 * * *`
- BullMQ async job
- Claude prompt: "Extract key episodic memories and preference learnings from today's activity."

**Dependencies:** F061 (episodic memory target), F059 (session history source)

---

### 3.9 Briefing & Summary Features

---

#### F067 — Morning Briefing Generation

| Field | Detail |
|-------|--------|
| **Feature ID** | F067 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
At user's configured wake time (default 7:00 AM), generates a comprehensive daily briefing: greeting, schedule overview, overdue items, top 3 priority actions, email highlights. Stored in `briefings` table.

**What it does NOT do:**
- Does NOT access WhatsApp messages (API limitation)
- Does NOT include weather, news, or stock data in v1.0

**Technical Requirements:**
- node-cron fires at `users.wake_time` preference
- Parallel fetch: Google Calendar + Supabase tasks + Gmail important/unread
- Claude structured briefing prompt with role + data injection
- BullMQ async job; results cached for instant delivery

**Dependencies:** F027, F036, F038, F060, F068, F069; Gmail API read-only

---

#### F068 — Briefing TTS Playback

| Field | Detail |
|-------|--------|
| **Feature ID** | F068 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Briefing text pre-generated as MP3 via ElevenLabs (not streaming — pre-built for instant playback). Auto-plays on briefing screen open. Wake word during playback pauses audio and activates voice command.

**Technical Requirements:**
- ElevenLabs TTS full briefing → MP3 in Supabase Storage (24h expiry)
- `expo-av` audio player
- Porcupine detection → immediate audio pause

**Dependencies:** F067 (briefing content), F003 (TTS), F001 (wake word interrupt)

---

#### F069 — Briefing Push Notification

| Field | Detail |
|-------|--------|
| **Feature ID** | F069 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Push notification when briefing is ready. Title: "🌅 Good morning — your briefing is ready". Body: first sentence of briefing. Deep-links to `/briefing/today`. Also used by F013, F043, F035.

**Technical Requirements:**
- `expo-notifications` / FCM / APNs
- Server-side push trigger via Supabase Edge Function or API
- Deep link routing via React Navigation

**Dependencies:** F067 (briefing ready event); used by F013, F035, F043

---

#### F070 — Briefing → Live Conversation

| Field | Detail |
|-------|--------|
| **Feature ID** | F070 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
At any point during briefing playback/reading, user can interrupt with wake word or text. Alex pauses briefing and handles request using briefing as context. Offers to resume after.

**Technical Requirements:**
- Wake word detection → audio pause → mic activate
- Briefing content injected into Redis session context as Layer 3
- State machine: `BRIEFING_PLAYING → COMMAND_ACTIVE → BRIEFING_RESUME_OFFERED`

**Dependencies:** F067, F068, F001, F006

---

#### F071 — Configurable Briefing Time

| Field | Detail |
|-------|--------|
| **Feature ID** | F071 |
| **Priority** | P2 — Phase v1.0 — Complexity: Low |

**Description:**
User sets preferred briefing time via voice ("Change my briefing to 6:30 AM") or Settings time picker. Cron schedule updates dynamically. Timezone-aware.

**Technical Requirements:**
- `wake_time` field in users table
- Dynamic cron re-scheduling on preference update
- UTC offset stored; local time computed for cron

**Dependencies:** F060 (preferences), F067 (briefing generation)

---

### 3.10 Automation Features

---

#### F073 — Multi-step Automation Engine

| Field | Detail |
|-------|--------|
| **Feature ID** | F073 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
Executes multi-step plans from Claude (F051). Handles sequential and parallel execution, dependency graphs, parameter passing, real-time progress updates, and completion notification. Max 8 steps per plan.

**What it does:**
- Topological sort of steps by dependency graph (Kahn's algorithm)
- Parallel execution of independent steps via `Promise.allSettled`
- Parameter references resolved at runtime (F074)
- Real-time progress updates via Supabase Realtime (F076)
- Completion or partial failure notification (F077)

**What it does NOT do:**
- Does NOT support conditional branches in v1.0 (no if/else logic)
- Does NOT support loops or iterations
- Does NOT execute > 8 steps in a single plan

**Technical Requirements:**
- BullMQ: one job per plan
- Step results: stored in `automation_plans.steps` JSONB field
- `Promise.allSettled` for parallel independent steps
- Max tool call depth per step: 3

**Dependencies:** F051 (plan creation), F074, F075, F076, F077, F078; all tool implementations

---

#### F074 — Step Dependency Resolution

| Field | Detail |
|-------|--------|
| **Feature ID** | F074 |
| **Priority** | P1 — Phase v1.0 — Complexity: High |

**Description:**
Resolves `$step{N}.result` parameter placeholders at runtime, injecting prior step outputs as inputs to dependent steps. Blocks dependent steps until prerequisites complete.

**Example:**
```
Step 1 result: { file_url: "drive.google.com/abc" }
Step 2 params: { attach: "$step1.result.file_url" }
  → resolved: { attach: "drive.google.com/abc" }
```

**Technical Requirements:**
- Regex param resolver: `\$step(\d+)\.result(\.[\w.]+)?`
- In-memory step result registry during plan execution

**Dependencies:** F073 (automation engine)

---

#### F075 — Automation Error Handling

| Field | Detail |
|-------|--------|
| **Feature ID** | F075 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Step fails → retry up to 3 times (exponential backoff: 1s, 3s, 9s). After 3 failures: mark step failed, continue independent steps, notify user of partial completion with [Retry] and [Skip] options.

**Technical Requirements:**
- BullMQ: `attempts: 3, backoff: { type: 'exponential', delay: 1000 }`
- `automation_plans.status = 'partial'` on failure
- Push notification: "X of Y steps completed. [Failed step] didn't work."

**Dependencies:** F073 (engine), F069 (notification)

---

#### F076 — Automation Progress Tracker (UI)

| Field | Detail |
|-------|--------|
| **Feature ID** | F076 |
| **Priority** | P1 — Phase v1.0 — Complexity: Medium |

**Description:**
Inline progress card in chat during multi-step execution. Each step row shows status badge in real time: ⏳ Pending → 🔄 Running → ✅ Done / ❌ Failed. Collapses to summary card on completion.

**Technical Requirements:**
- Supabase Realtime: subscribe to `automation_plans` row changes
- Animated status badges (React Native)

**Dependencies:** F073 (engine), F074 (step results); Supabase Realtime

---

#### F077 — Completion Notification

| Field | Detail |
|-------|--------|
| **Feature ID** | F077 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
On plan completion (full or partial), Alex notifies user via TTS (if active) or push notification (if background). Summary card persists in chat history.

**Technical Requirements:**
- Completion event handler in automation engine
- TTS if user in active voice session; push notification otherwise

**Dependencies:** F073, F003 (TTS), F069 (push)

---

#### F078 — Pre-execution Plan Preview

| Field | Detail |
|-------|--------|
| **Feature ID** | F078 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Before executing any plan containing external sends (email, WhatsApp, calendar invites), Alex presents the numbered plan for user review. Options: [Do all of this] [Edit plan] [Cancel].

**Technical Requirements:**
- Pre-execution scan: check plan for tools with external impact
- Plan preview modal (React Native)
- [Do all] triggers F073

**Dependencies:** F051 (plan), F073 (execution)

---

#### F079 — Retry Failed Steps

| Field | Detail |
|-------|--------|
| **Feature ID** | F079 |
| **Priority** | P1 — Phase v1.0 — Complexity: Low |

**Description:**
Retry a specific failed step without re-running completed steps. Available via [Retry] button on failed step row or voice command. Uses stored original params and prior step results.

**Technical Requirements:**
- `POST /v1/automation/:plan_id/retry/:step_id`
- Loads params from `automation_plans.steps` JSONB
- Re-injects prior step results for dependency resolution

**Dependencies:** F073, F075, F076

---

## 4.0 Feature Dependencies Map

```
FOUNDATION LAYER
────────────────────────────────────────────────────────────────
F050 Intent ◄── F006 Conversation ◄── F059 Short-term Memory
      │                                        │
      └──────────────────────────────────► F060 Long-term Memory

VOICE PIPELINE
────────────────────────────────────────────────────────────────
F001 Wake Word ──► F002 STT ──► F050 Intent ──► F053 Tool Router
  │  (interrupt)                                       │
  └──────────────────────────────────────────────► F003 TTS ◄─ final response

CONVERSATION RELIABILITY
────────────────────────────────────────────────────────────────
F007 Transcript Display ◄── F002
F008 Noise Retry ──► F002 (retry) / F004 (text fallback)
F005 Mode Switch ──► F002 + F003 + F004

FILE PIPELINE
────────────────────────────────────────────────────────────────
F014 Parsing ──► F009 Indexing ──► F010 Semantic Search
                                         │
                    F011 Ranking ◄────────┘
                         │
            F012 Preview  F013 Re-index (standalone)

COMMUNICATION PIPELINE
────────────────────────────────────────────────────────────────
F024 Contact Resolution ──► F017 Email ──► F018 Draft Preview
                        │          └──► F019 File Attach ◄── F010
                        │          └──► F020 Tone ◄── F064
                        └──► F021 WhatsApp ──► F023 24h Window
                                         └──► F022 File Attach ◄── F010
F025 Message Log ◄── F017 + F021

CALENDAR PIPELINE
────────────────────────────────────────────────────────────────
F027 Availability ──► F031 Conflict ──► F028 Create Event ──► F033 Meet Link
                                    └──► F029 Reschedule
F030 Delete ◄── F028 (event context)

TASK PIPELINE
────────────────────────────────────────────────────────────────
F034 Create Task ──► F035 Reminder ──► F039 Snooze
               └──► F038 Overdue ──► F067 Briefing
F040 Contact-linked ──► F024
F036 View ◄── F034 + F038
F037 Complete ◄── F036

MEETING PIPELINE
────────────────────────────────────────────────────────────────
F042 Transcription ──► F048 Storage
                  └──► F043 Summary ──► F044 Action Items ──► F034
                                   └──► F045 Share ──► F017
F046 Pre-meeting Files ◄── F010 + F027
F047 Follow-up Prompt ◄── F027 + F043
F056 Pre-meeting Context ◄── F046 + F036 + F025

MEMORY PIPELINE
────────────────────────────────────────────────────────────────
F063 Interaction Tracking ──► F054 Channel Selection
                          └──► F055 Follow-up Suggestions
F060 Memory ──► F067 Briefing + F006 Context
F065 Nightly Consolidation ──► F061 Episodic Memory ──► F060
F062 Correction ──► F060 (updates)
F064 Tone per Contact ──► F020 (email drafting)

BRIEFING PIPELINE
────────────────────────────────────────────────────────────────
F067 Generation ──► F068 TTS ──► F070 Live Conversation
              └──► F069 Push Notification
F071 Config ──► F067 (schedule)

AUTOMATION PIPELINE
────────────────────────────────────────────────────────────────
F051 Multi-intent ──► F078 Plan Preview ──► F073 Engine
                                               │
                              ┌────────────────┼─────────────────┐
                              │                │                 │
                           F074 Deps       F075 Errors       F076 UI
                                               │
                                           F079 Retry
                              └─────────────── F077 Notify
```

---

## 5.0 Phase Release Plan

### 5.1 v1.0 — Launch (All P1 + feasible P2 features)

**Total: 60 features**

| Category | Feature IDs |
|----------|------------|
| Voice & Conversation | F001, F002, F003, F004, F005, F006, F007, F008 |
| File Management | F009, F010, F011, F012, F013, F014 |
| Communication | F017, F018, F019, F020, F021, F022, F023, F024, F025 |
| Calendar & Scheduling | F027, F028, F029, F030, F031, F033 |
| Tasks & Reminders | F034, F035, F036, F037, F038, F039, F040 |
| Meeting | F042, F043, F044, F045, F046, F047, F048 |
| Intelligence & Decision | F050, F051, F052, F053, F054, F055, F056 |
| Memory & Personalization | F059, F060, F061, F062, F063, F064, F065 |
| Briefing & Summary | F067, F068, F069, F070, F071 |
| Automation | F073, F074, F075, F076, F077, F078, F079 |

---

### 5.2 v1.5 — Post-launch (~3 months)

| ID | Feature | Why Deferred |
|----|---------|-------------|
| F015 | Local File Search | OS-level file access; complex permissions on iOS/Android |
| F016 | Dropbox / OneDrive Indexing | Additional OAuth + parser work; Drive covers majority |
| F026 | Read / Summarise Emails | Significant UX scope; Gmail read adds complexity |
| F032 | Multi-attendee Scheduling | Cross-calendar free/busy requires external CalDAV |
| F041 | Recurring Tasks | Complex recurrence rule edge cases |
| F057 | Calendar Overload Detection | Intelligence enhancement; not core functionality |
| F072 | Briefing History View | Convenience; no new capability |

---

### 5.3 v2.0 — Future (~6+ months)

| ID | Feature | Why Deferred |
|----|---------|-------------|
| F049 | Speaker Identification | Requires diarization ML pipeline; significant compute |
| F058 | Emotion-aware Responses | Specialized audio ML model; GOAL.md lists as advanced |
| F066 | Behavioral Learning Engine | Requires data accumulation; v1.0 uses static preference rules |
| F080 | Saved Automation Templates | Useful at scale; single-user v1.0 doesn't require it |

---

## 6.0 Open Questions

| # | Question | Affected Features | Priority |
|---|----------|-----------------|----------|
| OQ-FL-1 | Should F018 (Draft Preview) be shown for ALL emails in v1.0 until trust is established, then auto-disabled after N sends? Or enable auto-send from day 1 for any "known" contact? | F017, F018 | High |
| OQ-FL-2 | Should F042 (Meeting Transcription) use a visually distinct, separate mode in the UI to prevent confusion with voice command mode? Or is contextual switching sufficient? | F042, F002, F007 | High |
| OQ-FL-3 | Should F055 (Proactive Suggestions) be ON by default or opt-in? Proactive messages drive engagement but risk feeling intrusive to new users. | F055, F056, F047 | Medium |
| OQ-FL-4 | In F073 (Automation Engine), if a step requires information Alex doesn't have (e.g., contact not in system), should Alex pause and ask mid-execution, or fail the step immediately with explanation? | F073, F075, F052 | Medium |
| OQ-FL-5 | For F009 (File Indexing), should "Shared with me" files in Google Drive be indexed by default or require explicit opt-in? Privacy implications differ significantly. | F009, F010 | Medium |

---

## 7.0 Next Steps

| # | Action | Owner | Dependency |
|---|--------|-------|-----------|
| NS-1 | Resolve OQ-FL-1 and OQ-FL-2 before building F017 and F042 | Product | Immediately |
| NS-2 | Use F-IDs to create engineering sprint breakdown (group by pipeline, assign complexity-based story points) | Engineering Lead | After sign-off |
| NS-3 | QA creates one test case per feature using: PRD acceptance criteria + USER_FLOW happy/error paths | QA | After sign-off |
| NS-4 | Confirm all F-IDs map correctly to API endpoints in SYSTEM_DESIGN.md § 6 | Engineering | Before Sprint 1 |
| NS-5 | Review §5.2 and §5.3 deferred list — confirm no P1 features were accidentally deferred | Product | Before Sprint 1 |
| NS-6 | Begin **Tech Stack Requirements Document** (Document 5) — confirm all libraries, services, and versions aligned with this feature list | Engineering Lead | After FEATURE_LIST sign-off |

---

*This document defines the complete scope of Alex from v1.0 through v2.0. All 80 features are catalogued with IDs, priorities, phases, dependencies, and technical requirements. Any new feature request must receive an F-ID here before being added to any sprint.*

---
**Document Control**

| Field | Value |
|-------|-------|
| Document Name | FEATURE_LIST.md |
| Version | v1.0 |
| Status | Draft |
| Created | 24 March 2026 |
| Total Features | 80 (F001–F080) |
| v1.0 Features | 60 |
| Deferred (v1.5 + v2.0) | 20 |
| References | GOAL.md, PRD.md v1.0, SYSTEM_DESIGN.md v1.0, USER_FLOW.md v1.0 |
