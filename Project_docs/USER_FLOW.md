# User Flow Document
## Alex — Personal AI Operating System
**Version:** v1.0
**Date:** 24 March 2026
**Status:** Draft
**Author:** Alex Build Team
**References:** PRD.md v1.0, SYSTEM_DESIGN.md v1.0, TECH_STACK.md v1.0, GOAL.md

---

## Table of Contents

1.0 Purpose & Scope
2.0 User Journey Overview
3.0 Core User Flows
  - 3.1 Onboarding Flow
  - 3.2 Voice Command Flow
  - 3.3 File Search & Send Flow
  - 3.4 Email Send Flow
  - 3.5 WhatsApp Message Flow
  - 3.6 Calendar Booking Flow
  - 3.7 Task & Reminder Flow
  - 3.8 Morning Briefing Flow
  - 3.9 Meeting Transcription Flow
  - 3.10 Multi-Step Task Flow
4.0 Edge Cases & Error Handling
5.0 Confirmation & Permission Flows
6.0 Open Questions
7.0 Next Steps

---

## 1.0 Purpose & Scope

### 1.1 Purpose

This User Flow Document maps every major interaction a user has with Alex v1.0 — from first launch through day-to-day operation. For each flow it specifies the trigger that initiates it, every decision point the system encounters, the happy path through to a successful outcome, and the error paths that arise when things go wrong.

This document is the authoritative reference for frontend engineers building the dashboard, backend engineers implementing the API endpoints, and QA engineers writing acceptance tests. Every screen state, every WebSocket event, and every confirmation prompt described in this document corresponds directly to a component or endpoint defined in SYSTEM_DESIGN.md and TECH_STACK.md.

### 1.2 Scope

This document covers ten core user flows that together represent the full functional surface of Alex v1.0 as defined in PRD.md. It does not cover administrative flows (account deletion, billing management) or v1.1 features (multi-user, mobile, CRM integrations). Onboarding is treated as a first-class flow because the decisions made during setup — AI mode selection, directory configuration, calendar authorisation — shape every subsequent interaction.

### 1.3 Notation

All flows in this document use a consistent ASCII notation:

```
[TRIGGER]       — the event that starts the flow (user action, scheduled job, external event)
[STEP]          — a processing step performed by the system or the user
<DECISION>      — a branching point with two or more possible outcomes
{OUTCOME}       — a terminal state (success, failure, or waiting for input)
-->             — forward progression
--> [Y] / [N]   — branch taken on Yes or No
```

---

## 2.0 User Journey Overview

### 2.1 First-Time User Experience

A new user arrives at Alex either via the web dashboard URL (Vercel deployment) or by running the stack locally with Docker Compose. They have not authenticated, connected any services, or configured any directories. The system presents a linear onboarding sequence that collects the minimum required configuration to make Alex operational.

The critical first-session path is: **account creation → AI mode selection → voice setup → directory configuration → calendar authorisation → email setup → WhatsApp setup → first command**. Each step after account creation is individually completable and skippable, so users who do not have a WhatsApp account or who do not want calendar access can proceed without blocking.

At the end of onboarding, Alex delivers a short spoken greeting and runs a live test command — "What do I have on today?" — to demonstrate end-to-end functionality before the user issues their first real command.

### 2.2 Returning User Experience

A returning user who has completed onboarding arrives at the dashboard already authenticated (Supabase Auth JWT stored in the browser, refreshed automatically). If the user has voice enabled, Porcupine's wake word detection is active immediately upon page load. If the user configured a morning briefing, Alex checks whether the briefing for the current day has been delivered and, if not, offers to deliver it.

The returning user's primary interaction loop is: **wake word or text input → intent parsed → plan confirmed or auto-executed → result delivered via voice and dashboard update**. This loop is designed to require zero navigation — the user never needs to open a menu or locate a button to accomplish routine tasks.

---

## 3.0 Core User Flows

---

### 3.1 Onboarding Flow

**Trigger:** User visits the Alex dashboard for the first time (no authenticated session present).

**Purpose:** Collect the minimum configuration required for Alex to be operational, establish the user's AI mode preference, and demonstrate a working end-to-end command before session close.

#### 3.1.1 Happy Path

