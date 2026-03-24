# User Flow Document — Alex: Personal AI Operating System
**Version:** v1.0
**Date:** 24 March 2026
**Status:** Draft
**References:** GOAL.md, PRD.md v1.0, SYSTEM_DESIGN.md v1.0
**Author:** Alex Project Team

---

## Table of Contents

1. [Purpose & Scope](#10-purpose--scope)
2. [User Journey Overview](#20-user-journey-overview)
3. [Core User Flows](#30-core-user-flows)
   - 3.1 [Onboarding Flow](#31-onboarding-flow)
   - 3.2 [Voice Command Flow](#32-voice-command-flow)
   - 3.3 [File Search & Send Flow](#33-file-search--send-flow)
   - 3.4 [Email Send Flow](#34-email-send-flow)
   - 3.5 [WhatsApp Message Flow](#35-whatsapp-message-flow)
   - 3.6 [Calendar Booking Flow](#36-calendar-booking-flow)
   - 3.7 [Task & Reminder Flow](#37-task--reminder-flow)
   - 3.8 [Morning Briefing Flow](#38-morning-briefing-flow)
   - 3.9 [Meeting Transcription Flow](#39-meeting-transcription-flow)
   - 3.10 [Multi-Step Task Flow](#310-multi-step-task-flow)
4. [Edge Cases & Error Handling](#40-edge-cases--error-handling)
5. [Confirmation & Permission Flows](#50-confirmation--permission-flows)
6. [Open Questions](#60-open-questions)
7. [Next Steps](#70-next-steps)

---

## 1.0 Purpose & Scope

### 1.1 Purpose

This document defines every significant user interaction with Alex — from first install through daily usage. It maps the complete journey a user takes for each major feature, including the happy path, all error paths, decision points, and recovery flows.

This document is the source of truth for frontend engineers, UX designers, and QA teams. Every screen state, confirmation prompt, and error message is defined here.

### 1.2 Decisions Carried Forward

| Decision | Source | Value |
|----------|--------|-------|
| Primary interface | PRD.md | Mobile-first (React Native); voice-first |
| Wake word | SYSTEM_DESIGN.md | "Hey Alex" (Porcupine on-device) |
| LLM | SYSTEM_DESIGN.md | Claude claude-sonnet-4-20250514 with tool use |
| Confirmation model | PRD.md US-1.4 | Required for irreversible/high-impact actions |
| Contact resolution | SYSTEM_DESIGN.md 4.5.3 | Fuzzy match → context → ask if ambiguous |
| Latency target | PRD.md | ≤ 2 seconds voice-to-first-response |
| WhatsApp API | SYSTEM_DESIGN.md | Meta Business API (official) |
| Draft by default | SYSTEM_DESIGN.md 4.5.1 | Email draft preview for first-time contacts |

### 1.3 Flow Notation

```
[TRIGGER]       — What starts the flow
[STEP]          — An action taken (by user or Alex)
<DECISION>      — A conditional branch point
[OUTCOME ✓]     — Successful end state
[OUTCOME ✗]     — Failed end state
[RECOVERY]      — How the user gets back on track
───►            — Normal flow direction
- - ►           — Error / alternative path
```

---

## 2.0 User Journey Overview

### 2.1 First-Time User Experience

```
Install App
    │
    ▼
[Onboarding: Welcome Screen]
    │
    ▼
[Grant Permissions: Mic, Notifications]
    │
    ▼
[Connect Accounts: Gmail → Google Calendar → Google Drive]
    │
    ▼
[Optional: Connect WhatsApp Business]
    │
    ▼
[Set Preferences: Name, Wake Time, Working Hours, Tone]
    │
    ▼
[File Indexing Begins] (background)
    │
    ▼
[Alex Introduction: Voice demo — "Hey Alex, what can you do?"]
    │
    ▼
[Home Screen — Ready to use]
```

**Time to first value:** < 5 minutes from install to first meaningful interaction.

---

### 2.2 Returning User — Daily Experience Arc

```
07:00 AM  ──►  [Push notification: "Your morning briefing is ready"]
                    │
                    ▼
               [User opens app or says "Hey Alex"]
                    │
                    ▼
               [Morning Briefing plays via TTS]
                    │
                    ▼
               [User acts on briefing items or dismisses]
                    │
──────────────────────────────────────────────────────────
Throughout day:
    ├── "Hey Alex, [voice command]"   ──► Voice Command Flow
    ├── Open app → type query         ──► Text Command Flow
    ├── Calendar reminder fires       ──► Pre-meeting prep notification
    └── Meeting ends                  ──► Meeting summary pushed
──────────────────────────────────────────────────────────
11:00 PM  ──►  [Background job: Consolidate day's memory]
               [Prepare next morning's briefing data]
```

---

## 3.0 Core User Flows

---

### 3.1 Onboarding Flow

**Trigger:** User installs Alex app for the first time.
**Goal:** User has all accounts connected and Alex is ready to use within 5 minutes.

#### 3.1.1 Happy Path

```
[INSTALL APP]
      │
      ▼
┌─────────────────────────────────────────────┐
│  SCREEN 1: Welcome                          │
│  "Hi, I'm Alex — your personal AI OS."     │
│  [Get Started]                              │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  SCREEN 2: Permissions                      │
│  Request: Microphone access                 │
│  Request: Notifications                     │
│  Request: Background app refresh            │
└──────────────────────┬──────────────────────┘
                       │
              <All granted?>
              /           \
           YES              NO
            │               │
            │         [Explain why needed]
            │         [Re-request]
            │               │
            └───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  SCREEN 3: Connect Google Account           │
│  [Connect Gmail + Calendar + Drive]         │
│  → OAuth 2.0 consent screen                 │
│  → Scopes: gmail.send, gmail.readonly,      │
│    calendar.events, drive.readonly          │
└──────────────────────┬──────────────────────┘
                       │
              <Auth successful?>
              /              \
           YES                NO
            │                 │
            │          [Show error + retry]
            │                 │
            └─────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  SCREEN 4: Connect WhatsApp (Optional)      │
│  "Link your WhatsApp number"                │
│  [Connect WhatsApp] or [Skip for now]       │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  SCREEN 5: Personal Preferences             │
│  • Your name: [text field]                  │
│  • Wake-up time: [time picker, default 7AM] │
│  • Working hours: [start] to [end]          │
│  • Tone: Formal / Balanced / Casual         │
│  [Save & Continue]                          │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  SCREEN 6: Indexing                         │
│  "Scanning your files in the background"    │
│  ████████░░ 80% — this takes ~2 minutes     │
│  [Continue to Alex →]                       │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  SCREEN 7: Quick Demo                       │
│  Alex speaks: "Try saying Hey Alex,         │
│  what's on my calendar today?"              │
│  [Microphone animates] → user speaks        │
│  → Alex responds with today's events        │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
              [HOME SCREEN — READY ✓]
```

#### 3.1.2 Error Paths

```
PERMISSION DENIED (Microphone)
    │
    ▼
Alex shows banner: "Alex needs microphone access for voice commands.
                    Text mode is still available."
    │
    ▼
Settings icon in header → Deep-links to iOS/Android app settings
    │
    ▼
User grants → mic activates immediately (no restart needed)

─────────────────────────────────────────────────────────

GOOGLE AUTH FAILS
    │
    ▼
"Couldn't connect your Google account. Please try again."
[Retry] [Contact Support]
    │
    ▼
On retry → fresh OAuth flow started
On 3rd failure → "Try again later. You can reconnect from Settings."
    │
    ▼
User proceeds without Google → text-only mode, limited features
    │
    ▼
Banner persists on home screen: "Connect Google to unlock full features"
```

---

### 3.2 Voice Command Flow

**Trigger:** User says "Hey Alex" or taps the microphone button.
**Goal:** Alex hears the command, understands intent, executes the correct action, and responds within ≤ 2 seconds.

#### 3.2.1 Happy Path

```
[USER SAYS "HEY ALEX"] or [TAPS MIC BUTTON]
      │
      ▼
[Porcupine detects wake word on-device]
      │
      ▼
[Microphone activates — UI shows waveform animation]
      │
      ▼
[USER SPEAKS COMMAND]
"Find the Q3 report and email it to Arjun"
      │
      ▼
[Deepgram streams audio → partial transcript shown live in UI]
      │
      ▼
[Silence detected → final transcript locked]
      │
      ▼
[Context assembled: system prompt + user profile + last 10 turns]
      │
      ▼
[Claude API called with tools — streaming enabled]
      │
      ▼
<Claude determines intent>
      │
      ├──► Single action needed → execute tool → stream response
      │
      └──► Multi-step needed → create plan → Automation Engine
      │
      ▼
[TOOL EXECUTED] (e.g., search_files + send_email)
      │
      ▼
[Claude streams final response text]
      │
      ▼
[ElevenLabs TTS streams audio — first chunk in ≤ 400ms]
      │
      ▼
[USER HEARS RESPONSE]
"Done — I found the Q3 Sales Report and emailed it to
 Arjun at arjun@company.com."
      │
      ▼
[Conversation turn saved to Redis + Supabase]
      │
      ▼
[UI: transcript + response shown in chat history]
      │
      ▼
[READY FOR NEXT COMMAND ✓]
```

#### 3.2.2 Low-Confidence Intent Path

```
[AMBIGUOUS COMMAND]: "Send it to him"
      │
      ▼
<Claude confidence < threshold?>
      │
      YES
      ▼
Alex asks ONE clarifying question:
"Send what to whom? I don't have a recent file or
 contact in context."
      │
      ▼
[User clarifies] → flow resumes from intent resolution
```

#### 3.2.3 Error Path

```
[STT FAILS / No audio detected]
      │
      ▼
Alex: "I didn't catch that — could you say it again?"
      │
      ▼
[Mic re-activates — user speaks again]
      │
      ▼
[On 2nd failure] → "Having trouble hearing you.
                   You can type your request instead."
      │
      ▼
[Text input field highlighted]

─────────────────────────────────────────────────────────

[CLAUDE API TIMEOUT / ERROR]
      │
      ▼
Alex: "I'm having a moment — give me a second."
[Spinner shown — retry in background, max 2 retries]
      │
      ├── Retry succeeds → continues normally
      │
      └── All retries fail →
          "Sorry, I couldn't process that right now.
           Try again in a moment." [Retry button shown]
```

---

### 3.3 File Search & Send Flow

**Trigger:** User requests to find a file, optionally followed by sending it.
**Goal:** Correct file retrieved in ≤ 3 seconds; optionally sent to a contact.

#### 3.3.1 Happy Path — Find Only

```
[TRIGGER]: "Find the proposal I sent to Priya last month"
      │
      ▼
[Claude calls: search_files("proposal Priya last month")]
      │
      ▼
[Query embedded → pgvector cosine similarity search]
      │
      ▼
<Results found?>
      │
      YES (score > 0.75)
      ▼
[Top 3 results returned with name, date, preview]
      │
      ▼
<1 clear top result (score gap > 0.15)?> 
      │
      ├── YES → Alex presents top result directly:
      │          "Found it — 'Priya_Consulting_Proposal_Feb2026.pdf'
      │           Last modified Feb 14. Want me to open or send it?"
      │
      └── NO (multiple similar scores) →
              Alex shows list:
              "I found 3 files that might match:
               1. Priya_Proposal_Feb2026.pdf
               2. Client_Proposal_Draft_v2.pdf
               3. Priya_Consulting_Brief.docx
               Which one?"
      │
      ▼
[User selects or confirms]
      │
      ▼
[FILE FOUND ✓] — shown in chat with name + preview + [Open] [Send] buttons
```

#### 3.3.2 Happy Path — Find & Send

```
[TRIGGER]: "Find the Q3 report and send it to Arjun on WhatsApp"
      │
      ▼
[search_files executed] → file found
      │
      ▼
<Contact resolved?>
      │
      ├── YES (Arjun → single match in contacts) →
      │       [send_whatsapp called with file attachment]
      │       → Sent ✓
      │       Alex: "Done — Q3 Sales Report sent to Arjun on WhatsApp."
      │
      └── NO (multiple Arjuns) →
              "Which Arjun? I have Arjun Mehta (+91 98xxx) 
               and Arjun Sharma (arjun@co.com)."
              User picks → send proceeds
      │
      ▼
[SENT ✓] — logged in sent_messages table
```

#### 3.3.3 Error Path — File Not Found

```
[search_files returns 0 results or all scores < 0.5]
      │
      ▼
Alex: "I couldn't find a file matching 'Q3 report' in your
       Google Drive. A few possibilities:
       • The file might not be indexed yet
       • Try a different description
       Want me to search again with different terms?"
      │
      ├── User rephrases → new search
      │
      └── [Re-index now] button → triggers background re-index
          Alex: "Re-indexing your Drive. I'll let you know
                 when it's ready — usually takes 2-3 minutes."
```

---

### 3.4 Email Send Flow

**Trigger:** User asks Alex to send an email, with or without an attachment.
**Goal:** Email drafted, optionally reviewed, and sent via Gmail API.

#### 3.4.1 Happy Path — Known Contact, No Attachment

```
[TRIGGER]: "Email Arjun and tell him the presentation is ready 
            for tomorrow's meeting"
      │
      ▼
[Claude calls: send_email tool]
      │
      ▼
[Contact resolved: Arjun → arjun@company.com (known, frequent)]
      │
      ▼
[Claude drafts email]:
  Subject: "Presentation Ready for Tomorrow's Meeting"
  Body: "Hi Arjun, just a quick note to let you know
         the presentation is ready for tomorrow. 
         Let me know if you need anything. Best, [User]"
      │
      ▼
<Is this a known/frequent contact?>
      │
      YES → skip preview (auto-send mode)
      ▼
[Gmail API → email sent]
      │
      ▼
Alex: "Email sent to Arjun — subject: 'Presentation Ready
       for Tomorrow's Meeting'."
      │
      ▼
[SENT ✓] — logged
```

#### 3.4.2 Happy Path — New Contact (Draft Preview Required)

```
[TRIGGER]: "Email Dr. Sharma about the invoice"
      │
      ▼
[Contact resolved: dr.sharma@clinic.in (first time emailing)]
      │
      ▼
[Claude drafts email]
      │
      ▼
<First-time contact?> → YES
      │
      ▼
[DRAFT PREVIEW shown in UI]:
┌─────────────────────────────────────────────────────┐
│  To: dr.sharma@clinic.in                           │
│  Subject: Invoice for [Service Name]               │
│  ─────────────────────────────────────             │
│  Dear Dr. Sharma,                                  │
│  Please find the invoice attached for...           │
│                                                    │
│  [Edit]  [Send ✓]  [Cancel ✗]                      │
└─────────────────────────────────────────────────────┘
      │
      ├── [Send ✓] → Gmail API → Sent ✓
      │              Alex: "Sent to Dr. Sharma."
      │
      ├── [Edit] → User edits inline → [Send] button
      │
      └── [Cancel] → Alex: "Okay, I've discarded that draft.
                            Let me know if you want to try again."
```

#### 3.4.3 Happy Path — With File Attachment

```
[TRIGGER]: "Email the contract to Priya with a note that it's 
            ready for her signature"
      │
      ▼
[PARALLEL EXECUTION]:
  ├── search_files("contract") → finds "Client_Contract_Priya.pdf"
  └── Contact resolved: priya@consulting.in
      │
      ▼
<User confirm attach correct file?>
      │
      ▼
Alex: "Found 'Client_Contract_Priya.pdf'. Should I attach
       that one?"  [Yes] [Different file]
      │
      YES
      ▼
[Email drafted + file attached as Google Drive link]
      │
      ▼
<Known contact?> → show/skip preview → Gmail API → Sent ✓
```

#### 3.4.4 Error Path

```
[GMAIL API FAILS]
      │
      ▼
Alex: "Couldn't send the email right now — Gmail returned
       an error. Should I try again or save it as a draft 
       in your Gmail?"
      │
      ├── [Try Again] → retry × 2
      │
      └── [Save as Draft] → Gmail API createDraft → 
          "Saved as a draft in your Gmail."
```

---

### 3.5 WhatsApp Message Flow

**Trigger:** User asks Alex to send a WhatsApp message or file.
**Goal:** Message sent via Meta Business API within the 24-hour window rules.

#### 3.5.1 Happy Path — Within 24h Window

```
[TRIGGER]: "WhatsApp Priya and tell her the meeting is moved 
            to 4 PM"
      │
      ▼
[Contact resolved: Priya → +91 9800000000]
      │
      ▼
<Last message to/from Priya on WhatsApp within 24h?>
      │
      YES → freeform message allowed
      ▼
[Claude drafts message]:
  "Hey Priya, just wanted to let you know the meeting has 
   been moved to 4 PM. See you then! 👍"
      │
      ▼
<Apply tone preference? Casual (set in memory)> → YES
      │
      ▼
[Meta Business API → message sent]
      │
      ▼
Alex: "Sent to Priya on WhatsApp."
      │
      ▼
[SENT ✓] — logged + message status webhook registered
```

#### 3.5.2 Outside 24h Window (Template Required)

```
[TRIGGER]: "WhatsApp the client about the invoice"
      │
      ▼
<Last WhatsApp interaction > 24 hours ago?>
      │
      YES → freeform blocked by Meta policy
      ▼
Alex: "I can't send a freeform WhatsApp message to this 
       contact right now — it's been more than 24 hours 
       since your last exchange. 
       Options:
       1. Send via email instead
       2. Use an approved message template
       Which would you prefer?"
      │
      ├── [Email instead] → routes to Email Send Flow
      │
      └── [Use template] → Alex selects best-fit approved template
                        → User confirms → sent via template API
```

#### 3.5.3 File Attachment via WhatsApp

```
[TRIGGER]: "Send the Q3 report to Arjun on WhatsApp"
      │
      ▼
[search_files + contact resolve run in parallel]
      │
      ▼
<File size ≤ 100MB (Meta limit)?>
      │
      ├── YES → file attached as document
      │         Alex: "Sent Q3 Sales Report to Arjun on WhatsApp."
      │
      └── NO → "That file is too large to send directly on WhatsApp 
                (limit: 100MB). Want me to:
                1. Share the Google Drive link instead
                2. Email it to Arjun"
```

---

### 3.6 Calendar Booking Flow

**Trigger:** User asks to check availability, create an event, or reschedule.
**Goal:** Correct event created in Google Calendar with attendees notified.

#### 3.6.1 Happy Path — Book a Meeting

```
[TRIGGER]: "Book a 1-hour call with Priya next Thursday afternoon"
      │
      ▼
[get_calendar("Thursday", free-busy)]
      │
      ▼
[Free slots returned: 1 PM, 3 PM, 4 PM on Thursday]
      │
      ▼
<More than one slot available?>
      │
      YES
      ▼
Alex: "You're free at 1 PM, 3 PM, or 4 PM next Thursday.
       Which works?"
      │
      ▼
[User: "3 PM is fine"]
      │
      ▼
[create_event called]:
  Title: "Call with Priya"
  Start: Thursday 3:00 PM
  End:   Thursday 4:00 PM
  Attendees: priya@consulting.in
  Video link: Google Meet (auto-generated)
      │
      ▼
[Google Calendar API → event created + invite sent to Priya]
      │
      ▼
Alex: "Done — 1-hour call with Priya booked for Thursday 
       at 3 PM. She'll get a calendar invite."
      │
      ▼
[EVENT CREATED ✓] — shown in chat with [View Event] button
```

#### 3.6.2 Happy Path — Check Availability

```
[TRIGGER]: "When am I free tomorrow afternoon?"
      │
      ▼
[get_calendar("tomorrow", user only)]
      │
      ▼
[Free slots identified: 2:00–3:30 PM, 5:00–6:00 PM]
      │
      ▼
Alex: "Tomorrow afternoon you have two free windows: 
       2:00–3:30 PM and 5:00–6:00 PM. 
       Want me to book something?"
      │
      ▼
[INFORMATION DELIVERED ✓] — no action unless user requests
```

#### 3.6.3 Reschedule Flow

```
[TRIGGER]: "Move my 2 PM meeting tomorrow to Thursday"
      │
      ▼
[get_calendar("tomorrow") → finds "Investor Update — 2:00 PM"]
      │
      ▼
<Correct event identified?>
      │
      YES → Alex: "Moving 'Investor Update' from tomorrow 2 PM
                   to Thursday — confirm?"
      │
      [Confirm] ─────►  [get_calendar("Thursday", free-busy)]
                               │
                        <Slot available at 2 PM Thursday?>
                        /                    \
                      YES                     NO
                       │                      │
              [update event →          "You have a conflict
               attendees notified]      at 2 PM Thursday.
               Alex: "Done —            How about 3 PM or 4 PM?"
               rescheduled."            → User picks → update
```

#### 3.6.4 Error Path — Conflict

```
[TRIGGER]: "Book a meeting with Arjun Tuesday at 10 AM"
      │
      ▼
[get_calendar → Tuesday 10 AM has "Team Standup"]
      │
      ▼
Alex: "You already have 'Team Standup' at 10 AM on Tuesday.
       Want me to find another time, or book it anyway?"
      │
      ├── [Find another time] → Alex suggests next free slot
      │
      └── [Book anyway] → double-booking confirmed by user → created
```

---

### 3.7 Task & Reminder Flow

**Trigger:** User asks to create, view, update, or complete a task or reminder.
**Goal:** Task stored with correct due date, surfaced at the right time.

#### 3.7.1 Create Task / Reminder

```
[TRIGGER]: "Remind me to follow up with Arjun on Friday at 9 AM"
      │
      ▼
[create_task called]:
  title: "Follow up with Arjun"
  due_at: Friday 09:00 AM
  related_contact: Arjun
  context: "Follow-up from conversation on [today's date]"
      │
      ▼
[Task saved to Supabase tasks table]
      │
      ▼
[Notification scheduled for Friday 9:00 AM]
      │
      ▼
Alex: "Got it — I'll remind you to follow up with Arjun
       this Friday at 9 AM."
      │
      ▼
[TASK CREATED ✓]

──────── At Friday 9:00 AM ────────────────────────────────
[Push notification]: "Reminder: Follow up with Arjun"
    │
    ▼
[User opens notification → Alex shows context]
Alex: "You wanted to follow up with Arjun today. 
       Want me to send him an email or WhatsApp now?"
    │
    ├── [Yes, email] → routes to Email Send Flow
    ├── [Yes, WhatsApp] → routes to WhatsApp Flow
    └── [Dismiss] → task marked snoozed (re-surfaces in 2 hours)
```

#### 3.7.2 View Tasks

```
[TRIGGER]: "What are my pending tasks?" 
      │
      ▼
[get_tasks(status="pending") + get_tasks(status="overdue")]
      │
      ▼
Alex: "You have 5 pending tasks:
       OVERDUE:
        • Email invoice to client (was due Monday)
       DUE TODAY:
        • Review Priya's proposal (due 5 PM)
       UPCOMING:
        • Call Arjun re: funding (Thursday)
        • Submit expenses (Friday)
        • Prepare Q3 deck (next week)"
      │
      ▼
[Each task shown as tappable card in UI]
```

#### 3.7.3 Complete / Update Task

```
[TRIGGER]: "Mark the Priya proposal task as done"
      │
      ▼
[get_tasks → matches "Review Priya's proposal"]
      │
      ▼
[PATCH /tasks/:id { status: "completed" }]
      │
      ▼
Alex: "Done — 'Review Priya's proposal' marked as complete."
      │
      ▼
[Task moves to completed list ✓]
```

---

### 3.8 Morning Briefing Flow

**Trigger:** Scheduled job at configured wake time (default 7:00 AM) OR user asks "Hey Alex, give me my briefing."
**Goal:** User receives a complete, prioritized daily briefing via voice and text.

#### 3.8.1 Auto-Delivery Happy Path

```
[07:00 AM — SCHEDULED JOB FIRES (BullMQ)]
      │
      ▼
[PARALLEL DATA FETCH]:
  ├── Google Calendar → today's events
  ├── Tasks DB → pending + overdue tasks
  ├── Gmail → unread important messages (last 12h)
  └── Memory → active projects, recent context
      │
      ▼
[Claude generates briefing] (background, ~10s)
      │
      ▼
[Briefing stored in Supabase briefings table]
      │
      ▼
[TTS audio generated for briefing text]
      │
      ▼
[PUSH NOTIFICATION SENT]:
  "🌅 Good morning! Your briefing is ready."
      │
      ▼
[User opens notification or app]
      │
      ▼
[BRIEFING PLAYS VIA TTS]:

"Good morning. It's Tuesday, March 24th.
 
 You have 3 meetings today: Team standup at 9 AM,
 Investor call at 2 PM, and a 1-on-1 with Priya at 5 PM.

 2 tasks are overdue: the client invoice and the Q3 report.
 I'd suggest handling those before the investor call.

 You have 4 unread emails that may need attention — 
 including a reply from Arjun about the contract.

 Your top 3 priorities today look like:
 1. Review and send the client invoice
 2. Prepare for the investor call
 3. Reply to Arjun about the contract.

 Shall I help with any of these now?"

      │
      ▼
<User responds?>
      │
      ├── YES, voice/text → Briefing transitions to live conversation
      │                     Alex handles the request directly
      │
      └── NO response → Briefing ends, chat history saved
                        User can replay later: [Play Again] button
```

#### 3.8.2 On-Demand Briefing

```
[TRIGGER]: "Hey Alex, give me my briefing"
      │
      ▼
<Today's briefing already generated?>
      │
      ├── YES → plays cached briefing immediately
      │
      └── NO → "Generating your briefing now — 
                 takes about 10 seconds..."
                 → data fetch + generate → play
```

#### 3.8.3 Error Path — Data Fetch Failure

```
[Calendar API fails during briefing generation]
      │
      ▼
Alex generates partial briefing with available data:
"Your briefing is ready, though I couldn't connect 
 to your calendar right now. 
 
 Based on tasks and emails:
 You have 3 pending tasks, including [overdue items]...
 
 I'll show your calendar events once I reconnect."
      │
      ▼
[Retry calendar API in background]
[Push update notification when calendar data loads]
```

---

### 3.9 Meeting Transcription Flow

**Trigger:** User says "Hey Alex, start transcribing" OR event starts and Alex sends pre-meeting prompt.
**Goal:** Full meeting transcript + summary + action items delivered within 2 minutes of meeting end.

#### 3.9.1 Happy Path — Full Flow

```
[TRIGGER]: "Hey Alex, start transcribing"
      │
      ▼
Alex: "Transcription started. I'll capture everything
       and send you a summary when you're done."
      │
      ▼
[Deepgram streaming activated — real-time transcription begins]
      │
      ▼
[UI: live transcript scrolls in real time]
      │
      ▼
[MEETING IN PROGRESS — audio streamed continuously]
      │
      ▼
[TRIGGER]: "Hey Alex, stop transcribing" 
           OR user taps [End Meeting] button
      │
      ▼
[Deepgram stream closed — final transcript saved]
      │
      ▼
[BACKGROUND JOB (BullMQ)]:
  │
  ├── Claude generates summary (key discussion points)
  ├── Claude extracts action items
  │     "1. Arjun to send revised contract by Friday
  │      2. Priya to review Q3 numbers by Wednesday
  │      3. Follow up with investor next week"
  └── Action items → auto-created as tasks (with owner = user)
      │
      ▼
[PUSH NOTIFICATION — ~90 seconds after meeting ends]:
"Meeting summary ready — 3 action items captured."
      │
      ▼
[User opens → sees]:
┌─────────────────────────────────────────────────────┐
│  Meeting Summary — March 24, 2026, 2:00 PM          │
│  Duration: 47 minutes                               │
│                                                     │
│  KEY POINTS                                         │
│  • Discussed Q3 revenue targets...                  │
│  • Contract revision agreed upon...                 │
│                                                     │
│  ACTION ITEMS                                       │
│  ☐ Send revised contract (Arjun, by Friday)         │
│  ☐ Review Q3 numbers (Priya, by Wednesday)          │
│  ☐ Follow up with investor (You, next week)         │
│                                                     │
│  [Share Summary] [View Full Transcript] [Edit]      │
└─────────────────────────────────────────────────────┘
      │
      ▼
<Share summary with attendees?>
      │
      ├── [Share Summary] → Alex: "Send to all meeting 
      │                      attendees?" [Yes] [Select people]
      │                      → emails sent with summary
      │
      └── [Dismiss] → Summary saved; tasks added to task list
```

#### 3.9.2 Pre-Meeting Prep (Proactive)

```
[10 MINUTES BEFORE CALENDAR EVENT]
[Automation Engine scheduled job fires]
      │
      ▼
<Event has attendees in contacts?>
      │
      YES
      ▼
Alex sends notification:
"Investor Call in 10 minutes.
 Last interaction with Arjun: March 18 (email re: contract)
 Relevant files: Q3_Report.pdf, Investor_Deck_v3.pdf
 [Open files] [Dismiss]"
```

---

### 3.10 Multi-Step Task Flow

**Trigger:** User gives a compound instruction requiring 3+ actions across different tools.
**Goal:** All steps executed in correct order, with real-time progress updates and graceful error handling.

#### 3.10.1 Happy Path — Full Multi-Step

```
[TRIGGER]: "Schedule a call with Priya for Thursday, 
            send her the contract on WhatsApp, and 
            remind me to prepare talking points 
            Wednesday night at 8 PM"
      │
      ▼
[Claude parses intent → creates Automation Plan]:
┌─────────────────────────────────────────────────────┐
│  PLAN: plan_abc123                                  │
│  Step A: get_calendar(Thursday) → find free slot    │
│  Step B: create_event(Priya, best slot) [← A]      │
│  Step C: search_files("contract")                   │
│  Step D: send_whatsapp(Priya, contract) [← C]      │
│  Step E: create_task("Prepare talking points",      │
│          due=Wednesday 8 PM) [independent]         │
└─────────────────────────────────────────────────────┘
      │
      ▼
Alex: "I'll handle all of that — working on it now."
[UI: progress tracker appears with 5 steps]
      │
      ▼
[STEP A EXECUTES]: get_calendar
  → Thursday free at 2 PM, 4 PM ✓
      │
      ▼
[STEP B EXECUTES]: create_event (uses Step A result)
  → "Call with Priya" Thursday 2 PM created
  → Calendar invite sent to Priya ✓
      │
      ▼
[STEPS C + E EXECUTE IN PARALLEL]:
  C: search_files("contract") 
     → "Client_Contract_Priya.pdf" found ✓
  E: create_task("Prepare talking points", Wed 8 PM)
     → Task created ✓
      │
      ▼
[STEP D EXECUTES]: send_whatsapp (uses Step C result)
  → Contract PDF sent to Priya on WhatsApp ✓
      │
      ▼
[ALL STEPS COMPLETE]
      │
      ▼
Alex: "All done:
       ✓ Call with Priya booked — Thursday at 2 PM
       ✓ Contract sent to Priya on WhatsApp
       ✓ Reminder set — Wednesday at 8 PM to prep talking points"
      │
      ▼
[COMPLETE ✓] — all actions logged
```

#### 3.10.2 Partial Failure Path

```
[STEP B FAILS]: Calendar API timeout while creating event
      │
      ▼
[Retry B × 2 — still fails]
      │
      ▼
[Step D depends on B — paused]
[Steps C and E continue independently]
      │
      ▼
Alex (mid-execution update):
"Quick update — I had trouble booking the calendar slot for 
 Priya (Google Calendar isn't responding). 
 
 I've completed:
 ✓ Contract sent to Priya on WhatsApp
 ✓ Reminder set for Wednesday at 8 PM
 ✗ Meeting not booked yet
 
 Should I try booking the meeting again?"
      │
      ├── [Retry] → Step B retried → succeeds → plan_abc123 completes
      │
      └── [Skip] → plan marked partially complete, user notified
```

---

## 4.0 Edge Cases & Error Handling

### 4.1 Master Error Handling Matrix

| Error Type | When It Occurs | Alex's Response | Recovery Path |
|------------|---------------|-----------------|---------------|
| **Mic not detected** | Voice command attempt | "I can't access your microphone. Check app permissions." | Deep-link to device settings |
| **STT failure (no transcript)** | Deepgram drops connection | "I didn't catch that — try again or type it." | Mic reactivates; text fallback offered |
| **Ambiguous intent** | Unclear command | Asks ONE clarifying question | User clarifies; flow resumes |
| **Contact not found** | Unknown name in command | "I don't have [name] in your contacts. Can you give me their email/number?" | User provides → stored in contacts |
| **Multiple contacts match** | Common name | Lists matches, asks user to pick | User selects → action proceeds |
| **File not found** | Search returns < 0.5 score | "No matching file found. Try rephrasing or re-indexing." | Rephrase / trigger re-index |
| **Email send failure** | Gmail API error | "Couldn't send — save as draft instead?" | Retry or save draft |
| **WhatsApp 24h window expired** | Outside window | Suggests email or template | User chooses alternative |
| **WhatsApp file too large** | > 100MB file | Offers Drive link or email alternative | User picks alternative |
| **Calendar conflict** | Event already booked at slot | Shows conflict, suggests alternatives | User picks new slot |
| **Claude API timeout** | LLM takes > 5s | "Give me a moment…" spinner → retry × 2 | Queue request; notify when done |
| **Google auth expired** | OAuth token revoked | "Your Google account needs to be reconnected." | Re-auth flow from Settings |
| **WhatsApp API rate limit** | Too many messages sent | "I need to wait a minute before sending more WhatsApp messages." | Auto-retry after cooldown |
| **Automation step fails** | Mid-plan tool error | Reports partial completion; asks to retry failed step | Retry individual step |
| **No internet connection** | Network offline | "I'm offline. Voice and text work locally; actions need internet." | Auto-resumes when reconnected |
| **Briefing generation fails** | All APIs down at 7 AM | Partial briefing with available data + error note | Retry on first user open |

### 4.2 Graceful Degradation by Feature

```
FULL CAPABILITIES (All connected)
    Gmail ✓ + WhatsApp ✓ + Drive ✓ + Calendar ✓
    → All 11 features fully operational

─────────────────────────────────────────────
PARTIAL: Gmail only (no WhatsApp)
    → File search ✓, Email ✓, Calendar ✓
    → WhatsApp flows → redirect to email

─────────────────────────────────────────────
PARTIAL: No Google Drive (only Gmail + Calendar)
    → Communication ✓, Calendar ✓
    → File search → "Drive not connected. Connect in Settings."

─────────────────────────────────────────────
MINIMAL: No internet
    → Voice recognition: ✗ (requires Deepgram)
    → Text input: ✓ (queued, executes on reconnect)
    → Local task list: ✓ (SQLite)
    → Briefing: read cached version only
```

---

## 5.0 Confirmation & Permission Flows

### 5.1 Auto-Act vs. Ask-First Rules

The following matrix defines exactly when Alex acts immediately and when it pauses for user confirmation.

| Action | Auto-Act | Ask First | Condition |
|--------|----------|-----------|-----------|
| Send email (known contact) | ✓ | | Contact emailed > 3 times |
| Send email (new/rare contact) | | ✓ | First time or < 3 prior emails |
| Send WhatsApp (known contact) | ✓ | | In 24h window; contact messaged > 5 times |
| Send WhatsApp (new contact) | | ✓ | Always |
| Send with file attachment | | ✓ | Always — confirm correct file |
| Create calendar event (solo) | ✓ | | No attendees |
| Create calendar event (with attendees) | | ✓ | Invites will be sent externally |
| Reschedule event | | ✓ | Always — affects attendees |
| Delete event | | ✓ | Always — irreversible |
| Create task / reminder | ✓ | | Always auto — non-destructive |
| Mark task complete | ✓ | | If clearly named match |
| Start meeting transcription | ✓ | | User explicitly triggered |
| Share meeting summary externally | | ✓ | Sending to attendees |
| Run multi-step automation | | ✓ | If plan includes ≥1 external send |
| Set memory preference | ✓ | | Auto-learns from behavior |
| Override/delete memory | | ✓ | User must explicitly confirm change |

### 5.2 Confirmation UI Patterns

#### Standard Confirm (Inline)
```
Alex: "Sending this email to Priya at priya@consulting.in —
       shall I go ahead?"

  [Yes, send]     [Edit first]     [Cancel]
```

#### File Confirm (With Preview)
```
Alex: "Attaching 'Client_Contract_Priya.pdf' — is this the 
       right file?"

  [Yes, attach it]     [Find a different file]
```

#### Multi-Action Preview (Before Automation)
```
Alex: "Here's my plan — shall I go ahead with all of this?

  1. ☐ Book call with Priya — Thursday 2 PM
  2. ☐ Send contract to Priya on WhatsApp
  3. ☐ Set reminder — Wednesday 8 PM

  [Do all of this]     [Edit plan]     [Cancel]"
```

#### Destructive Action Confirm
```
Alex: "Delete 'Investor Update' from your calendar on 
       Tuesday? This will cancel the meeting and notify 
       all attendees."

  [Yes, delete it]     [Keep it]"
```

### 5.3 Permission Escalation Flow

```
[ALEX WANTS TO DO SOMETHING IT HASN'T DONE BEFORE]
e.g., "Send files to an external contact for the first time"
      │
      ▼
Alex: "Just to confirm — I'll be sending files to people
       outside your usual contacts. Is that okay?"
  [Yes, always allow this]   [Yes, just this once]   [No]
      │
      ▼
[Choice stored in memory as permission preference]
```

---

## 6.0 Open Questions

| # | Question | Impact | Needed By |
|---|----------|--------|-----------|
| OQ-UF-1 | Should Alex show a live transcript feed on screen during voice commands, or only show the final response? Live transcription is more transparent but may feel noisy. | UX design of voice mode screen | Before frontend build |
| OQ-UF-2 | For multi-step plans, should Alex always preview the full plan and ask for confirmation, or only ask when a plan contains external sends? | Confirmation flow design § 5.1 | Before automation engine build |
| OQ-UF-3 | When meeting transcription is active and the user gives a voice command ("Hey Alex, pause"), how does Alex distinguish it from meeting audio? | Voice layer design (separate STT channel needed?) | Before transcription feature build |
| OQ-UF-4 | Should the morning briefing play automatically on app open, or only on explicit user request / notification tap? | Briefing UX; affects retention | Before briefing feature build |
| OQ-UF-5 | What happens if the user is mid-conversation and a scheduled job fires (e.g., briefing, overdue task alert)? Queue or interrupt? | Notification + conversation state management | Before scheduling build |
| OQ-UF-6 | What is the undo/rollback experience? If Alex sends an email by mistake, can the user say "Hey Alex, undo that"? Gmail supports draft recall, but sent messages cannot be recalled after delivery. | User trust and error recovery | Before communication layer build |

---

## 7.0 Next Steps

| # | Action | Owner | Dependency |
|---|--------|-------|-----------|
| NS-1 | Resolve OQ-UF-1, OQ-UF-2, OQ-UF-4 — these directly affect screen designs | Product | Before Document 4 (Feature List) |
| NS-2 | Hand USER_FLOW.md to UX designer to produce wireframes for all 10 flows | UX Designer | After this document |
| NS-3 | Map all flows in this document to API endpoints defined in SYSTEM_DESIGN.md § 6 | Engineering | Before development |
| NS-4 | Add edge cases from § 4.1 matrix to QA test plan | QA | Before testing phase |
| NS-5 | Define all confirmation copy (the exact words Alex uses for confirms) in AI Instructions Document (Doc 7) | Product + AI | During Doc 7 |
| NS-6 | Begin **Feature List Document** (Document 4) — complete feature breakdown with acceptance criteria | Product | After USER_FLOW sign-off |

---

*All flows in this document are based on PRD.md user stories and SYSTEM_DESIGN.md architecture. Any change to either upstream document must trigger a review of affected flows.*

---
**Document Control**

| Field | Value |
|-------|-------|
| Document Name | USER_FLOW.md |
| Version | v1.0 |
| Status | Draft |
| Created | 24 March 2026 |
| Last Updated | 24 March 2026 |
| References | GOAL.md, PRD.md v1.0, SYSTEM_DESIGN.md v1.0 |
