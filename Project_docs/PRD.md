# PRD — Alex: Personal AI Operating System
**Version:** v1.0  
**Date:** 24 March 2026  
**Status:** Draft  
**Source of Truth:** GOAL.md  
**Author:** Alex Project Team

---

## Table of Contents

1. [Purpose & Scope](#10-purpose--scope)
2. [Problem Statement](#20-problem-statement)
3. [Goals & Success Metrics](#30-goals--success-metrics)
4. [User Personas](#40-user-personas)
5. [Core Features](#50-core-features)
6. [User Stories](#60-user-stories)
7. [Constraints & Assumptions](#70-constraints--assumptions)
8. [Out of Scope](#80-out-of-scope)
9. [Open Questions](#90-open-questions)
10. [Next Steps](#100-next-steps)

---


## 1.0 Purpose & Scope

### 1.1 Purpose

This Product Requirements Document defines the functional and non-functional requirements for **Alex**, a personal AI Operating System designed to serve as an intelligent, autonomous, and continuously learning assistant. Alex is built to understand, search, decide, act, communicate, and automate real-world tasks on behalf of its user.

This document serves as the primary reference for the design, development, and validation of Alex v1.0. All downstream technical documents — including the System Design Document, User Flow Document, Feature List, Tech Stack Requirements, Security Document, and AI Instructions Document — must remain consistent with the decisions recorded here.

### 1.2 Scope

Alex v1.0 covers the following domains:

- Voice and text-based conversational assistance
- Intelligent file search and automated delivery
- Autonomous multi-step task execution
- Communication via email and WhatsApp
- Calendar management and scheduling
- Meeting transcription and summarization
- Task and reminder management
- Intelligent decision-making and intent resolution
- Smart suggestions and recommendations
- Memory, personalization, and behavioral learning
- Daily wake-up briefings

### 1.3 Hybrid AI Architecture Scope

Alex is designed to operate in **two modes**:

- **Default (Free/Local) Mode:** All core features must be fully functional using free or locally hosted AI models. No paid API dependency for core operation.
- **Upgrade (Paid API) Mode:** Optional integration with paid APIs (e.g., OpenAI, Claude) that enhances performance but does not alter or replace core functionality. Paid APIs are performance boosters only.

This hybrid model must be reflected consistently across all seven documentation artifacts.

---

## 2.0 Problem Statement

### 2.1 Problems Alex Solves

Modern professionals and individuals face a fragmented digital life. They manage multiple applications — calendars, email clients, messaging apps, file systems, task managers — none of which communicate with each other intelligently. The result is cognitive overload, missed tasks, poor information retrieval, and wasted time on repetitive actions.

Specifically, Alex addresses the following pain points:

- **Information fragmentation:** Files, emails, calendar events, and messages live in separate silos. Finding the right information at the right moment requires manual effort.
- **Repetitive communication tasks:** Composing emails, sending files via WhatsApp, and following up on meetings consumes time that could be automated.
- **Scheduling inefficiency:** Coordinating availability, suggesting meeting times, and managing reminders remains largely manual.
- **Meeting blind spots:** Valuable information shared in meetings is lost due to the absence of real-time transcription and summarization.
- **No unified assistant layer:** Existing tools are reactive and single-function. There is no intelligent layer that connects intent to action across platforms.
- **High cost of AI assistants:** Most capable AI solutions require paid subscriptions, excluding users who cannot or do not want to incur recurring costs for core functionality.

### 2.2 Target User

Alex is designed for the **individual professional** — someone who manages significant information flow, handles communication across multiple channels, attends recurring meetings, and needs consistent productivity support without the overhead of managing multiple tools.

The primary target user profile:

- Works independently or in a small team
- Manages a high volume of communication (email, messaging)
- Relies heavily on scheduling and calendar coordination
- Needs quick access to files and documents
- Values automation but requires control and transparency
- Is cost-conscious and prefers a free-first approach with optional paid upgrades

---

## 3.0 Goals & Success Metrics

### 3.1 Primary Goals

| # | Goal | Description |
|---|------|-------------|
| G1 | Full functionality in free mode | All 11 core capabilities must work without any paid API dependency |
| G2 | End-to-end task automation | Alex must complete multi-step tasks from a single voice or text command |
| G3 | Accurate intent understanding | Alex must correctly resolve user intent across ambiguous or multi-part commands |
| G4 | Seamless communication | Alex must send emails and WhatsApp messages reliably, with correct attachments |
| G5 | Persistent memory | Alex must learn and retain user preferences across sessions |
| G6 | Voice-first interaction | Alex must support real-time voice input and output as the primary interaction mode |
| G7 | Graceful upgrade path | Switching between free and paid modes must be seamless and non-disruptive |

### 3.2 Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Intent accuracy | ≥ 90% correct intent classification | Logged command vs. executed action comparison |
| Task completion rate | ≥ 85% end-to-end without user re-prompt | Session logs |
| Voice response latency | < 2 seconds for short commands | Response time measurement |
| File search success rate | ≥ 95% correct file retrieved | Search result vs. user selection |
| Email / WhatsApp delivery rate | 100% | Delivery confirmation logs |
| Calendar booking accuracy | ≥ 98% correct time slot booked | Calendar entry validation |
| User re-engagement (daily briefing) | ≥ 70% of active users engage daily | Session open rate |
| Free mode uptime | 100% core features functional without paid APIs | Feature availability audit |
| Memory retention accuracy | ≥ 80% preference recall after 7 days | Preference test against stored data |

---

## 4.0 User Personas

### 4.1 Persona 1 — Arjun, The Independent Consultant

**Age:** 34
**Location:** Delhi, India
**Role:** Independent business consultant managing 5–8 clients simultaneously

**Background:** Arjun handles proposal writing, client communication, file delivery, and meeting scheduling entirely on his own. He works across email, WhatsApp, and Google Calendar and spends a disproportionate amount of time on administrative tasks.

**Needs:**
- Quick file search and WhatsApp delivery without navigating folders manually
- Automated email drafting and sending for routine communications
- Meeting summaries with extracted action items
- A daily briefing to orient himself each morning

**Pain Points:**
- Frequently forgets follow-ups after meetings
- Wastes 30–45 minutes daily on file retrieval and forwarding tasks
- Cannot afford enterprise AI tools but needs equivalent productivity

**How Alex Helps:** Alex automates file delivery, sends follow-up emails post-meeting, provides daily briefings with pending tasks, and operates entirely in free mode — matching his budget constraints.

---

### 4.2 Persona 2 — Priya, The Startup Founder

**Age:** 29
**Location:** Bangalore, India
**Role:** Co-founder of an early-stage startup with a 5-person team

**Background:** Priya juggles product decisions, investor communications, team scheduling, and operational tasks. She moves fast and needs an assistant that can keep up without requiring configuration for each task.

**Needs:**
- Multi-step task execution from a single command
- Smart scheduling suggestions when coordinating with investors and team members
- Meeting transcription and action item extraction
- Proactive suggestions on follow-ups and priorities

**Pain Points:**
- Too many tools create context-switching fatigue
- Manually tracking meeting outcomes and action items is error-prone
- Needs AI capability but is cautious about recurring API costs during early-stage

**How Alex Helps:** Alex provides a unified interface for scheduling, meeting summaries, and task tracking. Priya can start in free mode and selectively activate paid API upgrades when business scale justifies the cost.

---

### 4.3 Persona 3 — Rohan, The Remote Knowledge Worker

**Age:** 26
**Location:** Pune, India
**Role:** Research analyst working remotely for a mid-sized firm

**Background:** Rohan attends multiple video calls daily, produces research reports, and must stay current on deliverables across several ongoing projects. He finds it difficult to stay organized without a reliable system.

**Needs:**
- Meeting transcription and summary generation
- Reminder and task tracking integrated with his calendar
- File search and delivery by voice to save time
- Preference learning so Alex adapts to his working patterns

**Pain Points:**
- Important meeting details are often lost or scattered across notes
- Frequently misses reminders because they live in separate apps
- Wants an assistant that improves with use, not one that requires constant instruction

**How Alex Helps:** Alex transcribes meetings, generates structured summaries, tracks reminders, and personalizes its behavior over time — reducing Rohan's administrative burden substantially.

---

## 5.0 Core Features

### 5.1 Feature Priority Table

The following table lists all 11 capabilities from GOAL.md, with priority classification for v1.0.

| # | Feature | Priority | Notes |
|---|---------|----------|-------|
| F1 | Conversational Voice & Text Assistance | Must Have | Primary interaction layer; required in free mode |
| F2 | Intelligent File Search + Action | Must Have | Core value proposition; semantic search required |
| F3 | Autonomous Task Execution | Must Have | Multi-step automation is foundational |
| F4 | Communication (Email + WhatsApp) | Must Have | Direct user value; high usage frequency |
| F5 | Calendar & Scheduling | Must Have | Core productivity feature |
| F6 | Meeting Copilot | Should Have | High value but dependent on audio integration |
| F7 | Task & Reminder Management | Must Have | Required for daily utility |
| F8 | Decision Making & Intent Understanding | Must Have | Underlies all other features |
| F9 | Smart Suggestions & Recommendations | Should Have | Enhances experience; not blocking |
| F10 | Memory & Personalization | Should Have | Required for long-term engagement; partial in v1.0 |
| F11 | Wake-Up Briefing | Should Have | High engagement value; depends on F5, F7, F10 |

### 5.2 Priority Definitions

- **Must Have:** Required for v1.0 launch. Alex cannot be considered functional without these.
- **Should Have:** Planned for v1.0 but may be delivered in a later sub-version if constraints require deferral.
- **Nice to Have:** Valuable but not blocking. Targeted for v1.1 or later.

---

## 6.0 User Stories

### 6.1 F1 — Conversational Voice & Text Assistance

**US-1.1:** As a consultant, I want to speak a command naturally and have Alex understand my intent, so that I do not need to learn specific syntax or keywords.

**US-1.2:** As a remote worker, I want to switch between voice and text input without losing context, so that I can use Alex in both quiet and noisy environments.

**US-1.3:** As a startup founder, I want Alex to maintain context across a multi-turn conversation, so that I do not need to repeat background information with each follow-up question.

**US-1.4:** As a user, I want Alex to detect a wake word and begin listening, so that I can activate it hands-free during busy moments.

---

### 6.2 F2 — Intelligent File Search + Action

**US-2.1:** As a consultant, I want to say "Send Priya the Q1 proposal" and have Alex find the correct file and deliver it via WhatsApp, so that I can complete the task without navigating to the file manually.

**US-2.2:** As a knowledge worker, I want file search to be case-insensitive and semantically aware, so that I can find files even when I do not remember the exact filename.

**US-2.3:** As a user, I want Alex to confirm before sending a file if it is ambiguous which file I meant, so that I do not accidentally send the wrong document.

**US-2.4:** As a startup founder, I want Alex to index new files automatically as they are added, so that search results remain current without manual updates.

---

### 6.3 F3 — Autonomous Task Execution

**US-3.1:** As a consultant, I want to give Alex a multi-step instruction such as "Find the contract, summarize it, and email it to the client" and have it execute all steps in sequence, so that I can delegate complex workflows with a single command.

**US-3.2:** As a user, I want Alex to ask for confirmation before irreversible actions such as sending an email or deleting a file, so that I maintain control over consequential steps.

**US-3.3:** As a startup founder, I want Alex to handle errors gracefully and report what succeeded and what failed, so that I can act on incomplete workflows without confusion.

**US-3.4:** As a user, I want to review a task plan before Alex executes it, so that I can correct misunderstandings before they result in real actions.

---

### 6.4 F4 — Communication (Email + WhatsApp)

**US-4.1:** As a consultant, I want to say "Email Rohan the meeting summary" and have Alex compose and send a professional email, so that I can dispatch communications without opening my email client.

**US-4.2:** As a startup founder, I want Alex to resolve contact names intelligently — including partial names and nicknames — so that I do not need to specify full names or email addresses every time.

**US-4.3:** As a user, I want Alex to adjust the tone of a message (formal vs. casual) based on my instruction, so that communications are contextually appropriate.

**US-4.4:** As a remote worker, I want Alex to attach the correct file to an email automatically when I reference it by description, so that I do not need to locate and attach it manually.

---

### 6.5 F5 — Calendar & Scheduling

**US-5.1:** As a startup founder, I want to say "Book a one-hour meeting with Priya next Tuesday afternoon" and have Alex find an available slot and create the calendar event, so that scheduling requires no manual calendar interaction.

**US-5.2:** As a consultant, I want Alex to check my availability before confirming any meeting, so that double-bookings are prevented automatically.

**US-5.3:** As a remote worker, I want Alex to suggest two or three available time slots when coordinating with multiple participants, so that scheduling negotiations are faster.

**US-5.4:** As a user, I want Alex to send calendar invitations to all participants automatically after booking a meeting, so that no follow-up coordination is required.

---

### 6.6 F6 — Meeting Copilot

**US-6.1:** As a remote worker, I want Alex to transcribe my meetings in real time, so that I have a searchable record of every discussion.

**US-6.2:** As a startup founder, I want Alex to generate a structured meeting summary with key decisions and action items, so that I can share outcomes with my team immediately after the meeting ends.

**US-6.3:** As a consultant, I want Alex to identify which action items are assigned to me versus others, so that I can prioritize my own follow-ups clearly.

**US-6.4:** As a user, I want Alex to automatically add extracted action items as tasks or reminders, so that nothing from a meeting is forgotten.

---

### 6.7 F7 — Task & Reminder Management

**US-7.1:** As a consultant, I want to say "Remind me to follow up with Arjun tomorrow at 10 AM" and have Alex set the reminder without any additional steps, so that task capture is frictionless.

**US-7.2:** As a remote worker, I want Alex to maintain a running task list that I can query at any time, so that I always know what is pending.

**US-7.3:** As a startup founder, I want Alex to escalate overdue reminders proactively rather than silently expiring them, so that nothing slips through.

---

### 6.8 F8 — Decision Making & Intent Understanding

**US-8.1:** As a user, I want Alex to correctly interpret multi-intent commands such as "Search for the contract, summarize it, and send it," so that I can issue compound instructions naturally.

**US-8.2:** As a consultant, I want Alex to ask a single clarifying question when my instruction is ambiguous, rather than refusing to act, so that the workflow continues with minimal friction.

**US-8.3:** As a user, I want Alex to select the correct action from a set of available capabilities based on my intent, so that I do not need to specify which tool to use.

---

### 6.9 F9 — Smart Suggestions & Recommendations

**US-9.1:** As a consultant, I want Alex to proactively suggest sending a follow-up email after a meeting if no follow-up has been sent within 24 hours, so that I do not miss client touchpoints.

**US-9.2:** As a startup founder, I want Alex to recommend the most relevant files or contacts when I begin composing a communication, so that I spend less time searching.

**US-9.3:** As a user, I want Alex to surface intelligent insights — such as a pending task that aligns with an upcoming meeting — so that I can act on connections I might otherwise miss.

---

### 6.10 F10 — Memory & Personalization

**US-10.1:** As a returning user, I want Alex to remember my preferred communication style and apply it automatically, so that I do not need to re-specify preferences every session.

**US-10.2:** As a consultant, I want Alex to learn which contacts I communicate with most frequently and prioritize them in suggestions, so that resolution is faster over time.

**US-10.3:** As a user, I want to be able to review and correct what Alex has learned about me, so that I maintain transparency and control over my personalization data.

---

### 6.11 F11 — Wake-Up Briefing

**US-11.1:** As a consultant, I want Alex to deliver a concise morning briefing covering my schedule, pending tasks, and any unread priority emails, so that I can start my day fully oriented.

**US-11.2:** As a startup founder, I want the briefing to include project status updates and any flagged items from the previous day, so that I stay on top of ongoing work without manual review.

**US-11.3:** As a remote worker, I want to receive the briefing via voice on request, so that I can consume it hands-free while preparing for the day.

---

## 7.0 Constraints & Assumptions

### 7.1 Technical Constraints

| Constraint | Detail |
|-----------|--------|
| Free mode must be fully functional | No core feature may depend on a paid API as its only implementation path |
| Paid APIs are optional upgrades only | OpenAI, Anthropic Claude, and similar services may only be activated by user choice |
| Mode switching must be non-disruptive | Switching between free and paid modes must not interrupt active tasks or corrupt stored data |
| Voice processing must support offline capability | At minimum, wake word detection must function without an internet connection |
| File system access is local by default | Alex must not require cloud file storage as a prerequisite for file search |
| Multi-platform communication | Email and WhatsApp integrations must work across the platforms users already use |

### 7.2 Budget Constraints

- Alex's core system must have zero recurring API cost in free mode.
- Paid API costs, when the upgrade mode is activated, are borne by the user and must be clearly disclosed before activation.
- Development tooling and hosting in v1.0 should prioritize open-source and self-hostable solutions.

### 7.3 Time Constraints

- Documentation phase (all 7 documents): to be completed before development begins.
- v1.0 feature scope is fixed by this PRD. New feature requests will be deferred to v1.1.

### 7.4 Assumptions

- Users have a working device (desktop or mobile) capable of running a local AI model.
- WhatsApp integration is possible through available APIs or automation bridges (e.g., WhatsApp Business API or third-party wrappers).
- Users consent to local storage of memory and preference data.
- Internet connectivity is available for communication features (email, WhatsApp), though voice and file search may function offline.
- The primary language for v1.0 is English, with multilingual support deferred to a later version.

---

## 8.0 Out of Scope

The following capabilities are explicitly excluded from Alex v1.0:

| Item | Reason for Exclusion |
|------|----------------------|
| Multilingual voice support | Adds significant NLP complexity; deferred to v1.1 |
| Native mobile application | v1.0 targets desktop/web; mobile is a separate platform effort |
| Autonomous financial transactions | Risk and compliance considerations; requires separate security review |
| Vision / image understanding | Advanced capability; deferred pending infrastructure readiness |
| Multi-agent orchestration | Complex coordination layer; planned for a future version |
| Team or multi-user accounts | v1.0 is a single-user system; collaboration features deferred |
| CRM or third-party SaaS integrations | Specific integrations (e.g., Salesforce, Notion) deferred to v1.1 |
| Cloud file storage management | Alex operates on local file systems only in v1.0 |
| Emotion-aware voice response | Emotion detection is a future enhancement |
| Automated upselling of paid APIs to the user | Alex must never push paid mode without explicit user initiation |

---

## 9.0 Open Questions

| # | Question | Owner | Target Resolution Date |
|---|----------|-------|------------------------|
| OQ-1 | Which local AI model(s) will serve as the default engine in free mode? (e.g., LLaMA, Mistral, Phi) | Tech Lead | Before System Design Document |
| OQ-2 | What is the WhatsApp integration mechanism? (Business API, Twilio, unofficial bridge?) | Engineering | Before Tech Stack Document |
| OQ-3 | How will meeting transcription be handled without a paid service? (e.g., Whisper local) | Engineering | Before Feature List Document |
| OQ-4 | What is the memory storage format? (local SQLite, flat JSON, vector store?) | Architecture | Before System Design Document |
| OQ-5 | How will wake word detection be implemented without cloud dependency? | Engineering | Before System Design Document |
| OQ-6 | What is the exact scope of calendar integration? (Google Calendar only, or multi-provider?) | Product | Before User Flow Document |
| OQ-7 | What security model governs access to stored memory and communication credentials? | Security Lead | Before Security Document |
| OQ-8 | Is the v1.0 delivery target desktop-only, or also web-based? | Product | Before System Design Document |

---

## 10.0 Next Steps

Upon approval of this PRD, the following actions are to be taken in sequence:

1. **Resolve Open Questions OQ-1 through OQ-8** before proceeding with any technical document.
2. **Author the System Design Document (v1.0)**, covering architecture, data flows, component design, and the hybrid AI model implementation. This document must reference this PRD as its requirement source.
3. **Author the User Flow Document (v1.0)**, mapping all major user journeys from intent to action completion.
4. **Author the Feature List Document (v1.0)**, enumerating every feature with acceptance criteria, dependencies, and delivery estimates.
5. **Author the Tech Stack Requirements Document (v1.0)**, specifying all tools, frameworks, models, and services required — with clear free-mode vs. paid-mode designation.
6. **Author the Security Document (v1.0)**, covering data handling, authentication, access control, and action permission models.
7. **Author the AI Instructions Document (v1.0)**, defining how Alex's AI layer is prompted, configured, and constrained to produce consistent and safe behavior.

All seven documents must remain internally consistent with this PRD and with each other. Any change to a decision made in this document must be recorded as a version update and communicated to all document owners.

---

*Document maintained by the Alex Build Team. Version history to be tracked in a separate changelog.*