```
[USER VISITS DASHBOARD — NO SESSION]
        |
        v
[Display: Welcome screen + "Get Started" CTA]
        |
        v
[STEP 1: Account Creation]
  User enters email + password
  OR clicks "Continue with Google"
        |
        v
  <Supabase Auth: credentials valid?>
        |
       [Y]------------------------------------------------[N]
        |                                                  |
        v                                                  v
  [JWT issued, session started]              {Show error: "Invalid credentials.
        |                                     Try again or reset password."}
        v
[STEP 2: AI Mode Selection]
  Display: "How should Alex think?"
  Option A: Free Mode (local AI — works offline, no API cost)
  Option B: Paid Mode (Claude / GPT-4o — faster, smarter)
        |
        v
  <User selects mode>
        |
   [Free Mode]----------------------------[Paid Mode]
        |                                      |
        v                                      v
  [Save: ai_mode = "free"]        [Prompt: Enter Anthropic or
  [Check: Ollama reachable?]       OpenAI API key]
        |                                      |
  <Ollama available?>              [Encrypt key → Supabase secrets]
       [Y]       [N]                           |
        |         |                    [Save: ai_mode = "paid"]
        v         v                            |
  [Confirm]  [Warn: "Ollama         [Test API key validity]
              not detected.                    |
              Alex will run              <Key valid?>
              in text-only                [Y]     [N]
              mode until               [Cont.]  [Show error +
              Ollama starts."]                    re-prompt]
        |
        v
[STEP 3: Voice Setup]
  Display: "Set up your wake word"
  Default: "Hey Alex"
  Option: Skip voice setup
        |
        v
  <User clicks "Test Wake Word">
  [Browser requests microphone permission]
        |
  <Permission granted?>
       [Y]                    [N]
        |                      |
        v                      v
  [Play test prompt]    [Warn: "Microphone access
  [User says            denied. Voice features
   "Hey Alex"]          will be unavailable.
        |                You can enable them later
  <Wake word             in Settings."]
  detected?>                   |
   [Y]       [N]               v
    |         |          [Skip voice setup]
    v         v
[Confirm  [Retry prompt
 voice     up to 3x,
 active]   then offer skip]
        |
        v
[STEP 4: Directory Configuration]
  Display: "Which folders should Alex watch?"
  User selects one or more local directories
  (Default suggestion: ~/Documents, ~/Desktop)
        |
        v
  [Save watched_dirs to preferences]
  [Trigger background file indexing job via Celery]
  [Display: "Indexing started — this runs in the background"]
        |
        v
[STEP 5: Google Calendar (Optional)]
  Display: "Connect Google Calendar?"
        |
  <User clicks "Connect">
        |
        v
  [OAuth 2.0 redirect → Google consent screen]
        |
  <User grants access?>
       [Y]                    [N / Skip]
        |                          |
        v                          v
  [Store refresh token       [Mark calendar as
   in Supabase secrets]       not connected]
  [Run initial calendar sync] [User can connect later
  [Confirm: "Calendar          in Settings]
   connected successfully"]
        |
        v
[STEP 6: Email Setup (Optional)]
  Display: "Connect your email?"
  User enters: email address, SMTP/IMAP credentials
        |
  <User provides credentials>
        |
        v
  [Test IMAP connection]
        |
  <Connection successful?>
       [Y]                    [N / Skip]
        |                          |
        v                          v
  [Encrypt credentials]      [Show error details +
  [Store in Supabase]         offer retry or skip]
  [Confirm connected]
        |
        v
[STEP 7: WhatsApp Setup (Optional)]
  Display: "Connect WhatsApp via Twilio?"
  User enters Twilio Account SID + Auth Token
  OR clicks "Skip for now"
        |
        v
  [Validate Twilio credentials]
        |
  <Valid?>
   [Y]         [N / Skip]
    |                |
    v                v
  [Save to     [Mark WhatsApp
   Supabase]    not connected]
  [Confirm]
        |
        v
[STEP 8: Onboarding Complete]
  Display: "Alex is ready."
  Alex speaks (TTS): "Hi, I'm Alex. Let's get started.
                      Ask me anything."
  Auto-run demo command: "What do I have on today?"
        |
        v
  [Alex reads from calendar + tasks + reminders]
  [Delivers first real response]
        |
        v
{ONBOARDING COMPLETE — DASHBOARD ACTIVE}
```

#### 3.1.2 Error Path Summary

If Google Calendar, email, or WhatsApp setup fails, onboarding is not blocked. The user proceeds to the dashboard with those integrations marked as "Not Connected" and a persistent banner offering to complete setup at any time. AI mode defaults to free if Ollama is unreachable; paid mode re-attempts connection on the next command if Ollama remains down.

---

### 3.2 Voice Command Flow

**Trigger:** User says "Hey Alex" (wake word) OR types a message in the dashboard chat input.

**Purpose:** Accept a user command, parse intent, plan execution, confirm if necessary, and return a response — all within the 2-second latency target for short commands.

#### 3.2.1 Happy Path

```
[TRIGGER: Wake word detected by Porcupine]
  OR
[TRIGGER: User types message in dashboard]
        |
        v
<Input source?>
  [Voice]                          [Text]
     |                                |
     v                                v
[STT: faster-whisper              [Text accepted directly —
 transcribes audio]                no STT step]
[Confidence score attached]
     |
     v
[Dashboard: show "Listening..." indicator]
     |
     v
[POST /api/v1/command]
  { input: "text", source: "voice"|"text", session_id }
        |
        v
[INTENT PARSER]
  AI Model Router called with:
  - prompt template (see AI Instructions Document)
  - user text
  - session context (last 5 turns from pgvector)
        |
        v
  <ambiguity_score > 0.4?>
       [Y]                              [N]
        |                               |
        v                               v
  [Generate one                  [Intent object produced]
   clarifying question]
  [TTS: speak the question]
  [Dashboard: show question]
  [Wait for user response]
  [Re-run intent parser with
   clarified input]
        |
        v
[TASK PLANNER]
  Decomposes intent into ordered steps
        |
        v
  <confirmation_required?>
       [Y]                              [N]
        |                               |
        v                               v
  [Build human-readable         [Execute immediately]
   plan preview]
  [TTS: "Here's what I'll do: ...
   Should I go ahead?"]
  [Dashboard: show plan
   with step list]
  [Wait for user: "Yes" / "No"]
        |
  <User confirms?>
   [Yes]          [No / Cancel]
     |                  |
     v                  v
  [Execute]     {CANCELLED — "No problem.
                 Let me know if you'd
                 like to change anything."}
        |
        v
[AUTOMATION ENGINE executes each step]
  [WebSocket: push progress events to dashboard]
  [Dashboard: show step completion in real time]
        |
        v
[ALL STEPS COMPLETE]
  [TTS: speaks result]
  [Dashboard: updates relevant panel]
  [Write to audit_logs]
  [Store interaction in pgvector memory]
        |
        v
{SUCCESS — response delivered via voice + dashboard}
```

