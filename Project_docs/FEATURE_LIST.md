# Feature List Document
## Alex — Personal AI Operating System
**Version:** v1.0
**Date:** 24 March 2026
**Status:** Draft
**Author:** Alex Build Team
**References:** PRD.md v1.0, SYSTEM_DESIGN.md v1.0, TECH_STACK.md v1.0, USER_FLOW.md v1.0, GOAL.md

---

## Table of Contents

1.0 Purpose & Scope
2.0 Feature Overview Table
3.0 Detailed Feature Breakdown
  - 3.1 Voice & Conversation Features
  - 3.2 File Management Features
  - 3.3 Communication Features
  - 3.4 Calendar & Scheduling Features
  - 3.5 Task & Reminder Features
  - 3.6 Meeting Features
  - 3.7 Intelligence & Decision Features
  - 3.8 Memory & Personalization Features
  - 3.9 Briefing & Summary Features
  - 3.10 Automation Features
4.0 Feature Dependencies Map
5.0 Phase Release Plan
6.0 Open Questions
7.0 Next Steps

---

## 1.0 Purpose & Scope

### 1.1 Purpose

This Feature List Document is the authoritative enumeration of every capability planned for Alex across all release phases. It translates the high-level goals in PRD.md and the interaction patterns in USER_FLOW.md into individually specified, acceptance-tested features — each with a unique identifier, a clear description of what it does and explicitly does not do, its technical dependencies, priority, and target release phase.

This document serves three audiences. For engineers, it defines the precise scope of each feature so implementation boundaries are unambiguous. For QA, the acceptance criteria in each feature entry are the direct basis for test cases. For product stakeholders, the phase release plan and dependency map provide a clear picture of build sequencing and the risks that arise if any feature slips.

### 1.2 Scope

This document covers all features across three release phases: v1.0 (must-have, launch-blocking), v1.5 (should-have, shipped within 90 days of v1.0), and v2.0 (planned enhancements, 6–12 months post-launch). Features explicitly excluded from the product in PRD.md §8.0 are not listed here.

### 1.3 Priority Definitions

| Priority | Definition |
|----------|-----------|
| P1 | Launch-blocking. Alex is not shippable without this feature. |
| P2 | High value. Shipping without it degrades the user experience significantly. |
| P3 | Meaningful enhancement. Absence does not block use of the product. |

### 1.4 Complexity Definitions

| Complexity | Definition |
|-----------|-----------|
| Low | Single component, well-understood implementation, < 1 week of engineering effort. |
| Medium | Two to three components, some integration work, 1–3 weeks of effort. |
| High | Multiple systems, non-trivial integration or AI prompt work, 3+ weeks of effort. |

---

## 2.0 Feature Overview Table

| Feature ID | Feature Name | Category | Priority | Complexity | Phase | Status |
|-----------|-------------|----------|----------|-----------|-------|--------|
| F001 | Wake Word Detection | Voice | P1 | Medium | v1.0 | Planned |
| F002 | Speech-to-Text Transcription | Voice | P1 | Medium | v1.0 | Planned |
| F003 | Text-to-Speech Response | Voice | P1 | Medium | v1.0 | Planned |
| F004 | Text Chat Interface | Voice | P1 | Low | v1.0 | Planned |
| F005 | Voice / Text Mode Switching | Voice | P1 | Low | v1.0 | Planned |
| F006 | Multi-Turn Conversation Context | Voice | P2 | Medium | v1.0 | Planned |
| F007 | Voice Emotion Awareness | Voice | P3 | High | v2.0 | Planned |
| F008 | Multilingual Voice Support | Voice | P3 | High | v2.0 | Planned |
| F009 | File Directory Indexing | File | P1 | Medium | v1.0 | Planned |
| F010 | Keyword File Search | File | P1 | Low | v1.0 | Planned |
| F011 | Semantic File Search | File | P1 | Medium | v1.0 | Planned |
| F012 | Real-Time File Watcher | File | P1 | Low | v1.0 | Planned |
| F013 | File Disambiguation | File | P1 | Low | v1.0 | Planned |
| F014 | File Preview in Dashboard | File | P2 | Low | v1.0 | Planned |
| F015 | Cloud File Storage Support | File | P3 | High | v2.0 | Planned |
| F016 | Email Compose & Send | Communication | P1 | Medium | v1.0 | Planned |
| F017 | Email Tone Adjustment | Communication | P2 | Low | v1.0 | Planned |
| F018 | Email with File Attachment | Communication | P1 | Medium | v1.0 | Planned |
| F019 | Email Inbox Reading | Communication | P2 | Medium | v1.0 | Planned |
| F020 | Smart Email Follow-Up Suggestion | Communication | P2 | Medium | v1.5 | Planned |
| F021 | WhatsApp Message Send | Communication | P1 | Medium | v1.0 | Planned |
| F022 | WhatsApp File Send | Communication | P1 | Medium | v1.0 | Planned |
| F023 | Contact Resolution (Fuzzy Match) | Communication | P1 | Medium | v1.0 | Planned |
| F024 | Contact Management | Communication | P2 | Low | v1.0 | Planned |
| F025 | Multi-Channel Communication History | Communication | P3 | Medium | v1.5 | Planned |
| F026 | Calendar Event Reading | Calendar | P1 | Medium | v1.0 | Planned |
| F027 | Calendar Event Creation | Calendar | P1 | Medium | v1.0 | Planned |
| F028 | Availability Check | Calendar | P1 | Medium | v1.0 | Planned |
| F029 | Smart Time Slot Suggestion | Calendar | P2 | Medium | v1.0 | Planned |
| F030 | Calendar Invite Dispatch | Calendar | P2 | Low | v1.0 | Planned |
| F031 | Multi-Provider Calendar Support | Calendar | P3 | High | v2.0 | Planned |
| F032 | Task Creation | Tasks | P1 | Low | v1.0 | Planned |
| F033 | Task Status Management | Tasks | P1 | Low | v1.0 | Planned |
| F034 | Task Prioritisation | Tasks | P2 | Low | v1.0 | Planned |
| F035 | Reminder Creation | Tasks | P1 | Low | v1.0 | Planned |
| F036 | Reminder Delivery | Tasks | P1 | Medium | v1.0 | Planned |
| F037 | Overdue Task Escalation | Tasks | P2 | Low | v1.0 | Planned |
| F038 | Recurring Reminder Support | Tasks | P2 | Low | v1.0 | Planned |
| F039 | Task–Calendar Correlation | Tasks | P2 | Medium | v1.5 | Planned |
| F040 | Meeting Audio Capture | Meeting | P2 | Medium | v1.0 | Planned |
| F041 | Real-Time Meeting Transcription | Meeting | P2 | High | v1.0 | Planned |
| F042 | Meeting Summary Generation | Meeting | P2 | High | v1.0 | Planned |
| F043 | Action Item Extraction | Meeting | P2 | High | v1.0 | Planned |
| F044 | Action Item to Task Conversion | Meeting | P2 | Low | v1.0 | Planned |
| F045 | Meeting History & Search | Meeting | P3 | Medium | v1.5 | Planned |
| F046 | Video Call Bot Integration | Meeting | P3 | High | v2.0 | Planned |
| F047 | Intent Parsing | Intelligence | P1 | High | v1.0 | Planned |
| F048 | AI Model Router (Free/Paid) | Intelligence | P1 | High | v1.0 | Planned |
| F049 | Multi-Intent Command Handling | Intelligence | P1 | High | v1.0 | Planned |
| F050 | Ambiguity Detection & Clarification | Intelligence | P1 | Medium | v1.0 | Planned |
| F051 | Smart Suggestions Engine | Intelligence | P2 | High | v1.5 | Planned |
| F052 | Proactive Follow-Up Nudges | Intelligence | P2 | Medium | v1.5 | Planned |
| F053 | Vision / Image Understanding | Intelligence | P3 | High | v2.0 | Planned |
| F054 | Session Memory (Short-Term) | Memory | P1 | Medium | v1.0 | Planned |
| F055 | Long-Term Semantic Memory | Memory | P1 | High | v1.0 | Planned |
| F056 | User Preference Learning | Memory | P2 | Medium | v1.0 | Planned |
| F057 | Preference Review & Correction | Memory | P2 | Low | v1.0 | Planned |
| F058 | Contact Frequency Ranking | Memory | P2 | Low | v1.0 | Planned |
| F059 | Behavioural Adaptation Engine | Memory | P3 | High | v2.0 | Planned |
| F060 | Morning Briefing Generation | Briefing | P2 | High | v1.0 | Planned |
| F061 | Briefing Scheduling | Briefing | P2 | Low | v1.0 | Planned |
| F062 | Voice Briefing Delivery | Briefing | P2 | Low | v1.0 | Planned |
| F063 | Priority Inbox Summary in Briefing | Briefing | P2 | Medium | v1.0 | Planned |
| F064 | Project Status in Briefing | Briefing | P3 | High | v1.5 | Planned |
| F065 | Multi-Step Task Execution | Automation | P1 | High | v1.0 | Planned |
| F066 | Execution Plan Preview | Automation | P1 | Medium | v1.0 | Planned |
| F067 | Step Dependency Resolution | Automation | P1 | Medium | v1.0 | Planned |
| F068 | Partial Failure Recovery | Automation | P1 | Medium | v1.0 | Planned |
| F069 | n8n Workflow Integration | Automation | P2 | Medium | v1.0 | Planned |
| F070 | Autonomous Agent Mode | Automation | P3 | High | v2.0 | Planned |

---

## 3.0 Detailed Feature Breakdown

---

### 3.1 Voice & Conversation Features

---

#### F001 — Wake Word Detection

**Description:** Alex listens passively for the wake phrase "Hey Alex" using Porcupine (Picovoice), an offline, low-CPU wake word engine. When the wake phrase is detected, the STT listener activates and the dashboard displays a listening indicator. Wake word detection runs on a dedicated background thread and does not require internet connectivity. Detection operates continuously while the Alex dashboard tab is open in the browser, or while the local agent is running. This feature does not include custom wake phrase configuration in v1.0 — "Hey Alex" is the only supported phrase. Custom phrases are targeted for v1.5.