#### 3.2.2 Error Path

```
[STT confidence < 0.6]
        |
        v
[TTS: "I didn't catch that — could you repeat?"]
[Retry STT up to 2 times]
        |
  <Still low confidence after retries?>
       [Y]
        v
[TTS: "I'm having trouble hearing you.
       You can also type your request."]
{FALLBACK TO TEXT INPUT}
```

---

### 3.3 File Search & Send Flow

**Trigger:** User issues a command referencing a file, e.g. "Find the Q1 proposal" or "Send Priya the contract."

**Purpose:** Locate the correct file from the indexed directories and either present it, attach it to a message, or deliver it via the next action in the plan.

#### 3.3.1 Happy Path

```
[TRIGGER: File reference detected in intent]
  e.g. "Find the Q1 proposal"
        |
        v
[FILE SEARCH ENGINE]
  Step 1 — Keyword search (PostgreSQL FTS)
    Query: file name, extension, date filters
    Returns: ranked candidates
        |
        v
  Step 2 — Semantic re-rank (pgvector)
    Embed query with all-MiniLM-L6-v2
    Cosine similarity against file_index embeddings
    Returns: top 5 results with similarity scores
        |
        v
  <Top result score >= 0.85?>
       [Y]                              [N]
        |                               |
        v                               v
  [Auto-select file]            [Present top 3 candidates
  [Proceed with plan]            to user]
                                 [Dashboard: show file list
                                  with names + dates]
                                 [TTS: "I found a few matches.
                                  Which one did you mean?
                                  1. Q1_Report_2026.pdf
                                  2. Q1_Draft_v2.docx
                                  3. Q1_Proposal_Final.pdf"]
                                        |
                                        v
                                 [User selects by number
                                  or by name]
                                        |
                                        v
                                 [Proceed with selected file]
        |
        v
<Destination action in plan?>
        |
   [Present only]   [Attach to email]  [Send via WhatsApp]
        |                  |                    |
        v                  v                    v
[Dashboard:         [Pass file path      [Pass file path
 show file info      to Email            to WhatsApp
 + download link]    Send Flow]          Send Flow]
        |
        v
{FILE LOCATED AND ACTION DISPATCHED}
```

#### 3.3.2 Error Path

```
<No files found matching query?>
        |
        v
[TTS: "I couldn't find a file matching that description.
       Could you give me more details — like the file name
       or when you last worked on it?"]
[Dashboard: show search input for manual refinement]
        |
        v
  <User provides more detail?>
   [Y]                    [N]
    |                      |
    v                      v
  [Re-run search]    {CANCELLED — "No problem.
                      Let me know if you'd like
                      to try a different search."}

<Watched directory has changed and file no longer exists?>
        |
        v
[TTS: "I found a reference to that file, but it seems
       to have been moved or deleted."]
[Trigger re-index of watched directory]
{FLOW ENDED — user informed}
```

---

### 3.4 Email Send Flow

**Trigger:** User issues an email command, e.g. "Email Rohan the meeting summary" or "Send a follow-up to Priya."

**Purpose:** Compose, optionally attach files, resolve the recipient, confirm, and dispatch the email via Resend (transactional API) or SMTP.

#### 3.4.1 Happy Path

```
[TRIGGER: email intent detected]
  e.g. "Email Rohan the meeting summary"
        |
        v
[CONTACT RESOLUTION]
  Fuzzy match "Rohan" against contacts table
        |
        v
  <Match confidence?>
  [Single match > 0.9]   [Multiple matches]    [No match]
         |                      |                   |
         v                      v                   v
  [Resolve to         [TTS: "Did you mean    [TTS: "I don't
   rohan@email.com]    Rohan Mehta or         have Rohan's
                        Rohan Sharma?"]        email. What is
                       [User clarifies]        it?"]
                            |                  [User provides]
                            v                  [Save to contacts?
                       [Proceed with            Optional]
                        confirmed contact]           |
                                                     v
                                               [Proceed with
                                                provided email]
        |
        v
[CONTENT RESOLUTION]
  <Attachment referenced?>
       [Y]                              [N]
        |                               |
        v                               v
  [Run File Search Flow          [No attachment —
   (§3.3) to locate file]         text-only email]
  [Attach resolved file]
        |
        v
[COMPOSE EMAIL]
  AI Model Router generates:
  - Subject line (inferred from context)
  - Body (using user's preferred tone from preferences)
  - Attachment included if resolved
        |
        v
[CONFIRMATION GATE]
  Dashboard: show email preview
    - To: rohan@email.com
    - Subject: "Meeting Summary — 25 March 2026"
    - Body: [generated text]
    - Attachment: meeting_summary.pdf (if any)
  TTS: "Here's the email to Rohan.
        Want me to send it?"
        |
        v
  <User confirms?>
   [Yes]                    [No — modify]
     |                           |
     v                           v
  [Dispatch via Resend      [TTS: "What would you
   or SMTP]                  like to change?"]
  [Wait for delivery         [User specifies edit]
   confirmation]             [Re-generate + re-confirm]
        |
        v
  <Delivery confirmed?>
   [Y]                    [N]
    |                      |
    v                      v
[TTS: "Done.           [TTS: "The email
 Email sent            failed to send.
 to Rohan."]           I'll retry once."]
[Dashboard:            [Celery retry task
 update sent log]       queued]
        |                      |
        v               <Retry successful?>
{SUCCESS}                [Y]        [N]
                          |          |
                          v          v
                      {SUCCESS}  {FAILURE —
                                  user notified,
                                  email saved
                                  as draft}
```

---

### 3.5 WhatsApp Message Flow

**Trigger:** User issues a WhatsApp command, e.g. "Send Priya the Q1 report on WhatsApp."

**Purpose:** Resolve the recipient's WhatsApp ID, optionally attach a file, confirm the message, and dispatch via Twilio.

#### 3.5.1 Happy Path

```
[TRIGGER: WhatsApp intent detected]
  e.g. "Send Priya the Q1 report on WhatsApp"
        |
        v
<WhatsApp connected (Twilio configured)?>
   [Y]                         [N]
    |                           |
    v                           v
[Proceed]              [TTS: "WhatsApp isn't
                         set up yet. Want me
                         to help you connect it?"]
                       [Offer Settings shortcut]
                       {FLOW PAUSED}
        |
        v
[CONTACT RESOLUTION — WhatsApp ID]
  Match "Priya" against contacts.whatsapp_id
        |
        v
  <WhatsApp ID known?>
   [Y]                         [N]
    |                           |
    v                           v
  [Proceed]             [TTS: "I don't have
                          Priya's WhatsApp number.
                          What is it?"]
                         [User provides]
                         [Save to contacts]
        |
        v
<File attachment referenced?>
   [Y]                         [N]
    |                           |
    v                           v
[Run File Search        [Text-only message]
 Flow (§3.3)]
[Encode as media
 attachment]
        |
        v
[CONFIRMATION GATE]
  Dashboard: show message preview
    - To: Priya (+91-XXXXXXXXXX)
    - Content: file name or message text
  TTS: "Sending the Q1 report to Priya on WhatsApp.
        Shall I go ahead?"
        |
        v
  <User confirms?>
   [Yes]               [No]
     |                   |
     v                   v
  [Twilio API       {CANCELLED}
   dispatch]
  [Receive message
   SID confirmation]
        |
        v
  <Twilio delivery confirmed?>
   [Y]                    [N]
    |                      |
    v                      v
[TTS: "Done.          [TTS: "WhatsApp delivery
 Sent to Priya."]      failed. I'll retry shortly."]
[Log to audit_logs]   [Celery retry with backoff]
        |
        v
{SUCCESS}
```

---

### 3.6 Calendar Booking Flow

**Trigger:** User issues a scheduling command, e.g. "Book a one-hour call with Priya next Tuesday afternoon."

**Purpose:** Parse the time reference, check availability against the user's Google Calendar, resolve any conflicts, confirm the booking details, and create the event.

#### 3.6.1 Happy Path

```
[TRIGGER: Calendar booking intent detected]
  e.g. "Book a 1-hour call with Priya next Tuesday afternoon"
        |
        v
<Google Calendar connected?>
   [Y]                         [N]
    |                           |
    v                           v
[Proceed]               [TTS: "Google Calendar
                          isn't connected.
                          Want to connect it now?"]
                         [Offer OAuth flow shortcut]
                         {FLOW PAUSED}
        |
        v
[TEMPORAL ENTITY EXTRACTION]
  Parse: "next Tuesday afternoon"
  Resolve to: 2026-03-31, 12:00 PM – 6:00 PM window
  Duration: 60 minutes
        |
        v
[AVAILABILITY CHECK]
  Query cached calendar_events table
  Find free 60-minute slots within the time window
        |
        v
  <Free slots found?>
   [Y: 1 slot]       [Y: multiple slots]      [N: fully booked]
        |                     |                        |
        v                     v                        v
  [Proceed with        [TTS: "I found 3         [TTS: "Tuesday
   that slot]           slots on Tuesday         afternoon looks
                         afternoon:              fully booked.
                         1. 1:00 PM – 2:00 PM    How about
                         2. 3:00 PM – 4:00 PM    Wednesday
                         3. 4:30 PM – 5:30 PM    morning?"]
                         Which works best?"]    [Suggest next
                        [User selects slot]      available window]
        |
        v
[CONTACT RESOLUTION — attendee email]
  Resolve "Priya" to priya@email.com
        |
        v
[CONFIRMATION GATE]
  Dashboard: show event preview
    - Title: "Call with Priya"
    - Date: Tuesday, 31 March 2026
    - Time: 1:00 PM – 2:00 PM
    - Attendees: priya@email.com
    - Calendar invite: will be sent
  TTS: "I'll book a 1-hour call with Priya on Tuesday
        at 1 PM and send her an invite. Shall I?"
        |
        v
  <User confirms?>
   [Yes]                    [No — modify]
     |                           |
     v                           v
  [Google Calendar         [User specifies change]
   events.insert()]         [Re-plan + re-confirm]
  [Send invite to Priya]
  [Cache new event]
        |
        v
[TTS: "Done. Call with Priya booked for Tuesday at 1 PM.
       She's been sent an invite."]
[Dashboard: update calendar panel]
        |
        v
{SUCCESS}
```