**User Benefit:** Enables hands-free, zero-friction activation. The user never needs to click, tap, or navigate to the dashboard to begin a command.

**Acceptance Criteria:**
- Wake word fires correctly in ≥ 95% of clean-audio attempts at a 1-metre speaking distance.
- False positive rate is < 1 per hour of ambient audio.
- Wake word detection consumes < 5% of a single CPU core continuously.
- Activating the wake word transitions the dashboard to "Listening" state within 300 ms.
- Deactivating voice in Settings stops wake word detection immediately.

**Technical Requirements:** Porcupine SDK (Python); browser microphone permission; background thread management in FastAPI process; WebSocket event pushed to dashboard on detection.

**Does Not Include:** Custom wake phrase training, multi-wake-word support, noise cancellation, speaker identification.

**Dependencies:** F002 (activated by wake word), F004 (fallback if voice unavailable)

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F002 — Speech-to-Text Transcription

**Description:** Converts captured microphone audio into plain text for processing by the Intent Parser. In free mode, `faster-whisper` (CTranslate2 Whisper implementation) runs locally using the `small` model, achieving near-real-time CPU transcription. In paid mode, audio is sent to the OpenAI Whisper API for sub-second transcription. Each transcription result carries a confidence score. Scores below 0.6 trigger a re-listen prompt. A maximum of two automatic retries are attempted before the system offers a text fallback. This feature handles command-length audio (1–30 seconds). Long-form meeting transcription is a separate feature (F041).

**User Benefit:** Allows users to interact with Alex entirely by voice without typing, reducing friction for mobile or hands-busy scenarios.

**Acceptance Criteria:**
- Transcription accuracy ≥ 90% for clear English speech with no background noise.
- Transcription of a 5-second command completes within 3 seconds in free mode and within 1 second in paid mode.
- Low-confidence transcriptions (< 0.6) surface a re-listen prompt rather than silently misinterpreting input.
- Free and paid STT paths produce identically formatted output to the Intent Parser.

**Technical Requirements:** `faster-whisper` Python library; OpenAI Whisper API (paid path); microphone access via browser; confidence score extraction; WebSocket event to update dashboard state.

**Does Not Include:** Speaker diarisation, real-time word-by-word display, non-English languages, noise suppression.

**Dependencies:** F001 (wake word triggers STT) or F004 (text input as fallback); F047 (transcription output passed to Intent Parser)

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F003 — Text-to-Speech Response

**Description:** Converts Alex's text responses into spoken audio played through the user's device speakers. In free mode, Coqui TTS with the VITS model (`tts_models/en/ljspeech/vits`) synthesises speech locally with approximately one second of latency per sentence. In paid mode, the ElevenLabs API provides near-human voice quality at under 300 ms latency. Both paths produce WAV audio streamed to the browser. TTS is used for all confirmations, question prompts, action results, briefings, and reminder alerts. Users can mute TTS output at any time without disabling voice input.

**User Benefit:** Allows Alex to communicate results hands-free, completing the voice interaction loop without requiring the user to look at the dashboard.

**Acceptance Criteria:**
- TTS begins playing within 1.5 seconds of a response being ready in free mode.
- TTS output is intelligible and clearly articulated for all standard English sentences.
- Muting TTS in Settings takes effect within one request cycle.
- Free and paid TTS paths are switchable without restarting the application.

**Technical Requirements:** Coqui TTS Python library; ElevenLabs API (paid path); WAV audio streaming to browser; mute toggle stored in preferences table.

**Does Not Include:** Custom voice cloning (v1.5), multilingual TTS, voice style or emotion adjustment.

**Dependencies:** F048 (AI Model Router generates text that is passed to TTS)

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F004 — Text Chat Interface

**Description:** A chat-style input field in the dashboard allows the user to type commands and questions as an alternative to voice. Submitted text follows the same processing pipeline as transcribed voice input — it is passed directly to the Intent Parser. The chat interface displays the conversation history for the current session, showing user messages on the right and Alex's responses on the left. Each response includes the timestamp and a small indicator showing which AI model processed it (free/paid). The interface does not scroll infinitely; the last 50 turns are displayed in the active session view, with older history accessible via the Memory panel.

**User Benefit:** Provides a reliable fallback for noisy environments, users who prefer typing, and situations where microphone access is unavailable.

**Acceptance Criteria:**
- Text input reaches the Intent Parser within 200 ms of submission.
- Chat history for the active session renders correctly on dashboard load.
- Input field supports multi-line text (Shift+Enter for newline; Enter to submit).
- AI mode indicator is visible per message.

**Technical Requirements:** Next.js chat component; TanStack Query for message history fetching; WebSocket subscription for streaming responses; `POST /api/v1/command` with `source: "text"`.

**Does Not Include:** Rich text formatting in input, file drag-and-drop into chat (v1.5), message editing after submission.

**Dependencies:** F047 (text passed to Intent Parser); F048 (AI Model Router)

**Priority:** P1 | **Complexity:** Low | **Phase:** v1.0

---

#### F005 — Voice / Text Mode Switching

**Description:** The user can switch between voice and text input modes at any time without losing session context. Switching is available via a toggle in the dashboard header and via the spoken command "Switch to text" or "Switch to voice". When switching from voice to text mid-conversation, the current session context — last 5 turns, any unresolved entities — is preserved and available to the next text command. When switching from text to voice, wake word detection activates immediately.

**User Benefit:** Ensures Alex is usable in any environment without the user losing their place in a multi-turn interaction.

**Acceptance Criteria:**
- Mode switch completes within one UI render cycle (< 100 ms).
- Session context is retained across the switch with no loss of conversation history.
- Voice mode deactivates microphone capture when switched to text.

**Technical Requirements:** Zustand store for input mode state; WebSocket session context; Porcupine thread management.

**Does Not Include:** Automatic mode detection based on ambient noise level (v2.0).

**Dependencies:** F001, F002, F004, F054 (session memory preserves context)

**Priority:** P1 | **Complexity:** Low | **Phase:** v1.0

---

#### F006 — Multi-Turn Conversation Context

**Description:** Alex retains the context of the last five conversational turns within an active session and uses that context when parsing new commands. This allows follow-up commands like "Now send it to Rohan instead" to correctly reference the file or action from the preceding turn without the user restating it. Context is stored in Redis for the active session (TTL: 30 minutes of inactivity) and in pgvector for long-term semantic recall across sessions. Context window management ensures the AI model is never sent more tokens than its context limit allows.

**User Benefit:** Enables natural, flowing conversation rather than requiring fully self-contained commands for every interaction.

**Acceptance Criteria:**
- Follow-up commands that reference a prior turn resolve correctly in ≥ 90% of tested cases.
- Context resets cleanly when the user says "Start over" or "New task."
- Session context does not persist after 30 minutes of inactivity.
- Long sessions with 20+ turns do not cause AI model context overflow errors.

**Technical Requirements:** Redis session store (TTL 30 min); pgvector long-term memory; context truncation logic in Intent Parser; session ID management in `POST /api/v1/command`.

**Does Not Include:** Cross-device session continuity, shared context between multiple users.

**Dependencies:** F047 (Intent Parser consumes context), F054, F055

**Priority:** P2 | **Complexity:** Medium | **Phase:** v1.0

---

#### F007 — Voice Emotion Awareness

**Description:** Detects emotional cues in the user's voice (urgency, frustration, distress) and adjusts Alex's response tone accordingly. Urgent commands receive faster processing priority in the task queue. Detected frustration triggers a softer, more patient response tone.

**Does Not Include in this phase:** Anything listed under v1.0 or v1.5 — this feature requires emotion detection model integration not planned until v2.0.

**Priority:** P3 | **Complexity:** High | **Phase:** v2.0

---

#### F008 — Multilingual Voice Support

**Description:** Extends STT, TTS, and intent parsing to languages beyond English. Initial target languages: Hindi, Spanish, French. Requires multilingual Whisper model, language-specific TTS voices, and language-aware prompt templates in the AI Instructions Document.

**Priority:** P3 | **Complexity:** High | **Phase:** v2.0

---

### 3.2 File Management Features

---

#### F009 — File Directory Indexing

**Description:** Indexes all files within user-configured watched directories into PostgreSQL (file metadata) and pgvector (semantic content embeddings). At initial setup, a full index is built as a Celery background job. The index stores file name, path, extension, size, SHA-256 content hash, and a 384-dimensional embedding of the first 512 tokens of extractable text content. Apache Tika handles text extraction from PDF, DOCX, XLSX, PPTX, and plain text files. Binary files without extractable text (images, executables) are indexed by metadata only. The user can configure which directories to watch in Settings. A maximum of ten watched directories are supported in v1.0.

**User Benefit:** Makes every document in the user's watched folders discoverable by name, content, or natural-language description without manual tagging.

**Acceptance Criteria:**
- Initial index of 10,000 files completes within 15 minutes on a mid-range machine.
- Each file's metadata and embedding are stored atomically — no partial records.
- Files without extractable text are indexed by metadata only without error.
- Index progress is visible in the dashboard during initial build.
- SHA-256 hash is used to detect changed files and trigger re-indexing of modified content only.

**Technical Requirements:** Celery background job; Apache Tika Python wrapper; `sentence-transformers` (all-MiniLM-L6-v2); PostgreSQL `file_index` table; pgvector `content_embedding` column; `watchdog` library for directory monitoring.

**Does Not Include:** Cloud storage indexing (Google Drive, Dropbox), email attachment indexing, indexing files on network drives.

**Dependencies:** F012 (Watchdog triggers incremental updates), F010, F011

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F010 — Keyword File Search

**Description:** Executes fast, case-insensitive keyword search over indexed file metadata using PostgreSQL full-text search (replacing Whoosh from SYSTEM_DESIGN.md). Supports partial matches, wildcard queries, and Boolean operators (AND, OR, NOT). Returns results ranked by text similarity score. Used as the first stage of the hybrid search pipeline before semantic re-ranking.