---

### 3.7 Task & Reminder Flow

**Trigger:** User sets a task or reminder verbally or via text, e.g. "Remind me to follow up with Arjun tomorrow at 10 AM" or "Add a task: review the proposal by Friday."

**Purpose:** Parse the task or reminder details, store them, and trigger delivery at the specified time.

#### 3.7.1 Task Creation — Happy Path

```
[TRIGGER: Task/reminder intent detected]
  e.g. "Remind me to call Arjun tomorrow at 10 AM"
        |
        v
[ENTITY EXTRACTION]
  Action:    "call Arjun"
  Trigger:   "tomorrow at 10 AM"
  Resolved:  2026-03-26 10:00:00 IST
  Type:      reminder (time-based trigger)
        |
        v
[NO CONFIRMATION REQUIRED for simple reminders]
  [INSERT into reminders table]
  [Celery Beat schedules delivery job]
        |
        v
[TTS: "Got it. I'll remind you to call Arjun
       tomorrow at 10 AM."]
[Dashboard: reminder appears in upcoming list]
        |
        v
{SUCCESS — REMINDER STORED}
```

#### 3.7.2 Reminder Delivery — Happy Path

```
[TRIGGER: Celery Beat fires at 2026-03-26 10:00:00]
        |
        v
[Load reminder from database]
  message: "Call Arjun"
  trigger_at: 10:00 AM
        |
        v
<Dashboard open / user active?>
   [Y]                         [N]
    |                           |
    v                           v
[WebSocket push:          [Web push notification:
 "Reminder: Call Arjun"]   "Alex: Call Arjun"]
[TTS: "Just a reminder —
 you wanted to call Arjun."]
        |
        v
[Update reminder status → "triggered"]
[Dashboard: move to "Past Reminders"]
        |
        v
<Reminder has repeat setting?>
   [Y: daily/weekly]             [N]
    |                             |
    v                             v
[Schedule next                {DONE}
 occurrence in
 Celery Beat]
```

#### 3.7.3 Overdue Task Escalation

```
[TRIGGER: Celery Beat daily overdue check (midnight)]
        |
        v
[Query: tasks WHERE due_date < NOW() AND status != 'completed']
        |
        v
  <Overdue tasks found?>
   [Y]                    [N]
    |                      |
    v                      v
[Update status          {NO ACTION}
 → 'overdue']
[Add to next morning
 briefing as priority items]
[Web push if user active:
 "You have X overdue tasks"]
        |
        v
{ESCALATION LOGGED}
```

---

### 3.8 Morning Briefing Flow

**Trigger:** Celery Beat fires at user's configured briefing time (default: 7:30 AM) OR user says "Give me my morning briefing."

**Purpose:** Aggregate the day's schedule, pending tasks, overdue items, and priority inbox emails into a concise spoken and visual briefing.

#### 3.8.1 Happy Path

```
[TRIGGER: Celery Beat @ configured briefing time]
  OR
[TRIGGER: User says "Morning briefing" / "What's on today?"]
        |
        v
[BRIEFING COMPOSER — data aggregation]
  Query 1: tasks WHERE due_date = TODAY OR status = 'overdue'
  Query 2: reminders WHERE trigger_at BETWEEN NOW AND NOW+24h
  Query 3: calendar_events WHERE start_time BETWEEN NOW AND END OF DAY
  Query 4: IMAP SEARCH FLAGGED OR UNSEEN (last 12 hours, priority inbox)
        |
        v
  <Any data available across queries?>
   [Y]                         [N]
    |                           |
    v                           v
[Send all data to          [TTS: "Your schedule
 AI Model Router]           looks clear today.
 Prompt: "Generate a        No tasks, reminders,
 concise morning            or priority emails.
 briefing…"]                Enjoy your day."]
        |
        v
[Model returns structured briefing text]
  Format:
  - Greeting + date
  - Today's calendar events (chronological)
  - Due tasks (priority-sorted)
  - Overdue items (if any — flagged prominently)
  - Priority emails (sender + subject only)
  - One smart suggestion (if memory/preferences support it)
        |
        v
[TTS: speak full briefing]
[Dashboard: render briefing in "Today" panel]
[Mark briefing as delivered for today]
        |
        v
  <User asks follow-up question during briefing?>
   [Y]                         [N]
    |                           |
    v                           v
[Handle as new Voice        {BRIEFING COMPLETE}
 Command Flow (§3.2)
 with briefing context
 retained in session]
```

#### 3.8.2 Error Path

```
<Calendar API returns error during data aggregation?>
        |
        v
[Log error to Sentry]
[Proceed with available data (tasks + reminders)]
[Append to briefing: "Note: Calendar data is
 temporarily unavailable."]

<IMAP connection fails?>
        |
        v
[Proceed without inbox data]
[Append to briefing: "I couldn't check your email
 this morning — you may want to check it manually."]
```

---

### 3.9 Meeting Transcription Flow

**Trigger:** User says "Alex, start transcribing" or clicks "Start Meeting" in the dashboard while in a meeting.

**Purpose:** Capture ongoing audio, transcribe it in near-real-time, generate a structured summary with action items on request, and optionally create tasks from extracted action items.

#### 3.9.1 Happy Path

```
[TRIGGER: "Start meeting transcription"]
        |
        v
[REQUEST microphone permission if not already granted]
        |
        v
  <Permission available?>
   [Y]                         [N]
    |                           |
    v                           v
[Begin audio capture]    [TTS: "Microphone access
[Dashboard: show          is required for transcription.
 "Recording" indicator    Please enable it in your
 with elapsed time]       browser settings."]
        |                 {FLOW BLOCKED}
        v
[STT: faster-whisper processes audio in 30-second chunks]
[Each chunk transcribed and appended to live transcript]
[Dashboard: transcript panel updates in real time via WebSocket]
        |
        v
[TRIGGER: User says "Stop transcribing" or clicks "End Meeting"]
        |
        v
[Save raw transcript to Supabase Storage]
[Save transcript path to meetings table]
        |
        v
[SUMMARISATION]
  Send full transcript to AI Model Router
  Prompt: extract —
    - Meeting title (inferred)
    - Key decisions
    - Action items (with assignees where mentioned)
    - Attendees (detected from transcript)
        |
        v
[Model returns structured summary JSON]
[Save summary + action_items to meetings table]
[Dashboard: show summary in "Meeting" panel]
        |
        v
  <Action items extracted?>
   [Y]                         [N]
    |                           |
    v                           v
[TTS: "I found 3 action   {SUMMARY DISPLAYED —
 items. Want me to add     NO TASKS CREATED}
 them as tasks?"]
        |
  <User confirms?>
   [Yes]                    [No]
     |                        |
     v                        v
  [INSERT each action   {TASKS NOT CREATED —
   item into tasks        summary still saved}
   table with
   source = 'meeting']
  [TTS: "Done. 3 tasks
   added to your list."]
        |
        v
{MEETING FLOW COMPLETE}
```

---

### 3.10 Multi-Step Task Flow

**Trigger:** User issues a compound command that requires more than one action to complete, e.g. "Find the ACME contract, summarise it, and email it to Rohan with a note saying I'll call him Thursday."

**Purpose:** Demonstrate Alex's core autonomous execution capability — decomposing a complex instruction into an ordered plan, executing each step in sequence, passing outputs between steps, and recovering gracefully if any step fails.

#### 3.10.1 Happy Path

```
[TRIGGER: Multi-step command issued]
  Input: "Find the ACME contract, summarise it, and
          email it to Rohan with a note saying
          I'll call him Thursday"
        |
        v
[INTENT PARSER]
  Produces intent object:
  {
    intent: "multi_step_task",
    steps: [
      { action: "file_search",  query: "ACME contract" },
      { action: "summarise",    input: "{{step_1_result}}" },
      { action: "send_email",   to: "Rohan",
        attach: "{{step_1_result}}",
        body_context: "I'll call him Thursday",
        summary: "{{step_2_result}}" }
    ],
    requires_confirmation: true
  }
        |
        v
[TASK PLANNER — dependency graph]
  Step 1: file_search (no deps)
  Step 2: summarise (depends on step 1)
  Step 3: send_email (depends on step 1 + step 2)
        |
        v
[CONFIRMATION GATE — plan preview shown]
  Dashboard:
  ┌─────────────────────────────────────────┐
  │  Alex's Plan                            │
  │  ─────────────────────────────────────  │
  │  Step 1 ○  Search for "ACME contract"  │
  │  Step 2 ○  Summarise the document      │
  │  Step 3 ○  Email to Rohan with summary │
  │             + attachment               │
  │                                         │
  │  [Go ahead]          [Cancel]           │
  └─────────────────────────────────────────┘
  TTS: "Here's my plan. Should I go ahead?"
        |
        v
  <User confirms?>
   [Yes]                    [No]
     |                        |
     v                        v
  [Execute]            {CANCELLED}
        |
        v
[STEP 1: File Search]
  File Search Flow (§3.3)
  Result: /docs/ACME_Contract_2026.pdf
  Status: ✓ Complete
  [WebSocket: push step 1 complete event to dashboard]
        |
        v
[STEP 2: Summarise]
  Send document text to AI Model Router
  Prompt: "Summarise this contract in 3–5 sentences
           focusing on key obligations and deadlines"
  Result: "The ACME contract covers... [summary text]"
  Status: ✓ Complete
  [WebSocket: push step 2 complete event]
        |
        v
[STEP 3: Send Email]
  Email Send Flow (§3.4) — with pre-resolved inputs:
    - recipient: rohan@email.com (resolved in step 1)
    - attachment: ACME_Contract_2026.pdf
    - body includes: summary text + "I'll call Thursday"
  [No second confirmation — overall plan already confirmed]
  Status: ✓ Complete
  [WebSocket: push step 3 complete event]
        |
        v
[TTS: "All done. I found the ACME contract,
       summarised it, and emailed it to Rohan
       with a note about Thursday's call."]
[Dashboard: all steps marked complete]
[Write to audit_logs]
[Embed interaction in pgvector memory]
        |
        v
{MULTI-STEP FLOW COMPLETE}
```