**User Benefit:** Provides instant, deterministic retrieval for users who know part of the filename, extension, or approximate date.

**Acceptance Criteria:**
- Keyword search across 10,000 indexed files returns results within 500 ms.
- Case-insensitive matching works for all standard ASCII filenames.
- Partial matches (e.g., "Q1 rep" matching "Q1_Report_2026.pdf") return correct results.
- Search correctly applies date filters when temporal entities are extracted from the query.

**Technical Requirements:** PostgreSQL full-text search (`tsvector`, `tsquery`); GIN index on `file_index.name`; `GET /api/v1/files/search?mode=keyword`.

**Does Not Include:** Content-level keyword search within document body (that is handled by F011).

**Dependencies:** F009 (index must exist)

**Priority:** P1 | **Complexity:** Low | **Phase:** v1.0

---

#### F011 — Semantic File Search

**Description:** Embeds the user's search query using all-MiniLM-L6-v2 and performs cosine similarity search against file content embeddings stored in pgvector. Returns the top five semantically similar files regardless of filename. Used as the second stage of the hybrid search pipeline to re-rank candidates returned by F010 or to operate independently for descriptive queries where keywords are unhelpful. Auto-selects the top result if its similarity score is ≥ 0.85. Presents the top three candidates to the user for manual selection if all scores are below 0.85.

**User Benefit:** Allows the user to find files by describing their content rather than remembering their name — for example, "the contract I signed with ACME last quarter."

**Acceptance Criteria:**
- Semantic search of 10,000 indexed files returns results within 2 seconds.
- Similarity threshold of 0.85 auto-selects the correct file in ≥ 95% of unambiguous cases.
- Multi-result disambiguation presents results with human-readable descriptions (name, date, size).
- Semantic search degrades gracefully when embeddings are not available (metadata-only fallback).

**Technical Requirements:** `sentence-transformers` (all-MiniLM-L6-v2); pgvector cosine similarity operator (`<=>`); IVFFlat index on embedding column (created after 1,000 rows); `GET /api/v1/files/search?mode=semantic`.

**Does Not Include:** Indexing file images or charts within documents, cross-file semantic comparison.

**Dependencies:** F009 (embeddings must exist in index)

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F012 — Real-Time File Watcher

**Description:** Monitors all configured watched directories continuously using the `watchdog` Python library. On any file system event — creation, modification, deletion, or rename — triggers an incremental index update within two seconds. File creations and modifications queue a re-embedding job in Celery. Deletions remove the file's record from both the PostgreSQL file_index table and pgvector. Renames update the path field without re-embedding if content hash is unchanged.

**User Benefit:** Keeps the search index current automatically. The user never needs to manually trigger a re-index after saving, moving, or deleting files.

**Acceptance Criteria:**
- New files appear in search results within 5 seconds of creation in a watched directory.
- Deleted files are removed from search results within 5 seconds of deletion.
- Renamed files are findable by their new name within 5 seconds.
- The watcher survives directory unmounts and reconnects on remount without restart.

**Technical Requirements:** `watchdog` Python library; Celery task for incremental index update; SHA-256 change detection to avoid redundant re-embedding.

**Does Not Include:** Watching network file systems in v1.0 (local directories only), watching more than 10 directories simultaneously.

**Dependencies:** F009 (base index), F010, F011

**Priority:** P1 | **Complexity:** Low | **Phase:** v1.0

---

#### F013 — File Disambiguation

**Description:** When a file search returns multiple results with no clear top candidate (all scores below the 0.85 auto-select threshold), Alex presents the top three results to the user and requests a selection. In voice mode, Alex reads the top three options and waits for a numeric or descriptive selection. In text mode, the dashboard renders a clickable card list. If the user's selection narrows to one file, the flow continues. If the user's description still does not match, Alex offers to broaden or refine the search query.

**User Benefit:** Prevents Alex from acting on the wrong file when the user's description is ambiguous, which is especially important before attaching files to emails or WhatsApp messages.

**Acceptance Criteria:**
- Disambiguation prompt is triggered whenever top result similarity score is < 0.85 and multiple candidates exist.
- Voice disambiguation reads a maximum of three options clearly.
- User selection by number ("the first one") and by name ("the one from February") both resolve correctly.
- A user response of "none of these" returns to search without consuming the overall command timeout.

**Technical Requirements:** Intent Parser entity refinement; TTS output formatting for list reading; dashboard file card component; session context updated with confirmed file selection.

**Does Not Include:** Side-by-side file content preview in v1.0 (that is F014).

**Dependencies:** F010, F011, F002 (voice selection), F004 (text selection)

**Priority:** P1 | **Complexity:** Low | **Phase:** v1.0

---

#### F014 — File Preview in Dashboard

**Description:** Displays a file preview card in the dashboard when a file is found or selected. The card shows file name, path, type icon, size, last modified date, and — for documents with extractable text — the first 200 characters of content. For PDFs and DOCX files, a thumbnail is generated at index time and shown in the card. The user can open the file in its native application from the card.

**User Benefit:** Lets the user confirm the correct file has been found before approving an action, reducing errors in file-to-message delivery.

**Acceptance Criteria:**
- Preview card renders within 500 ms of file selection.
- Thumbnail renders for PDF and DOCX files only; other types show a file-type icon.
- "Open file" action opens the file in the OS default application.

**Technical Requirements:** Next.js file card component; thumbnail generation at index time via pdf2image (PDF) or docx2img; Supabase Storage for thumbnail caching.

**Does Not Include:** In-browser document editing, full document preview, preview of image files.

**Dependencies:** F009 (thumbnails generated at index time), F010, F011

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0

---

#### F015 — Cloud File Storage Support

**Description:** Extends file indexing and search to cloud storage providers: Google Drive, Dropbox, and OneDrive. Requires OAuth integration with each provider, a cloud-aware file watcher using provider webhooks, and content extraction via provider-native export APIs.

**Priority:** P3 | **Complexity:** High | **Phase:** v2.0

---

### 3.3 Communication Features

---

#### F016 — Email Compose & Send

**Description:** Composes and sends an email entirely from a natural-language command. Alex resolves the recipient via F023 (contact resolution), generates the subject line and body using the AI Model Router, and dispatches the email via Resend (transactional API) or the user's configured SMTP provider. A confirmation preview is always shown before sending (per USER_FLOW.md §5.1). The composed email reflects the user's tone preference stored in preferences (formal by default; overridable per command). Alex generates a contextually appropriate subject line if the user does not specify one. After sending, the sent message is logged to audit_logs.

**User Benefit:** Allows the user to delegate routine email composition and dispatch entirely to Alex, eliminating the need to open an email client for standard professional communications.

**Acceptance Criteria:**
- Email is composed and ready for confirmation within 5 seconds of command submission.
- Delivery confirmation is received and logged for every sent message.
- If Resend delivery fails, a single automatic retry occurs after 60 seconds.
- After two failed attempts, the composed email is saved as a draft and the user is notified.
- Confirmation preview renders correctly with To, Subject, and Body visible before send.

**Technical Requirements:** Resend Python SDK or `smtplib` SMTP fallback; `POST /api/v1/communication/email/send`; AI Model Router for composition; contacts table for recipient resolution; audit_logs write.

**Does Not Include:** Email threading (replying to existing threads), CC/BCC fields in v1.0, read receipts, email scheduling.

**Dependencies:** F023 (recipient resolution), F048 (AI composition), F016 (confirmation gate per USER_FLOW §5.1)

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F017 — Email Tone Adjustment

**Description:** Allows the user to specify the tone of a composed email — formal, casual, brief, or detailed — either as part of the original command ("Send a casual email to Priya") or during the confirmation review ("Make it more concise"). Tone preference set in a command overrides the default stored in preferences for that message only. Tone is passed as a parameter to the AI Model Router prompt template used in email composition.

**User Benefit:** Ensures every outgoing email matches the relationship and context without the user manually editing the draft.

**Acceptance Criteria:**
- Tone keywords (formal, casual, brief, detailed, friendly, professional) are correctly applied to generated email content.
- Tone override in a command takes effect for that message only without changing the stored default.
- Tone modification via the confirmation screen re-generates the body within 5 seconds.

**Technical Requirements:** Tone parameter in email composition prompt template (AI Instructions Document); preferences table `communication.email_tone` key.

**Does Not Include:** Custom tone profiles, tone detection from prior sent emails (v1.5).

**Dependencies:** F016, F048

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0

---

#### F018 — Email with File Attachment

**Description:** Resolves a referenced file via the File Search engine (F010/F011), encodes it as a MIME attachment, and includes it in the composed email. The file reference can be explicit ("attach the Q1 report") or implicit ("email Priya the contract"). When a file reference is detected in the email command, the File Search Flow (USER_FLOW §3.3) is executed as a prerequisite step before email composition. Multiple files can be attached in a single email if multiple references are detected.

**User Benefit:** Automates the most time-consuming part of file delivery — finding the file, then manually attaching it — into a single spoken command.

**Acceptance Criteria:**
- File is attached correctly as a MIME multipart attachment, retaining original filename and MIME type.
- Attachment appears in the email confirmation preview before send.
- Emails with attachments up to 10 MB are sent successfully.
- Emails with attachments exceeding 10 MB display a warning and suggest an alternative delivery method.

**Technical Requirements:** MIME multipart encoding in Python; File Search Flow integration; attachment size validation before send.

**Does Not Include:** Attaching email-hosted links rather than inline attachments (v1.5), compressing large attachments.

**Dependencies:** F009, F010, F011, F013, F016

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F019 — Email Inbox Reading

**Description:** Reads the user's email inbox via IMAP and surfaces selected messages in Alex's responses and briefings. Primary use cases are: (1) answering "Do I have any important emails?" and (2) pulling priority emails for the morning briefing (F063). IMAP credentials are stored encrypted in Supabase secrets. Alex reads only UNSEEN and FLAGGED messages from the last 24 hours for briefing purposes. Full inbox management (reply, archive, delete) is explicitly out of scope for v1.0.

**User Benefit:** Brings inbox awareness into Alex's context without requiring the user to leave the dashboard or switch to their email client.

**Acceptance Criteria:**
- IMAP connection is established and returns new messages within 10 seconds.
- Only UNSEEN and FLAGGED messages from the last 24 hours are surfaced for briefing.
- Email credentials survive application restart without requiring re-entry.
- IMAP connection failure is caught gracefully and does not block the briefing flow.

**Technical Requirements:** Python `imaplib` (stdlib); IMAP SSL on port 993; encrypted credential storage via Supabase secrets; `GET /api/v1/communication/email/inbox`.

**Does Not Include:** Email reply, archive, delete, inbox search by keyword, reading emails beyond last 24 hours for briefing.

**Dependencies:** Supabase secrets (credential storage), F060 (briefing consumes inbox data)

**Priority:** P2 | **Complexity:** Medium | **Phase:** v1.0

---

#### F020 — Smart Email Follow-Up Suggestion

**Description:** Proactively suggests a follow-up email when Alex detects that a meeting has ended, an action item was assigned, or an email was sent but no reply has been received within a configurable window (default: 24 hours for client communications, 48 hours for internal). Suggestions are surfaced in the briefing and as dashboard nudges, not as automatic sends.

**Priority:** P2 | **Complexity:** Medium | **Phase:** v1.5

---

#### F021 — WhatsApp Message Send

**Description:** Composes and sends a WhatsApp message to a resolved contact via the Twilio WhatsApp API (Sandbox for free mode; Business API for paid). Contact is resolved via F023. A confirmation preview is shown before every send. The message body is generated by the AI Model Router using a concise, conversational prompt template appropriate for messaging (distinct from the email template). Message delivery status is retrieved from Twilio's webhook and logged.

**User Benefit:** Lets the user send WhatsApp messages without picking up their phone, using the same voice command interface used for every other action.

**Acceptance Criteria:**
- WhatsApp message is sent and delivery confirmation received within 5 seconds in paid mode, 10 seconds in free mode.
- A delivered status indicator appears in the dashboard after send.
- Sending to a contact not in Twilio's opt-in list (Sandbox limitation) surfaces a clear error rather than a silent failure.

**Technical Requirements:** Twilio Python SDK; `POST /api/v1/communication/whatsapp/send`; Twilio delivery webhook handler; contacts.whatsapp_id field.

**Does Not Include:** WhatsApp group messaging, WhatsApp message reading/inbox, WhatsApp calls.

**Dependencies:** F023 (contact resolution), F048 (message composition)

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F022 — WhatsApp File Send