#### 3.10.2 Error Path — Mid-Plan Failure

```
[STEP 2 FAILS: AI Model Router timeout]
        |
        v
[Automation Engine catches ActionError]
[Stop execution — do NOT proceed to step 3]
        |
        v
[TTS: "I completed step 1 — the contract is found —
       but I hit an error generating the summary.
       Step 3 (the email) hasn't been sent.
       Would you like me to retry the summary,
       skip it and send the file without a summary,
       or cancel the whole thing?"]
[Dashboard: show partial plan with failure state
  Step 1 ✓  Contract found
  Step 2 ✗  Summary failed — [Retry] [Skip] [Cancel]
  Step 3 ○  Email — waiting]
        |
        v
  <User choice?>
  [Retry]       [Skip step 2]     [Cancel]
     |                |                |
     v                v                v
  [Re-run         [Proceed to     {CANCELLED —
   step 2]         step 3 with     steps 1 was
  [If success →    file only,      completed;
   continue        no summary]     no email sent}
   to step 3]
```

---

## 4.0 Edge Cases & Error Handling

### 4.1 System-Level Failures

The table below documents every significant failure mode across the system, the user-facing message, and the recovery path.

| Failure | User-Facing Message | Recovery Path |
|---------|-------------------|---------------|
| Ollama offline (free mode) | "My AI brain seems to be sleeping. I'll try again in a moment." | Retry 3x with 5s backoff; if still unreachable, prompt to check Ollama status in Settings |
| Paid API key invalid or rate-limited | "There was an issue reaching the AI service. Switching to free mode temporarily." | Fallback to free mode; persist paid mode setting; retry next command with paid mode |
| PostgreSQL connection lost | "I'm having trouble accessing my memory right now." | FastAPI returns 503; Celery tasks paused; retry on reconnect via connection pool |
| Supabase Storage unreachable | "I couldn't access file storage at the moment." | Log to Sentry; complete non-storage steps; notify user of partial completion |
| Celery worker down | Background tasks (reminders, indexing, briefings) stop firing | Sentry alert sent; Railway auto-restarts worker service; queued tasks execute on restart |
| SMTP delivery failure | "The email failed to send. I'll try once more." | Single automatic retry after 60 seconds; if second failure, save as draft and notify |
| Twilio API error | "WhatsApp delivery failed. I'll retry shortly." | Celery retry with exponential backoff (60s, 5m, 30m); notify user after third failure |
| Google Calendar API auth expiry | "Your calendar connection has expired." | Prompt to re-authorise OAuth; briefings and scheduling proceed without calendar data |
| STT confidence below threshold | "I didn't quite catch that — could you repeat?" | Retry up to 2 times; offer text fallback on third failure |
| Wake word false positive | User can say "Stop" or "Never mind" at any time | Interrupt handler cancels active flow; system returns to listening state |
| File index corruption | Search returns no results for known files | Trigger full re-index of watched directories; notify user via dashboard banner |

### 4.2 Contact Resolution Failures

When a contact cannot be resolved, Alex never silently drops the action. It always informs the user of the resolution failure and requests the minimum information needed to proceed — typically a full name, email address, or phone number. Newly provided contact information is offered for saving to the contacts table to prevent the same failure in future sessions.

### 4.3 Timeout Handling

Long-running steps (AI inference in free mode, large file indexing, lengthy meeting transcription) display a progress indicator in the dashboard and a "still working…" voice prompt after 8 seconds. If a step exceeds 60 seconds, Alex notifies the user and offers to continue waiting or cancel. No step is silently abandoned.

### 4.4 Confirmation Timeout

If a confirmation prompt is presented and the user does not respond within 60 seconds, the plan is cancelled automatically and a brief notification is shown. This prevents unintended email sends or calendar bookings from executing after the user has walked away from the dashboard.

---

## 5.0 Confirmation & Permission Flows

### 5.1 When Alex Always Confirms Before Acting

The following actions are always gated behind an explicit user confirmation regardless of command source, AI mode, or prior user preferences:

| Action | Why Confirmation Required |
|--------|--------------------------|
| Send any email | Irreversible external communication |
| Send any WhatsApp message | Irreversible external communication |
| Create a calendar event with external invitees | Sends invitations to other people |
| Delete a task or reminder | Data loss; not easily reversible |
| Execute a plan with 3+ steps | High consequence; user should verify the full sequence |
| Use a paid AI API for the first time | Cost implication; user must opt in explicitly |
| Save a new contact's details | Privacy implication |
| Re-index all watched directories | Potentially long-running operation |

### 5.2 When Alex Acts Without Asking

The following actions execute automatically without a confirmation prompt, because they are low-consequence, reversible, or explicitly instructed:

| Action | Reason for Auto-Execution |
|--------|--------------------------|
| Set a reminder or task | Reversible; user-initiated; no external effect |
| Retrieve and display file search results | Read-only; no external effect |
| Read calendar events or inbox | Read-only; no external effect |
| Generate and display a meeting summary | No external effect; user has already requested it |
| Cache calendar sync or file index updates | Background system maintenance |
| Deliver a morning briefing | User has pre-authorised this at a specific time |
| Log command and result to audit_logs | System operation; fully user-visible |

### 5.3 Modify-and-Confirm Flow

When a user responds to a confirmation prompt with "No — change X", Alex enters a modify cycle rather than cancelling. The user specifies which element to change (recipient, tone, time, attachment), Alex re-generates the relevant part of the plan, and presents the updated confirmation. The modify cycle repeats as many times as the user needs before a final "yes" or "cancel" is given.

```
[CONFIRMATION PRESENTED]
        |
  <User response?>
  [Yes]       [Modify]           [Cancel]
    |              |                 |
    v              v                 v
[Execute]  [User states change] {CANCELLED}
            [Alex re-generates]
            [Re-present confirm]
            [Loop until Yes or Cancel]
```

### 5.4 Permission Escalation — First-Time Integrations

The first time Alex attempts to use any external integration (email send, WhatsApp message, calendar event creation), it presents a one-time permission prompt even if the integration was connected during onboarding. This provides a clear moment of informed consent that the integration will be used to perform real-world actions — distinct from the connection-level consent granted during setup.

```
[FIRST USE OF EMAIL SEND]
        |
        v
[Dashboard: "This is the first time Alex will
 send an email on your behalf. The email
 will come from your connected Gmail account.
 Allow Alex to send emails?"]
        |
  <User allows?>
   [Yes — save preference]   [No — this time only]   [Never — disable]
            |                         |                       |
            v                         v                       v
   [Execute + don't          [Execute once —          [Mark email as
    ask again]                ask again next time]     disabled in
                                                       settings]
```

---

## 6.0 Open Questions

| # | Question | Owner | Resolution Target |
|---|----------|-------|------------------|
| UF-OQ-1 | The voice command flow targets a 2-second response latency for short commands in free mode. Given faster-whisper STT (1–3 seconds) + Mistral 7B inference (3–8 seconds), the total pipeline may exceed 2 seconds on modest hardware. Should the latency target be revised, or should the streaming response pattern (return TTS as tokens generate) be implemented from day one? | Engineering / Product | Before backend development begins |
| UF-OQ-2 | The confirmation timeout is set at 60 seconds. Is this appropriate for all contexts — including voice users who may be moving around and text users who may be reading the plan carefully? Should different timeouts apply to voice vs. text confirmation prompts? | Product | Before frontend development begins |
| UF-OQ-3 | Meeting transcription currently captures all audio via the browser microphone, which picks up only the local participant's voice on a video call. How should Alex handle remote participants' voices in a video meeting? Options: screen audio capture, Zoom/Meet bot integration, or a clear disclaimer that only the local participant's speech is captured. | Engineering | Before Meeting Copilot development begins |
| UF-OQ-4 | The multi-step flow shows a plan preview before execution. For returning users who have confirmed similar plans many times, should Alex offer a "Trust Mode" that skips confirmation for low-risk plan types (e.g., file search + email to a known contact)? | Product | Before v1.1 planning |
| UF-OQ-5 | The morning briefing flow reads "priority inbox" via IMAP. How is a priority email defined? Options: FLAGGED messages only, UNSEEN messages from known contacts, a user-defined keyword filter, or a machine-learning classifier trained on the user's past interactions. | Product / AI | Before AI Instructions Document |
| UF-OQ-6 | When a file search yields zero results, Alex asks for more detail. Should Alex also proactively suggest triggering a re-index of watched directories, in case the file exists but was indexed before the current session? | Product | Before File Search feature development |

---

## 7.0 Next Steps

The flows defined in this document are now locked as the canonical reference for user interaction design in Alex v1.0. All ten flows map directly to backend API endpoints and frontend component states.

**Decisions locked by this document:** Confirmation is required for all irreversible external actions (email, WhatsApp, calendar creation with invitees, multi-step plans with 3+ actions). Auto-execution is permitted for all read-only and internally scoped operations. A modify cycle is available at every confirmation prompt. The voice and text input paths converge at the Intent Parser — no separate code path exists for voice vs. text commands.

The remaining documents to author, in order, are:

1. **Feature List Document (v1.0)** — enumerate every feature with acceptance criteria, the specific API endpoints and components involved, and the free-mode vs. paid-mode implementation path. The flows defined here serve as the primary source of acceptance criteria.
2. **Security Document (v1.0)** — define the credential encryption strategy (Supabase secrets), JWT validation in FastAPI, Row Level Security policies in PostgreSQL, and the action permission model referenced in Section 5.0 of this document.
3. **AI Instructions Document (v1.0)** — specify the exact prompt templates used by the Intent Parser, Task Planner, Briefing Composer, Meeting Summariser, and email composer — all of which are invoked in the flows documented here.

---

*Document maintained by the Alex Build Team. All flows in this document supersede informal interaction descriptions in SYSTEM_DESIGN.md. Version history tracked in the project changelog.*