**Description:** Attaches and delivers a resolved file to a WhatsApp contact as a media message. Supported MIME types: PDF, DOCX, XLSX, PPTX, PNG, JPG (per Twilio's supported media types). Files are encoded as `multipart/form-data` and passed to Twilio's media messaging endpoint. Files are resolved via the File Search Flow before dispatch. File size is validated against Twilio's 16 MB media limit before attempting send.

**User Benefit:** Enables complete file-to-WhatsApp delivery in a single command, the most common file delivery workflow for the target user personas.

**Acceptance Criteria:**
- File arrives as a native media attachment (not a link) in the recipient's WhatsApp.
- Files above 16 MB trigger a clear user-facing error before any send attempt.
- Unsupported file types trigger a clear user-facing error before any send attempt.

**Technical Requirements:** Twilio media message API; file MIME type validation; file size check; `multipart/form-data` encoding.

**Does Not Include:** Sending multiple files in a single WhatsApp message (Twilio limitation).

**Dependencies:** F009, F010, F011, F013, F021

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F023 — Contact Resolution (Fuzzy Match)

**Description:** Resolves a natural-language contact reference — a first name, nickname, partial name, or company name — to a specific contact record in the PostgreSQL contacts table. Uses Levenshtein distance for fuzzy matching combined with interaction frequency ranking (contacts used more often are ranked higher when scores are equal). Resolution outcomes: single high-confidence match (≥ 0.9, auto-proceeds), multiple plausible matches (disambiguation prompt), or no match (user prompted for contact details). New contact details provided by the user are offered for saving.

**User Benefit:** The user never needs to specify full names, email addresses, or phone numbers in their commands — Alex learns who they mean from partial references.

**Acceptance Criteria:**
- Single unambiguous match resolves without prompting the user in ≥ 95% of tested references.
- Disambiguation prompt lists at most three candidates.
- No match triggers a graceful prompt for contact details rather than a failure state.
- Frequency ranking is updated after every successful contact use.

**Technical Requirements:** `fuzzywuzzy` or `rapidfuzz` Python library; `contacts` table with `aliases` (JSON array), `frequency` (integer); `GET /api/v1/contacts/resolve?q={query}`.

**Does Not Include:** Contact import from phone address book or Google Contacts in v1.0 (v1.5), duplicate contact detection.

**Dependencies:** contacts table (PostgreSQL)

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F024 — Contact Management

**Description:** Allows the user to add, update, and delete contacts manually through the dashboard or by voice. Supports setting display name, aliases, email, phone, and WhatsApp ID. Contacts added via voice ("Save Priya's number as +91-XXXXXXXXXX") are stored immediately without a confirmation step, since contact creation is a reversible, low-consequence action.

**Acceptance Criteria:**
- New contact created via dashboard persists on page refresh.
- New contact created via voice is findable in the next search within 2 seconds.
- Contact deletion removes all associated records from the contacts table.

**Technical Requirements:** CRUD endpoints: `POST`, `GET`, `PATCH`, `DELETE /api/v1/contacts/{id}`; dashboard Contacts panel component.

**Does Not Include:** Contact photo storage, contact syncing with Google or iPhone address books.

**Dependencies:** F023

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0

---

#### F025 — Multi-Channel Communication History

**Description:** Unified view in the dashboard showing a combined timeline of emails sent and WhatsApp messages dispatched by Alex, with delivery status, recipient, and timestamp. Searchable by contact name and date range.

**Priority:** P3 | **Complexity:** Medium | **Phase:** v1.5

---

### 3.4 Calendar & Scheduling Features

---

#### F026 — Calendar Event Reading

**Description:** Reads events from the user's connected Google Calendar for a specified time window. Cached locally in the `calendar_events` PostgreSQL table, refreshed every 5 minutes by a Celery Beat job. Used by the briefing, availability check, and smart scheduling features. Returns event title, start/end time, location, and attendee list. Supports natural-language time queries: "today," "this week," "next Tuesday."

**Acceptance Criteria:**
- Calendar events for today are available within 10 seconds of a query.
- Cache is no more than 5 minutes stale under normal operation.
- Events from the cached table are returned within 500 ms.
- Natural-language time queries ("next week," "tomorrow morning") resolve to correct date ranges.

**Technical Requirements:** Google Calendar API v3; OAuth 2.0 refresh token; Celery Beat 5-minute sync job; `calendar_events` table; `GET /api/v1/calendar/events?from={date}&to={date}`.

**Does Not Include:** Outlook, iCal, or Calendly integration in v1.0; reading attendees' calendars.

**Dependencies:** Google Calendar OAuth (onboarding F005), Celery Beat (F036)

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F027 — Calendar Event Creation

**Description:** Creates a new calendar event in the user's Google Calendar via the API `events.insert` method. Accepts title, date/time, duration, location, and attendee list. All event details are extracted from the user's natural-language command and confirmed before creation. Events are added to the local `calendar_events` cache immediately after creation without waiting for the next sync cycle.

**Acceptance Criteria:**
- Event appears in Google Calendar within 3 seconds of confirmation.
- Event is immediately visible in Alex's dashboard calendar view.
- Created events include all attendees specified in the command.
- Events with no specified duration default to 60 minutes.

**Technical Requirements:** Google Calendar API `events.insert`; `POST /api/v1/calendar/events`; immediate cache update post-creation.

**Does Not Include:** Recurring event creation in v1.0 (v1.5), event editing after creation via voice.

**Dependencies:** F026, F028 (availability check run before creation), F023 (attendee resolution)

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F028 — Availability Check

**Description:** Checks whether the user has a free time slot of the requested duration on a specified day and within a specified time window. Queries the local `calendar_events` cache, identifies gaps between existing events, and returns available slots ranked by preference (avoiding early morning and late evening unless the user has no other option). Returns the single best slot for a confirmed booking or a list of up to three slots for multi-participant scheduling suggestions.

**Acceptance Criteria:**
- Availability check across one day's events completes within 1 second.
- Returns no false-available slots (does not propose times already occupied by existing events).
- Respects user-configured working hours (default 9 AM – 6 PM) when suggesting slots.

**Technical Requirements:** Gap-detection algorithm against `calendar_events` table; working hours preference (`preferences.calendar.working_hours`); `GET /api/v1/calendar/availability?date={date}&duration={minutes}`.

**Does Not Include:** Cross-participant availability checking (requires access to attendees' calendars, not available in v1.0).

**Dependencies:** F026

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F029 — Smart Time Slot Suggestion

**Description:** When the user requests a meeting without specifying a time, Alex proactively suggests two or three optimal slots based on availability, time-of-day preferences learned from past bookings, and the nature of the meeting (calls vs. in-person tend toward different time windows). Presented as a numbered list in voice and as clickable cards in the dashboard.

**Acceptance Criteria:**
- Suggestion list excludes all times occupied by existing events.
- Suggestions respect working hours preference.
- User selection by number or description navigates directly to F027 (event creation).

**Technical Requirements:** Availability check (F028); preference-weighted slot ranking; dashboard time slot card component.

**Does Not Include:** Learning from external participants' preferred meeting times.

**Dependencies:** F026, F028, F056 (preference learning for time-of-day patterns)

**Priority:** P2 | **Complexity:** Medium | **Phase:** v1.0

---

#### F030 — Calendar Invite Dispatch

**Description:** After creating a calendar event with attendees, sends a Google Calendar invitation to each attendee email address via the Google Calendar API. The invitation appears in each attendee's Google Calendar and inbox as a standard calendar invite. Invitation dispatch is automatic after the user confirms event creation — no separate command is required.

**Acceptance Criteria:**
- Invitations are dispatched to all attendees within 5 seconds of event creation.
- A confirmation message lists all attendees who received an invite.
- Attendees with non-Google email addresses receive an ICS calendar file via the API's invitation mechanism.

**Technical Requirements:** Google Calendar API `events.insert` with `sendUpdates: "all"` parameter; attendee email list from F023.

**Does Not Include:** Custom invitation message body, RSVP tracking in v1.0.

**Dependencies:** F027, F023

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0

---

#### F031 — Multi-Provider Calendar Support

**Description:** Extends calendar integration to Microsoft Outlook (via Graph API), Apple Calendar (via CalDAV), and Calendly (via API). Requires provider-specific OAuth flows and adapter layers behind the existing calendar interface.

**Priority:** P3 | **Complexity:** High | **Phase:** v2.0

---

### 3.5 Task & Reminder Features

---

#### F032 — Task Creation

**Description:** Creates a task record in the PostgreSQL `tasks` table from a natural-language command. Extracts task title, optional description, priority (low/normal/high/urgent), and due date. Tasks without a specified due date are stored with `due_date = NULL` and appear in an "Undated" section in the dashboard. Tasks can be created from voice commands, text commands, and as a result of action item extraction from meetings (F044). Task creation does not require confirmation, as it is a reversible, internally-scoped action.

**Acceptance Criteria:**
- Task is stored and visible in dashboard within 2 seconds of command.
- Temporal entities ("by Friday," "next week") resolve to correct ISO 8601 dates in the user's timezone.
- Priority keywords ("urgent," "high priority") correctly populate the `priority` field.

**Technical Requirements:** `POST /api/v1/tasks`; temporal entity extraction via AI Model Router; timezone resolution via user preference.

**Does Not Include:** Task assignment to other users, task dependencies (v1.5), subtask support.

**Dependencies:** F047 (intent parsing); Celery Beat (for due-date notifications)

**Priority:** P1 | **Complexity:** Low | **Phase:** v1.0

---

#### F033 — Task Status Management

**Description:** Allows the user to update task status — pending, in_progress, completed, cancelled — by voice or from the dashboard. Completing a task moves it to the "Completed" section in the dashboard. Cancelling removes it from the active list without deletion (soft delete). The user can also query task status: "What tasks do I have pending?" returns a summary read aloud and displayed in the dashboard.

**Acceptance Criteria:**
- Status update takes effect within 1 second of command.
- "Mark it done" and similar natural-language completions work when a task was recently referenced in the session.
- Completed tasks are not included in the morning briefing's active task list.

**Technical Requirements:** `PATCH /api/v1/tasks/{id}`; session context (last referenced task); dashboard task panel with status filter.

**Does Not Include:** Bulk status update for multiple tasks in a single command (v1.5).

**Dependencies:** F032

**Priority:** P1 | **Complexity:** Low | **Phase:** v1.0

---

#### F034 — Task Prioritisation

**Description:** Assigns and updates priority levels (low, normal, high, urgent) on tasks. Priority affects sorting order in the dashboard task list and escalation behaviour in the morning briefing. Urgent tasks appear at the top of the briefing regardless of due date. Priority can be set at creation or updated by voice command.

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0

**Dependencies:** F032, F033

---

#### F035 — Reminder Creation

**Description:** Creates a time-triggered reminder in the `reminders` table. Requires a message and a trigger time, both extractable from natural-language commands. Supports absolute time references ("at 10 AM tomorrow") and relative references ("in 2 hours"). Optional repeat settings: daily, weekly. Reminders can be linked to an existing task (populates `task_id` FK) or standalone. Creation does not require confirmation.

**Acceptance Criteria:**
- Reminder is stored within 1 second of command.
- Relative time references resolve correctly against the user's current local time.
- Creating a reminder with a past trigger time surfaces an immediate warning and prompts correction.

**Technical Requirements:** `POST /api/v1/reminders`; temporal entity extraction; Celery Beat scheduling.

**Does Not Include:** Location-based reminders (v2.0), context-aware trigger conditions ("remind me when I email Priya").

**Dependencies:** F047, Celery Beat

**Priority:** P1 | **Complexity:** Low | **Phase:** v1.0

---

#### F036 — Reminder Delivery

**Description:** Delivers triggered reminders at the scheduled time via WebSocket push (if dashboard is open) and Web Push notification (if browser notifications are permitted). TTS reads the reminder message aloud if voice is active. Reminder status is updated to "triggered" after delivery. If the user dismisses the notification, status updates to "dismissed." If no dismissal is recorded within 5 minutes, a second delivery attempt is made.

**Acceptance Criteria:**
- Reminder fires within 30 seconds of the scheduled trigger time.
- Web Push notification is delivered even when the dashboard tab is not active.
- TTS reads the reminder message when voice mode is enabled.
- Second delivery attempt occurs if no dismissal within 5 minutes.

**Technical Requirements:** Celery Beat trigger job; `webpush` Python library; WebSocket event; TTS (F003).

**Dependencies:** F035, Celery Beat, F003

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F037 — Overdue Task Escalation

**Description:** A Celery Beat job runs daily at midnight, identifying all tasks where `due_date < NOW()` and `status != 'completed'`. These tasks are updated to `status = 'overdue'` and added to the morning briefing as priority items. If the user is actively using Alex when the overdue check runs, a dashboard notification is pushed immediately.

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0 | **Dependencies:** F032, F036, F060

---

#### F038 — Recurring Reminder Support

**Description:** Extends F035 to support daily and weekly repeat schedules. After each delivery, Celery Beat automatically schedules the next occurrence. The user can cancel a recurring reminder by voice ("Stop reminding me about the standup") or from the dashboard.

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0 | **Dependencies:** F035, F036

---

#### F039 — Task–Calendar Correlation

**Description:** Intelligently correlates tasks with calendar events — for example, surfacing a task tagged "prepare for Q1 review" when a calendar event called "Q1 Review" is detected on the same day. Correlations are surfaced as smart suggestions in the briefing and dashboard.

**Priority:** P2 | **Complexity:** Medium | **Phase:** v1.5 | **Dependencies:** F026, F032, F051

---

### 3.6 Meeting Features

---

#### F040 — Meeting Audio Capture

**Description:** Captures audio from the browser's microphone during a meeting session initiated by the user. Audio is captured in 30-second chunks via the Web Audio API and streamed to the backend via WebSocket for transcription. A recording indicator showing elapsed time is displayed in the dashboard. The user explicitly starts and stops recording. Raw audio files are stored in Supabase Storage under the `meeting-recordings` bucket, keyed by meeting UUID.

**Acceptance Criteria:**
- Recording starts within 1 second of the "Start Meeting" command.
- Recording indicator updates elapsed time every second.
- Audio chunks are delivered to the backend with < 2 seconds of latency.
- Raw audio files are stored in Supabase Storage and associated with the meeting record.

**Technical Requirements:** Web Audio API (browser); WebSocket audio streaming; Supabase Storage; `meetings` table record creation on session start.

**Does Not Include:** Multi-participant audio capture, screen audio capture, Zoom/Meet bot integration (F046).

**Dependencies:** F041 (consumes audio); Supabase Storage

**Priority:** P2 | **Complexity:** Medium | **Phase:** v1.0

---

#### F041 — Real-Time Meeting Transcription

**Description:** Processes incoming 30-second audio chunks from F040 using `faster-whisper` (free mode) or the OpenAI Whisper API (paid mode). Each chunk's transcription is appended to a live transcript document displayed in the dashboard's Meeting panel, updating in real time via WebSocket. Speaker attribution is not supported in v1.0 — all text is attributed to a single speaker. The complete transcript is stored as a text file in Supabase Storage at session end, with its path saved to `meetings.transcript_path`.

**Acceptance Criteria:**
- Each 30-second chunk is transcribed within 5 seconds (free mode) or 2 seconds (paid mode).
- Transcript panel updates continuously during the meeting without page refresh.
- Complete transcript is saved to Supabase Storage within 30 seconds of session end.
- Transcription errors in individual chunks are logged but do not terminate the session.

**Technical Requirements:** `faster-whisper` (free) or OpenAI Whisper API (paid); WebSocket chunk pipeline; Supabase Storage; `meetings.transcript_path` update.

**Does Not Include:** Speaker diarisation, confidence score display per word, keyword highlighting during meeting.

**Dependencies:** F040, F048 (paid mode routing)

**Priority:** P2 | **Complexity:** High | **Phase:** v1.0

---

#### F042 — Meeting Summary Generation

**Description:** At meeting session end, sends the full transcript text to the AI Model Router with a structured summarisation prompt. The prompt instructs the model to extract: meeting title (inferred), key discussion points, decisions made, unresolved questions, and a separate list of action items with assignees where named. The generated summary is stored in `meetings.summary` and displayed in the dashboard Meeting History panel. Available for review and sharing immediately after the meeting.

**Acceptance Criteria:**
- Summary is generated within 60 seconds of session end for meetings up to 90 minutes.
- Summary contains at minimum: key points, decisions, and action items sections.
- Summary is displayed in the dashboard without requiring a page refresh.
- Summary generation failure (model timeout) is communicated to the user and retried once.

**Technical Requirements:** AI Model Router (meeting summary prompt template from AI Instructions Document); `meetings.summary` column update; dashboard Meeting History component.

**Does Not Include:** Editing the generated summary within Alex (user can copy and edit elsewhere).

**Dependencies:** F041, F048, F043

**Priority:** P2 | **Complexity:** High | **Phase:** v1.0

---

#### F043 — Action Item Extraction

**Description:** Extracts structured action items from the meeting summary. Each action item captures: description, assigned person (if named), and due date (if mentioned). Extracted as a JSON array stored in `meetings.action_items`. Surfaced to the user immediately after summary generation with an offer to create tasks from them.

**Acceptance Criteria:**
- Action items are extracted correctly for ≥ 85% of explicitly stated action assignments in test transcripts.
- Assignee names are extracted when explicitly stated ("Rohan will send the report").
- Action items without explicit assignees default to the user as owner.
- Items are presented as a numbered list with assignee and due date visible.

**Technical Requirements:** Structured JSON output prompt in AI Model Router; `meetings.action_items` JSON column; dashboard action item list component.

**Does Not Include:** Inferring implicit action items not directly stated in the transcript.

**Dependencies:** F042

**Priority:** P2 | **Complexity:** High | **Phase:** v1.0

---

#### F044 — Action Item to Task Conversion

**Description:** Offers to convert extracted action items (F043) into tasks in the `tasks` table. The user confirms once ("Add them all as tasks") rather than individually. Action items assigned to named individuals other than the user are still created as tasks, with a note indicating the intended assignee. The `tasks.source` field is set to `'meeting'` and `tasks.meeting_id` is populated with the originating meeting UUID.

**Acceptance Criteria:**
- All extracted action items are created as tasks with a single confirmation.
- Tasks created from meetings are visible in the dashboard task list with a "From meeting" badge.
- `meeting_id` FK is populated and queryable.

**Technical Requirements:** Batch `POST /api/v1/tasks`; `tasks.source = 'meeting'`; `tasks.meeting_id` FK.

**Does Not Include:** Sending action items to named assignees via email or WhatsApp automatically (requires user command).

**Dependencies:** F043, F032

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0

---

#### F045 — Meeting History & Search

**Description:** A searchable archive of all past meeting summaries and transcripts, accessible from the dashboard. Search by date, attendee name, or keyword. Semantic search across summary content via pgvector for natural-language queries ("find the meeting where we discussed the ACME contract").

**Priority:** P3 | **Complexity:** Medium | **Phase:** v1.5

---

#### F046 — Video Call Bot Integration

**Description:** Deploys an automated bot that joins Zoom, Google Meet, or Microsoft Teams calls, records audio directly, and streams it to Alex for transcription — eliminating the need for the user to manually start recording.

**Priority:** P3 | **Complexity:** High | **Phase:** v2.0

---

### 3.7 Intelligence & Decision Features

---

#### F047 — Intent Parsing

**Description:** Transforms raw user text (from STT or text input) into a structured intent object containing: intent type, ordered action steps, extracted entities (contacts, files, dates, times), and an ambiguity score. Uses the AI Model Router (F048) with a structured intent extraction prompt. If ambiguity score exceeds 0.4, generates one clarifying question rather than proceeding or failing. The intent object is the input to the Task Planner (F065). Intent parsing uses a short-term context window of the last five turns (from F054) to resolve pronouns and references correctly.

**Acceptance Criteria:**
- Correct intent classification in ≥ 90% of test cases covering all ten user flows.
- Ambiguity detection triggers a clarifying question rather than a wrong action for scores > 0.4.
- Intent parser never returns an unhandled exception to the user — all errors surface as graceful "I didn't understand" responses.
- Entities (contact names, file references, dates) are extracted correctly in ≥ 92% of test cases.

**Technical Requirements:** AI Model Router (F048); structured JSON output mode; intent prompt template (AI Instructions Document); session context from Redis/pgvector; `POST /api/v1/command` handler.

**Does Not Include:** Learning user-specific phrasing patterns over time (that is F059, v2.0).

**Dependencies:** F048, F054, F006

**Priority:** P1 | **Complexity:** High | **Phase:** v1.0

---

#### F048 — AI Model Router (Free/Paid)

**Description:** The single abstraction layer through which all AI model calls flow. Reads `ai_mode` from the user preferences table at call time (not at startup), enabling hot-switching without a process restart. In free mode, routes to Ollama at `http://localhost:11434/api/generate` using Mistral 7B Instruct (primary) or LLaMA 3.1 8B (fallback). In paid mode, routes to the Anthropic Messages API (claude-sonnet-4-20250514, primary) or OpenAI Chat Completions API (gpt-4o, fallback). Exposes a single `async generate(prompt, system, temperature, max_tokens, response_format)` interface. All callers are agnostic to the active provider.

**Acceptance Criteria:**
- Mode switch from free to paid takes effect on the next API call with no restart required.
- If primary provider fails (timeout, API error), fallback provider is attempted automatically.
- If both providers fail in paid mode, system falls back to free mode and notifies the user.
- Router logs provider used, latency, and token count for every call to audit_logs.

**Technical Requirements:** Python `httpx` async client; Anthropic Python SDK; OpenAI Python SDK; `ai_mode` preference read at call time; provider fallback chain; `audit_logs` write.

**Does Not Include:** Per-feature model selection (all features use the same active provider in v1.0), fine-tuning.

**Dependencies:** preferences table (`ai_mode`, `paid_provider`); Ollama service (free mode); Anthropic/OpenAI API keys in Supabase secrets (paid mode)

**Priority:** P1 | **Complexity:** High | **Phase:** v1.0

---

#### F049 — Multi-Intent Command Handling

**Description:** Correctly processes commands containing multiple discrete intents — "Search for the contract, summarise it, and email it to Rohan" — by producing a multi-step intent object with an ordered array of action steps and dependency declarations. Each step specifies which previous step's output it requires as input. Passed to the Task Planner (F065) for execution plan construction.

**Acceptance Criteria:**
- Commands with up to five sequential actions are parsed and structured correctly.
- Step dependencies are correctly declared (email send correctly declares dependency on file search).
- The confirmation preview renders all steps in human-readable order before execution.

**Technical Requirements:** Multi-step intent schema in AI Model Router prompt; dependency graph in Task Planner; confirmation preview component.

**Does Not Include:** Parallel step execution (all steps are sequential in v1.0).

**Dependencies:** F047, F065

**Priority:** P1 | **Complexity:** High | **Phase:** v1.0

---

#### F050 — Ambiguity Detection & Clarification

**Description:** When the Intent Parser calculates an ambiguity score above 0.4 for a given input, generates exactly one targeted clarifying question rather than proceeding with a potentially wrong interpretation or rejecting the command. The question is the minimum ask needed to resolve the ambiguity — it never asks for information already available in the context window. After the user's clarification response, the intent is re-parsed with the original input plus the clarification appended.

**Acceptance Criteria:**
- Only one clarifying question is ever asked per ambiguous command.
- The clarifying question correctly targets the source of ambiguity (wrong file, ambiguous recipient, unclear timing).
- Re-parsed intent after clarification achieves a score below 0.4 in ≥ 90% of tested cases.
- Alex never asks a question whose answer is already in the session context.

**Technical Requirements:** Ambiguity scoring in intent prompt; question generation prompt; session context update with clarification.

**Dependencies:** F047, F006

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F051 — Smart Suggestions Engine

**Description:** Analyses user behaviour patterns — frequently contacted people, recurring tasks, past command sequences — and proactively surfaces relevant suggestions at appropriate moments. Examples: "You usually email a summary to Priya after client calls. Want me to draft one?" Suggestions are surfaced in the dashboard and optionally via TTS. The user can dismiss or act on each suggestion.

**Priority:** P2 | **Complexity:** High | **Phase:** v1.5

---

#### F052 — Proactive Follow-Up Nudges

**Description:** Monitors elapsed time since specific triggering events (meeting ended, email sent with no reply, task due date approaching) and surfaces a proactive nudge to the user in the briefing or as a dashboard notification.

**Priority:** P2 | **Complexity:** Medium | **Phase:** v1.5

---

#### F053 — Vision / Image Understanding

**Description:** Accepts image input (screenshots, photos, scanned documents) and extracts meaning — text via OCR, content description, or structured data. Uses Claude's vision capability (paid mode) or an open-source vision model (free mode).

**Priority:** P3 | **Complexity:** High | **Phase:** v2.0

---

### 3.8 Memory & Personalization Features

---

#### F054 — Session Memory (Short-Term)

**Description:** Stores the last five turns of the active conversation session in Redis (TTL: 30 minutes of inactivity). This context is passed to the Intent Parser with every new command, enabling pronoun resolution and follow-up commands. Session context is keyed by `session_id` (UUID generated at dashboard load). Context clears automatically on session timeout and can be manually cleared by the user.

**Acceptance Criteria:**
- Session context is correctly available to the Intent Parser on every command within a session.
- Follow-up commands ("Do the same for Rohan") correctly resolve references from the prior turn.
- Session context clears after 30 minutes of inactivity.
- Context clear command ("Start over") resets to an empty context within one cycle.

**Technical Requirements:** Redis key `session:{session_id}:context` (TTL 1800s); context serialisation to JSON; `session_id` passed in every `POST /api/v1/command` request.

**Does Not Include:** Persistent cross-session context (that is F055).

**Dependencies:** Redis; F047

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F055 — Long-Term Semantic Memory

**Description:** Stores embeddings of past interactions in pgvector for semantic recall across sessions. After each completed interaction, a summary of the input and response is embedded using all-MiniLM-L6-v2 and stored in the `conversation_memory` pgvector collection. When a new command is received, the top three semantically similar past interactions are retrieved and included in the Intent Parser context window, giving Alex relevant background without requiring the user to repeat themselves across sessions.

**Acceptance Criteria:**
- Relevant past interactions are retrieved in ≥ 80% of test cases where past context would aid interpretation.
- Memory recall adds < 500 ms to total command processing time.
- Memory entries older than 90 days are automatically pruned by a nightly Celery job.
- The user can view their stored memories in the dashboard Memory panel and delete individual entries.

**Technical Requirements:** pgvector `conversation_memory` table; all-MiniLM-L6-v2 embedding at interaction end; cosine similarity retrieval; Celery nightly pruning job; `GET /api/v1/memory/history`; `DELETE /api/v1/memory/history`.

**Does Not Include:** Cross-user memory sharing, memory export.

**Dependencies:** pgvector; F047; F054

**Priority:** P1 | **Complexity:** High | **Phase:** v1.0

---

#### F056 — User Preference Learning

**Description:** Learns and stores the user's preferences in the `preferences` PostgreSQL table as key-value pairs. Preferences are updated in two ways: explicitly (user says "I prefer formal emails") and implicitly (system detects consistent patterns over five or more interactions, such as always choosing 1 PM slots for meetings). Preferences cover: default email tone, preferred meeting time window, most-used contacts, working hours, AI mode, briefing time, and voice settings. All preferences are visible and editable in the Settings panel.

**Acceptance Criteria:**
- Explicit preference commands update the preferences table within 1 second.
- Implicit preference detection triggers after five consistent instances of the same behaviour.
- Preferences correctly influence AI prompt parameters and contact ranking.

**Technical Requirements:** `preferences` table; preference extraction in AI Model Router post-processing; `PATCH /api/v1/memory/preferences`; Settings panel component.

**Does Not Include:** Preference export, syncing preferences across devices.

**Dependencies:** F048, F055

**Priority:** P2 | **Complexity:** Medium | **Phase:** v1.0

---

#### F057 — Preference Review & Correction

**Description:** Dashboard panel listing all stored preferences with human-readable labels. The user can edit or delete any preference. Voice command "What have you learned about me?" reads the top ten most significant stored preferences aloud.

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0 | **Dependencies:** F056

---

#### F058 — Contact Frequency Ranking

**Description:** Updates `contacts.frequency` (interaction count) after every successful contact resolution and use. Frequency ranking influences search result ordering in F023 — contacts used more often appear higher in ambiguous resolution results.

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0 | **Dependencies:** F023, F024

---

#### F059 — Behavioural Adaptation Engine

**Description:** Analyses long-term interaction patterns to adaptively change Alex's default behaviours — adjusting response verbosity, proactive suggestion frequency, and confirmation thresholds based on how the user has responded over time.

**Priority:** P3 | **Complexity:** High | **Phase:** v2.0

---

### 3.9 Briefing & Summary Features

---

#### F060 — Morning Briefing Generation

**Description:** Generates a structured, personalised morning briefing by aggregating data from four sources: today's calendar events (F026), due and overdue tasks (F032, F037), upcoming reminders (F035), and priority inbox emails (F019). All aggregated data is sent to the AI Model Router with a briefing composition prompt that instructs the model to produce a concise, spoken-word-friendly summary. The briefing is delivered via TTS (F003) and rendered in the dashboard's "Today" panel simultaneously. Briefing generation is triggered by Celery Beat at the user's configured time (default 7:30 AM), or on-demand via voice command.

**Acceptance Criteria:**
- Briefing generation completes within 20 seconds of trigger.
- Briefing covers all four data sources when data is available.
- Graceful degradation when any data source is unavailable (calendar or email failure does not block briefing).
- On-demand briefing ("Give me my briefing") triggers the same generation flow.
- Briefing is marked as delivered for the day; a second trigger before midnight returns "I already gave you your briefing today. Want me to repeat it?"

**Technical Requirements:** Celery Beat daily job; briefing composition prompt (AI Instructions Document); `GET /api/v1/calendar/events`, `GET /api/v1/tasks`, `GET /api/v1/reminders`, IMAP read; TTS (F003); dashboard Today panel.

**Does Not Include:** Briefing push to mobile device, multi-day briefings, briefing sharing.

**Dependencies:** F026, F032, F035, F019, F048, F003, F062, Celery Beat

**Priority:** P2 | **Complexity:** High | **Phase:** v1.0

---

#### F061 — Briefing Scheduling

**Description:** Allows the user to configure the time at which the morning briefing is automatically delivered each day. Configurable in Settings and by voice command ("Set my briefing to 8 AM"). Stored in `preferences.system.briefing_time`. Celery Beat dynamically reschedules the delivery job when this preference changes.

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0 | **Dependencies:** F060, Celery Beat

---

#### F062 — Voice Briefing Delivery

**Description:** The morning briefing is spoken aloud by Alex via TTS (F003) upon generation. The user can interrupt at any time by saying "Stop" to halt TTS playback. After the briefing is delivered, Alex waits for a follow-up command with the briefing context still active in the session (enabling commands like "Reschedule the 10 AM to the afternoon" referencing an event just mentioned).

**Priority:** P2 | **Complexity:** Low | **Phase:** v1.0 | **Dependencies:** F060, F003

---

#### F063 — Priority Inbox Summary in Briefing

**Description:** Reads UNSEEN and FLAGGED emails from the last 12 hours via IMAP and includes a summary of each (sender name + subject line only; no body content) in the morning briefing. A maximum of five priority emails are surfaced in the briefing to maintain conciseness.

**Priority:** P2 | **Complexity:** Medium | **Phase:** v1.0 | **Dependencies:** F019, F060

---

#### F064 — Project Status in Briefing

**Description:** Adds a project status section to the morning briefing based on task clusters — grouping tasks by project tag and summarising progress for each active project. Requires a project tagging system for tasks, which is a v1.5 addition.

**Priority:** P3 | **Complexity:** High | **Phase:** v1.5

---

### 3.10 Automation Features

---

#### F065 — Multi-Step Task Execution

**Description:** The Automation Engine executes the ordered execution plan produced by the Task Planner. It runs steps sequentially, passes each step's output as context to the next step via a shared execution context dictionary, and handles errors at each step boundary. On any step failure, execution halts and the user is given a clear report of which steps succeeded, which failed, and the error detail. The user is offered options: retry the failed step, skip it, or cancel the plan. Execution never proceeds past a failed step automatically.

**Acceptance Criteria:**
- Plans with up to five steps execute in correct dependency order.
- Step outputs are correctly passed as inputs to dependent steps (e.g., file search result as email attachment).
- Any step failure halts execution at that point — subsequent steps do not execute.
- Partial failure report is delivered via TTS and shown in the dashboard within 3 seconds of failure detection.
- Retry, skip, and cancel options are all functional from the dashboard and by voice.

**Technical Requirements:** `AutomationEngine` Python class; step dependency graph; execution context dict; `PATCH /api/v1/plans/{id}/status`; WebSocket step completion events; Celery for async steps.

**Does Not Include:** Parallel step execution, rollback of completed steps, plan persistence across sessions.

**Dependencies:** F047, F049, F066, F067, F068

**Priority:** P1 | **Complexity:** High | **Phase:** v1.0

---

#### F066 — Execution Plan Preview

**Description:** Before executing any plan with `confirmation_required: true`, serialises the execution plan into a human-readable step list and presents it to the user via TTS (voice mode) and as a visual step list in the dashboard. The user must explicitly confirm before execution begins. The confirmation prompt times out after 60 seconds with automatic cancellation if no response is received.

**Acceptance Criteria:**
- Plan preview renders all steps with plain-language descriptions (not technical identifiers).
- Confirmation timeout of 60 seconds is enforced consistently.
- User can say "Yes," "Go ahead," "Confirm," or equivalent to proceed.
- User can say "No," "Cancel," or "Stop" to cancel.

**Technical Requirements:** Plan serialisation to human-readable text; TTS delivery of plan; dashboard plan preview component; WebSocket confirmation event; 60-second timeout with Celery task.

**Dependencies:** F047, F049, F065

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F067 — Step Dependency Resolution

**Description:** The Task Planner analyses the ordered steps from the intent object and builds a dependency graph, declaring which steps require the output of prior steps. The Automation Engine respects this graph during execution, only starting a step when all its declared dependencies have completed successfully. Template variables (e.g., `{{step_1_result}}`) in step parameters are substituted with actual outputs at execution time.

**Acceptance Criteria:**
- Template variable substitution works correctly for file path, summary text, and contact email outputs.
- A step with an unmet dependency raises `DependencyError` rather than executing with null inputs.
- Dependency graph correctly models all standard two- and three-step workflows.

**Technical Requirements:** Dependency graph in Task Planner; template variable substitution engine; execution context dictionary.

**Dependencies:** F049, F065

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F068 — Partial Failure Recovery

**Description:** When any step in an execution plan fails, the Automation Engine produces a partial failure report specifying completed steps, the failed step, and the error reason in plain language. The dashboard renders this as a visual step status list. The user is offered three recovery options: retry the failed step (re-executes from that step with the same context), skip and continue (marks step as skipped and proceeds to next steps where possible), or cancel the remaining plan.

**Acceptance Criteria:**
- Partial failure is surfaced within 3 seconds of error detection.
- Retry option correctly re-attempts the failed step without re-running successful prior steps.
- Skip option correctly continues to the next step where dependencies allow.
- Cancel correctly halts all remaining steps without any side effects.

**Technical Requirements:** `ExecutionResult` data model; WebSocket failure event; dashboard step status component; retry queue via Celery.

**Dependencies:** F065, F066

**Priority:** P1 | **Complexity:** Medium | **Phase:** v1.0

---

#### F069 — n8n Workflow Integration

**Description:** Connects Alex's automation layer to self-hosted n8n for complex, multi-service workflow execution. Alex can trigger n8n workflows via webhook by name or description, passing execution context as JSON payload. Use cases include: posting a meeting summary to a Slack channel, creating a Notion page from meeting notes, or syncing a completed task to a project management tool. n8n workflow definitions are stored as JSON in the `/workflows` directory of the repository.

**Acceptance Criteria:**
- Alex can trigger an n8n workflow by webhook within 2 seconds of command.
- Execution context (file paths, summary text, contact details) is correctly passed to n8n as a JSON payload.
- n8n workflow execution errors are surfaced back to Alex and reported to the user.

**Technical Requirements:** n8n self-hosted on Railway; `httpx` webhook call in FastAPI; workflow registry (name-to-webhook-URL mapping) in preferences.

**Does Not Include:** Building n8n workflows through Alex's voice interface.

**Dependencies:** n8n deployment on Railway; F065

**Priority:** P2 | **Complexity:** Medium | **Phase:** v1.0

---

#### F070 — Autonomous Agent Mode

**Description:** An opt-in mode in which Alex executes multi-step plans without confirmation prompts, monitors the results of each step, and makes autonomous decisions about retries and alternative paths. Reserved for v2.0 pending security review and user trust research.

**Priority:** P3 | **Complexity:** High | **Phase:** v2.0

---

## 4.0 Feature Dependencies Map

The following map shows which features are prerequisites for others. A feature cannot ship without all features it depends on being complete.

```
CORE INFRASTRUCTURE (must be built first)
  F048 — AI Model Router
    └── Required by: F003, F016, F017, F021, F042, F043, F047, F060
  F047 — Intent Parser
    └── Required by: F049, F050, F054, F065
  F054 — Session Memory
    └── Required by: F006, F047
  F009 — File Directory Indexing
    └── Required by: F010, F011, F012, F013, F014

VOICE PIPELINE
  F001 (Wake Word)
    └── requires: F002
  F002 (STT)
    └── requires: F001 or F004
    └── required by: F047
  F003 (TTS)
    └── required by: F060, F062, F003 (briefing delivery)
  F004 (Text Chat)
    └── required by: F047

FILE SEARCH CHAIN
  F009 → F010 → F011 → F013
  F012 depends on F009
  F018 depends on F010, F011, F013
  F022 depends on F010, F011, F013

COMMUNICATION CHAIN
  F023 (Contact Resolution)
    └── required by: F016, F021, F022, F027, F030
  F016 (Email Send)
    └── requires: F023, F048
    └── required by: F018, F020
  F021 (WhatsApp Send)
    └── requires: F023, F048
    └── required by: F022

CALENDAR CHAIN
  F026 (Calendar Read)
    └── required by: F027, F028, F029, F030, F060
  F028 (Availability Check)
    └── required by: F027, F029
  F027 (Event Create)
    └── requires: F028, F023
    └── required by: F030

TASK & REMINDER CHAIN
  F032 (Task Create)
    └── required by: F033, F034, F037, F044
  F035 (Reminder Create)
    └── required by: F036, F038
  F036 (Reminder Delivery) requires Celery Beat

MEETING CHAIN
  F040 (Audio Capture)
    └── required by: F041
  F041 (Transcription)
    └── required by: F042
  F042 (Summary)
    └── required by: F043
  F043 (Action Items)
    └── required by: F044

BRIEFING CHAIN
  F060 requires: F026, F032, F035, F019, F048, F003
  F061 requires: F060
  F062 requires: F060, F003
  F063 requires: F019, F060

AUTOMATION CHAIN
  F065 (Multi-Step Execution)
    └── requires: F047, F049, F066, F067, F068
  F066 (Plan Preview) requires: F047, F049
  F067 (Dependency Resolution) requires: F049
  F068 (Partial Failure) requires: F065

MEMORY CHAIN
  F054 → F055 → F056 → F057
  F058 requires: F023
```

---

## 5.0 Phase Release Plan

### 5.1 v1.0 — Launch Release (Must Have)

These features constitute the minimum viable Alex. The product is not shippable without all P1 features and the P2 features marked as required below.

| Feature ID | Feature Name | Priority |
|-----------|-------------|----------|
| F001 | Wake Word Detection | P1 |
| F002 | Speech-to-Text Transcription | P1 |
| F003 | Text-to-Speech Response | P1 |
| F004 | Text Chat Interface | P1 |
| F005 | Voice / Text Mode Switching | P1 |
| F006 | Multi-Turn Conversation Context | P2 |
| F009 | File Directory Indexing | P1 |
| F010 | Keyword File Search | P1 |
| F011 | Semantic File Search | P1 |
| F012 | Real-Time File Watcher | P1 |
| F013 | File Disambiguation | P1 |
| F014 | File Preview in Dashboard | P2 |
| F016 | Email Compose & Send | P1 |
| F017 | Email Tone Adjustment | P2 |
| F018 | Email with File Attachment | P1 |
| F019 | Email Inbox Reading | P2 |
| F021 | WhatsApp Message Send | P1 |
| F022 | WhatsApp File Send | P1 |
| F023 | Contact Resolution (Fuzzy Match) | P1 |
| F024 | Contact Management | P2 |
| F026 | Calendar Event Reading | P1 |
| F027 | Calendar Event Creation | P1 |
| F028 | Availability Check | P1 |
| F029 | Smart Time Slot Suggestion | P2 |
| F030 | Calendar Invite Dispatch | P2 |
| F032 | Task Creation | P1 |
| F033 | Task Status Management | P1 |
| F034 | Task Prioritisation | P2 |
| F035 | Reminder Creation | P1 |
| F036 | Reminder Delivery | P1 |
| F037 | Overdue Task Escalation | P2 |
| F038 | Recurring Reminder Support | P2 |
| F040 | Meeting Audio Capture | P2 |
| F041 | Real-Time Meeting Transcription | P2 |
| F042 | Meeting Summary Generation | P2 |
| F043 | Action Item Extraction | P2 |
| F044 | Action Item to Task Conversion | P2 |
| F047 | Intent Parsing | P1 |
| F048 | AI Model Router (Free/Paid) | P1 |
| F049 | Multi-Intent Command Handling | P1 |
| F050 | Ambiguity Detection & Clarification | P1 |
| F054 | Session Memory (Short-Term) | P1 |
| F055 | Long-Term Semantic Memory | P1 |
| F056 | User Preference Learning | P2 |
| F057 | Preference Review & Correction | P2 |
| F058 | Contact Frequency Ranking | P2 |
| F060 | Morning Briefing Generation | P2 |
| F061 | Briefing Scheduling | P2 |
| F062 | Voice Briefing Delivery | P2 |
| F063 | Priority Inbox Summary in Briefing | P2 |
| F065 | Multi-Step Task Execution | P1 |
| F066 | Execution Plan Preview | P1 |
| F067 | Step Dependency Resolution | P1 |
| F068 | Partial Failure Recovery | P1 |
| F069 | n8n Workflow Integration | P2 |

**v1.0 total: 51 features**

---

### 5.2 v1.5 — Iterative Enhancement (Should Have, 60–90 days post v1.0)

| Feature ID | Feature Name | Priority |
|-----------|-------------|----------|
| F020 | Smart Email Follow-Up Suggestion | P2 |
| F025 | Multi-Channel Communication History | P3 |
| F039 | Task–Calendar Correlation | P2 |
| F045 | Meeting History & Search | P3 |
| F051 | Smart Suggestions Engine | P2 |
| F052 | Proactive Follow-Up Nudges | P2 |
| F064 | Project Status in Briefing | P3 |

**v1.5 total: 7 features**

---

### 5.3 v2.0 — Advanced Capabilities (Nice to Have, 6–12 months post v1.0)

| Feature ID | Feature Name | Priority |
|-----------|-------------|----------|
| F007 | Voice Emotion Awareness | P3 |
| F008 | Multilingual Voice Support | P3 |
| F015 | Cloud File Storage Support | P3 |
| F031 | Multi-Provider Calendar Support | P3 |
| F046 | Video Call Bot Integration | P3 |
| F053 | Vision / Image Understanding | P3 |
| F059 | Behavioural Adaptation Engine | P3 |
| F070 | Autonomous Agent Mode | P3 |

**v2.0 total: 8 features**

---

## 6.0 Open Questions

| # | Question | Owner | Resolution Target |
|---|----------|-------|------------------|
| FL-OQ-1 | F041 (Meeting Transcription) processes 30-second audio chunks via `faster-whisper`. On free mode with CPU-only inference, this may lag behind real time for longer meetings. Should the chunk size be configurable (e.g., 10 seconds for better accuracy vs. 60 seconds for lower CPU load)? | Engineering | Before F040/F041 development |
| FL-OQ-2 | F055 (Long-Term Semantic Memory) prunes entries older than 90 days. Is 90 days the correct default? Some users may want Alex to remember important interactions indefinitely. Should this be user-configurable? | Product | Before F055 development |
| FL-OQ-3 | F023 (Contact Resolution) uses fuzzy string matching. For users with very large contact lists (500+ contacts), Levenshtein matching may become slow. Should a pgvector-based semantic contact search be used as a fallback for large contact databases? | Engineering | Before F023 development |
| FL-OQ-4 | F060 (Morning Briefing) triggers at a fixed time from Celery Beat. If the user's device is off or disconnected at briefing time, the briefing is not delivered. Should Alex detect a missed briefing and offer it at the next login? | Product | Before F060 development |
| FL-OQ-5 | F065 (Multi-Step Execution) runs steps sequentially. Several common workflows (email to multiple recipients, indexing multiple directories) would benefit from parallel execution. Should parallelism be introduced for independent steps with no declared dependencies? | Engineering | Before v1.5 planning |
| FL-OQ-6 | The Feature List includes 51 v1.0 features. Given the dependencies and complexity of the high-rated items, should any P2 features (e.g., F040–F044 Meeting Copilot, F060–F063 Briefing) be deferred to v1.5 to reduce the launch surface and improve delivery confidence? | Product | Before sprint planning |

---

## 7.0 Next Steps

With the Feature List Document complete, the following decisions are locked and available to the remaining documentation:

All 70 features are assigned IDs (F001–F070), prioritised, phased, and cross-referenced to their stack components. The v1.0 release surface is 51 features across ten categories. All eight v2.0 features are explicitly deferred and should not influence the Security Document or AI Instructions Document.

The two remaining documents to author are:

1. **Security Document (v1.0)** — covers credential encryption (Supabase secrets for API keys and email credentials), JWT validation in FastAPI, PostgreSQL Row Level Security policies, the action permission model described in USER_FLOW.md §5.0, and audit log data retention. This document must specifically address the security implications of F016, F021, F022 (outbound communication), F048 (AI API key handling), and F055 (long-term memory storage).

2. **AI Instructions Document (v1.0)** — specifies the exact prompt templates for every AI-powered feature: F047 (Intent Parser), F049 (Multi-Intent), F050 (Ambiguity Detection), F042 (Meeting Summary), F043 (Action Item Extraction), F060 (Briefing Composer), F016 (Email Composition), and F021 (WhatsApp composition). Each template must specify the model it is optimised for, the expected JSON output schema, and the fallback behaviour when the model returns malformed output.

---

*Document maintained by the Alex Build Team. Feature IDs F001–F070 are stable identifiers and must be referenced consistently in all sprint planning, QA, and documentation work going forward. Version history tracked in the project changelog.*
