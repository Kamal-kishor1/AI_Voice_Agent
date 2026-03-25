# Database Design Document

**File name:** DATABASE.md
**Version:** v1.0
**Date:** 24 March 2026

---

## 1.0 Purpose & Scope

This document defines the complete database architecture for Antigravity (Alex AI Voice Assistant). It covers schema design, relationships, indexing strategies, migration workflows, query patterns, backup policies, and data retention rules. It is intended as a definitive reference for backend engineers, DBAs, and DevOps teams to implement, maintain, and scale the persistence layer.

---

## 2.0 Database Overview

### Database technology chosen

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Primary Relational | **PostgreSQL 16** | Users, tasks, calendars, contacts, conversations, audit logs |
| Vector Store | **pgvector** (PostgreSQL extension) | Semantic search embeddings for files, messages, and memory |
| Cache / Broker | **Redis 7** | Session cache, rate limiting, Pub/Sub, task queues |
| File Metadata | PostgreSQL | Metadata only; actual files stored in S3-compatible object storage |

### SQL vs NoSQL decision and why

**Decision: SQL (PostgreSQL)**

| Factor | SQL (PostgreSQL) | NoSQL (MongoDB) | Verdict |
|--------|------------------|-----------------|---------|
| Data integrity | ACID transactions, FK constraints | Eventual consistency | ✅ SQL |
| Complex queries | JOINs, CTEs, window functions | Limited aggregation pipeline | ✅ SQL |
| Schema evolution | Alembic migrations, ALTER TABLE | Schema-less (advantage for early prototyping) | ✅ SQL |
| Vector search | pgvector native extension | Requires separate service | ✅ SQL |
| Ecosystem fit | SQLAlchemy + FastAPI mature | Motor/Beanie less mature | ✅ SQL |

**Rationale:** Alex requires strong relational integrity (users → conversations → messages → actions), complex temporal queries (calendar scheduling, task deadlines), and vector similarity search. PostgreSQL with pgvector unifies all three under one engine, reducing operational overhead.

### Single vs multiple database strategy

**Strategy: Single PostgreSQL instance with logical schema separation**

- `public` schema — Core application tables
- `vector` schema — Embedding tables (pgvector)
- `audit` schema — Immutable audit/log tables

Redis operates as a separate, stateless caching layer. No data in Redis is authoritative; it can be rebuilt from PostgreSQL at any time.

---

## 3.0 Entity Relationship Diagram

```text
┌──────────┐       1:N       ┌──────────────────┐
│  users   │────────────────▶│  conversations   │
└──────────┘                 └──────────────────┘
     │                              │
     │ 1:N                          │ 1:N
     ▼                              ▼
┌──────────┐                 ┌──────────────────┐
│ contacts │                 │    messages      │
└──────────┘                 └──────────────────┘
     │                              │
     │                              │ 1:N
     │                              ▼
     │                       ┌──────────────────┐
     │                       │  action_logs     │
     │                       └──────────────────┘
     │
┌──────────┐       1:N       ┌──────────────────┐
│  users   │────────────────▶│  calendar_events │
└──────────┘                 └──────────────────┘
     │
     │ 1:N
     ▼
┌──────────┐       1:N       ┌──────────────────┐
│  users   │────────────────▶│     tasks        │
└──────────┘                 └──────────────────┘
     │
     │ 1:N
     ▼
┌──────────┐       1:N       ┌──────────────────┐
│  users   │────────────────▶│   reminders      │
└──────────┘                 └──────────────────┘
     │
     │ 1:N
     ▼
┌──────────┐                 ┌──────────────────┐
│  users   │────────────────▶│   files          │
└──────────┘    1:N          └──────────────────┘
     │                              │
     │ 1:N                          │ 1:1
     ▼                              ▼
┌──────────────┐             ┌──────────────────┐
│ user_prefs   │             │ file_embeddings  │
└──────────────┘             └──────────────────┘
     │
     │
┌──────────┐       1:N       ┌──────────────────┐
│  users   │────────────────▶│ meeting_summaries│
└──────────┘                 └──────────────────┘
```

### Cardinality Summary

| Parent | Child | Relationship |
|--------|-------|-------------|
| `users` | `conversations` | 1:N |
| `conversations` | `messages` | 1:N |
| `messages` | `action_logs` | 1:N |
| `users` | `contacts` | 1:N |
| `users` | `calendar_events` | 1:N |
| `users` | `tasks` | 1:N |
| `users` | `reminders` | 1:N |
| `users` | `files` | 1:N |
| `files` | `file_embeddings` | 1:1 |
| `users` | `user_preferences` | 1:N |
| `users` | `meeting_summaries` | 1:N |

---

## 4.0 Schema Design

### 4.1 `users`

**Purpose:** Stores registered user accounts and authentication data.

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Unique user identifier |
| `email` | VARCHAR(255) | ✅ | — | UNIQUE, NOT NULL | Login email |
| `password_hash` | VARCHAR(255) | ✅ | — | NOT NULL | Bcrypt hashed password |
| `full_name` | VARCHAR(150) | ✅ | — | NOT NULL | Display name |
| `avatar_url` | TEXT | ❌ | `NULL` | — | Profile image URL |
| `role` | VARCHAR(20) | ✅ | `'user'` | CHECK IN ('admin','user') | Access role |
| `is_active` | BOOLEAN | ✅ | `TRUE` | — | Soft active flag |
| `last_login_at` | TIMESTAMPTZ | ❌ | `NULL` | — | Last successful login |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Record creation |
| `updated_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Last modification |
| `deleted_at` | TIMESTAMPTZ | ❌ | `NULL` | — | Soft delete timestamp |

**Example Row:**

| id | email | full_name | role | is_active | created_at |
|----|-------|-----------|------|-----------|------------|
| `a1b2c3d4-...` | kamal@example.com | Kamal Kishor | user | true | 2026-03-24T10:00:00Z |

---

### 4.2 `conversations`

**Purpose:** Groups messages into a single conversational thread between a user and Alex.

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Conversation identifier |
| `user_id` | UUID | ✅ | — | FK → `users.id`, NOT NULL | Owner of conversation |
| `title` | VARCHAR(255) | ❌ | `'New Conversation'` | — | Auto-generated or user-set title |
| `status` | VARCHAR(20) | ✅ | `'active'` | CHECK IN ('active','archived','deleted') | Lifecycle state |
| `context_summary` | TEXT | ❌ | `NULL` | — | LLM-generated running summary for context window |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Thread start time |
| `updated_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Last message time |

**Example Row:**

| id | user_id | title | status | created_at |
|----|---------|-------|--------|------------|
| `e5f6a7b8-...` | `a1b2c3d4-...` | "Schedule team sync" | active | 2026-03-24T10:05:00Z |

---

### 4.3 `messages`

**Purpose:** Individual messages within a conversation (user utterances and AI responses).

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Message identifier |
| `conversation_id` | UUID | ✅ | — | FK → `conversations.id`, NOT NULL | Parent conversation |
| `role` | VARCHAR(20) | ✅ | — | CHECK IN ('user','assistant','system') | Sender role |
| `content` | TEXT | ✅ | — | NOT NULL | Message text content |
| `audio_url` | TEXT | ❌ | `NULL` | — | S3 URL to original voice recording |
| `token_count` | INTEGER | ❌ | `NULL` | — | LLM tokens consumed |
| `intent` | VARCHAR(100) | ❌ | `NULL` | — | Detected intent label |
| `confidence` | FLOAT | ❌ | `NULL` | CHECK (0.0–1.0) | Intent confidence score |
| `metadata` | JSONB | ❌ | `'{}'` | — | Flexible extra data (tool calls, etc.) |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Timestamp |

**Example Row:**

| id | conversation_id | role | content | intent | confidence |
|----|----------------|------|---------|--------|------------|
| `m1n2o3p4-...` | `e5f6a7b8-...` | user | "Book a meeting with Raj tomorrow at 3 PM" | schedule_meeting | 0.96 |

---

### 4.4 `action_logs`

**Purpose:** Tracks every autonomous action Alex executes on behalf of the user.

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Log entry ID |
| `message_id` | UUID | ✅ | — | FK → `messages.id`, NOT NULL | Triggering message |
| `user_id` | UUID | ✅ | — | FK → `users.id`, NOT NULL | Acting user |
| `action_type` | VARCHAR(50) | ✅ | — | NOT NULL | e.g., `send_email`, `book_meeting`, `search_files` |
| `status` | VARCHAR(20) | ✅ | `'pending'` | CHECK IN ('pending','running','success','failed') | Execution state |
| `input_payload` | JSONB | ❌ | `'{}'` | — | Parameters sent to action handler |
| `output_payload` | JSONB | ❌ | `'{}'` | — | Result or error details |
| `duration_ms` | INTEGER | ❌ | `NULL` | — | Execution time in milliseconds |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Initiated at |
| `completed_at` | TIMESTAMPTZ | ❌ | `NULL` | — | Finished at |

**Example Row:**

| id | action_type | status | input_payload | duration_ms |
|----|-------------|--------|---------------|-------------|
| `x9y8z7w6-...` | send_whatsapp | success | `{"to": "+91...", "body": "Hi Raj..."}` | 1200 |

---

### 4.5 `contacts`

**Purpose:** User's address book for smart contact resolution in emails, WhatsApp, and calendar invites.

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Contact ID |
| `user_id` | UUID | ✅ | — | FK → `users.id`, NOT NULL | Owner |
| `name` | VARCHAR(150) | ✅ | — | NOT NULL | Contact display name |
| `email` | VARCHAR(255) | ❌ | `NULL` | — | Email address |
| `phone` | VARCHAR(20) | ❌ | `NULL` | — | Phone / WhatsApp number |
| `relationship` | VARCHAR(50) | ❌ | `NULL` | — | e.g., colleague, client, friend |
| `is_favorite` | BOOLEAN | ✅ | `FALSE` | — | Quick-access flag |
| `metadata` | JSONB | ❌ | `'{}'` | — | Extra fields (company, notes) |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Added at |
| `updated_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Modified at |

---

### 4.6 `calendar_events`

**Purpose:** Stores scheduled meetings, appointments, and time blocks.

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Event ID |
| `user_id` | UUID | ✅ | — | FK → `users.id`, NOT NULL | Owner |
| `title` | VARCHAR(255) | ✅ | — | NOT NULL | Event title |
| `description` | TEXT | ❌ | `NULL` | — | Event details |
| `start_time` | TIMESTAMPTZ | ✅ | — | NOT NULL | Start datetime |
| `end_time` | TIMESTAMPTZ | ✅ | — | NOT NULL | End datetime |
| `location` | VARCHAR(255) | ❌ | `NULL` | — | Physical or virtual location |
| `attendees` | JSONB | ❌ | `'[]'` | — | Array of `{ name, email, status }` |
| `recurrence_rule` | VARCHAR(255) | ❌ | `NULL` | — | iCal RRULE string |
| `external_id` | VARCHAR(255) | ❌ | `NULL` | UNIQUE | Google Calendar event ID |
| `status` | VARCHAR(20) | ✅ | `'confirmed'` | CHECK IN ('confirmed','tentative','cancelled') | Event status |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Created at |
| `updated_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Updated at |

**Example Row:**

| id | title | start_time | end_time | attendees |
|----|-------|------------|----------|-----------|
| `c1d2e3f4-...` | "Team Standup" | 2026-03-25T10:00Z | 2026-03-25T10:30Z | `[{"name":"Raj","email":"raj@co.in","status":"accepted"}]` |

---

### 4.7 `tasks`

**Purpose:** User task/to-do items managed by Alex.

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Task ID |
| `user_id` | UUID | ✅ | — | FK → `users.id`, NOT NULL | Owner |
| `title` | VARCHAR(255) | ✅ | — | NOT NULL | Task title |
| `description` | TEXT | ❌ | `NULL` | — | Task details |
| `priority` | VARCHAR(10) | ✅ | `'medium'` | CHECK IN ('low','medium','high','urgent') | Priority level |
| `status` | VARCHAR(20) | ✅ | `'todo'` | CHECK IN ('todo','in_progress','done','cancelled') | Current state |
| `due_date` | TIMESTAMPTZ | ❌ | `NULL` | — | Deadline |
| `completed_at` | TIMESTAMPTZ | ❌ | `NULL` | — | Completion timestamp |
| `source` | VARCHAR(50) | ✅ | `'manual'` | — | How task was created (`voice`, `meeting_extract`, `manual`) |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Created at |
| `updated_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Updated at |

---

### 4.8 `reminders`

**Purpose:** Time-triggered reminders set by the user via voice or text.

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Reminder ID |
| `user_id` | UUID | ✅ | — | FK → `users.id`, NOT NULL | Owner |
| `task_id` | UUID | ❌ | `NULL` | FK → `tasks.id` | Linked task (optional) |
| `message` | TEXT | ✅ | — | NOT NULL | Reminder text |
| `remind_at` | TIMESTAMPTZ | ✅ | — | NOT NULL | When to fire |
| `is_recurring` | BOOLEAN | ✅ | `FALSE` | — | Repeating reminder |
| `recurrence_rule` | VARCHAR(255) | ❌ | `NULL` | — | iCal RRULE |
| `status` | VARCHAR(20) | ✅ | `'pending'` | CHECK IN ('pending','sent','dismissed') | Lifecycle |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Created at |

---

### 4.9 `files`

**Purpose:** Metadata for user-uploaded or system-indexed files (actual binary in S3).

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | File ID |
| `user_id` | UUID | ✅ | — | FK → `users.id`, NOT NULL | Owner |
| `filename` | VARCHAR(255) | ✅ | — | NOT NULL | Original file name |
| `mime_type` | VARCHAR(100) | ✅ | — | NOT NULL | e.g., `application/pdf` |
| `size_bytes` | BIGINT | ✅ | — | NOT NULL | File size |
| `storage_path` | TEXT | ✅ | — | NOT NULL, UNIQUE | S3 key / object path |
| `is_indexed` | BOOLEAN | ✅ | `FALSE` | — | Whether vector embedding exists |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Upload time |
| `deleted_at` | TIMESTAMPTZ | ❌ | `NULL` | — | Soft delete |

---

### 4.10 `file_embeddings` (vector schema)

**Purpose:** pgvector embeddings for semantic file search.

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Embedding ID |
| `file_id` | UUID | ✅ | — | FK → `files.id`, UNIQUE, NOT NULL | Source file |
| `chunk_index` | INTEGER | ✅ | `0` | NOT NULL | Chunk position within file |
| `content_text` | TEXT | ✅ | — | NOT NULL | Raw text chunk used for embedding |
| `embedding` | VECTOR(1536) | ✅ | — | NOT NULL | OpenAI `text-embedding-3-small` vector |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Indexed at |

---

### 4.11 `user_preferences`

**Purpose:** Stores learned user behaviors, preferences, and personalization data.

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Preference ID |
| `user_id` | UUID | ✅ | — | FK → `users.id`, NOT NULL | Owner |
| `key` | VARCHAR(100) | ✅ | — | NOT NULL | Preference key (e.g., `preferred_greeting`, `tone`) |
| `value` | JSONB | ✅ | — | NOT NULL | Preference value (flexible structure) |
| `source` | VARCHAR(50) | ✅ | `'learned'` | — | `learned` (AI), `manual` (user-set) |
| `confidence` | FLOAT | ❌ | `NULL` | CHECK (0.0–1.0) | Confidence if AI-learned |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Created at |
| `updated_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Last updated |

**Example Row:**

| key | value | source | confidence |
|-----|-------|--------|------------|
| preferred_meeting_length | `{"minutes": 30}` | learned | 0.85 |
| tone | `{"style": "professional"}` | manual | NULL |

---

### 4.12 `meeting_summaries`

**Purpose:** AI-generated meeting transcription summaries and extracted action items (Meeting Copilot).

| Field | Data Type | Required | Default | Constraints | Description |
|-------|----------|----------|---------|-------------|-------------|
| `id` | UUID | ✅ | `gen_random_uuid()` | PK | Summary ID |
| `user_id` | UUID | ✅ | — | FK → `users.id`, NOT NULL | Owner |
| `calendar_event_id` | UUID | ❌ | `NULL` | FK → `calendar_events.id` | Linked calendar event |
| `title` | VARCHAR(255) | ✅ | — | NOT NULL | Meeting title |
| `transcript_url` | TEXT | ❌ | `NULL` | — | S3 URL to full transcript |
| `summary` | TEXT | ✅ | — | NOT NULL | AI-generated summary |
| `action_items` | JSONB | ❌ | `'[]'` | — | Array of `{ description, assignee, due }` |
| `duration_minutes` | INTEGER | ❌ | `NULL` | — | Meeting length |
| `created_at` | TIMESTAMPTZ | ✅ | `NOW()` | NOT NULL | Created at |

---

## 5.0 Indexes

| Table | Index Name | Column(s) | Type | Rationale |
|-------|-----------|-----------|------|-----------|
| `users` | `idx_users_email` | `email` | UNIQUE B-TREE | Fast login lookup |
| `conversations` | `idx_conv_user_id` | `user_id` | B-TREE | List conversations per user |
| `conversations` | `idx_conv_updated` | `updated_at DESC` | B-TREE | Recent conversations first |
| `messages` | `idx_msg_conv_id_created` | `conversation_id, created_at` | COMPOSITE B-TREE | Paginated chat history |
| `messages` | `idx_msg_intent` | `intent` | B-TREE | Analytics on user intents |
| `action_logs` | `idx_action_user_status` | `user_id, status` | COMPOSITE B-TREE | Pending actions dashboard |
| `calendar_events` | `idx_cal_user_time` | `user_id, start_time` | COMPOSITE B-TREE | Availability queries |
| `calendar_events` | `idx_cal_external` | `external_id` | UNIQUE B-TREE | Google Calendar sync dedup |
| `tasks` | `idx_task_user_status` | `user_id, status` | COMPOSITE B-TREE | Active tasks per user |
| `tasks` | `idx_task_due` | `due_date` | B-TREE | Upcoming deadline queries |
| `reminders` | `idx_remind_at` | `remind_at` | B-TREE | Worker polling for due reminders |
| `files` | `idx_file_user` | `user_id` | B-TREE | User file listing |
| `file_embeddings` | `idx_embed_vector` | `embedding` | IVFFlat / HNSW | Approximate nearest neighbor search |
| `user_preferences` | `idx_pref_user_key` | `user_id, key` | COMPOSITE UNIQUE | Fast preference lookup |

**Composite index notes:**
- `idx_msg_conv_id_created`: Optimizes the most frequent query — loading a conversation's messages ordered chronologically with pagination.
- `idx_cal_user_time`: Enables efficient range scans for "show me my schedule for tomorrow" without full table scan.

---

## 6.0 Relationships & Foreign Keys

| FK Column | References | ON DELETE | ON UPDATE | Rationale |
|-----------|-----------|-----------|-----------|-----------|
| `conversations.user_id` | `users.id` | CASCADE | CASCADE | Delete user → delete all conversations |
| `messages.conversation_id` | `conversations.id` | CASCADE | CASCADE | Delete conversation → delete all messages |
| `action_logs.message_id` | `messages.id` | CASCADE | CASCADE | Delete message → delete action logs |
| `action_logs.user_id` | `users.id` | CASCADE | CASCADE | User deletion cleans up |
| `contacts.user_id` | `users.id` | CASCADE | CASCADE | User deletion cleans up |
| `calendar_events.user_id` | `users.id` | CASCADE | CASCADE | User deletion cleans up |
| `tasks.user_id` | `users.id` | CASCADE | CASCADE | User deletion cleans up |
| `reminders.user_id` | `users.id` | CASCADE | CASCADE | User deletion cleans up |
| `reminders.task_id` | `tasks.id` | SET NULL | CASCADE | Task deletion doesn't remove reminder |
| `files.user_id` | `users.id` | CASCADE | CASCADE | User deletion cleans up |
| `file_embeddings.file_id` | `files.id` | CASCADE | CASCADE | File deletion removes embeddings |
| `user_preferences.user_id` | `users.id` | CASCADE | CASCADE | User deletion cleans up |
| `meeting_summaries.user_id`| `users.id` | CASCADE | CASCADE | User deletion cleans up |
| `meeting_summaries.calendar_event_id` | `calendar_events.id` | SET NULL | CASCADE | Event deletion doesn't destroy summary |

**Orphan data handling:** All user-owned data cascades on user deletion. For optional FKs (e.g., `reminders.task_id`), `SET NULL` preserves the child record while removing the stale reference.

---

## 7.0 Data Types & Conventions

| Convention | Standard | Example |
|------------|----------|---------|
| Table names | `snake_case`, plural | `calendar_events`, `action_logs` |
| Column names | `snake_case` | `created_at`, `user_id` |
| ID strategy | **UUID v4** | `gen_random_uuid()` — avoids sequential ID enumeration attacks |
| Timestamps | `TIMESTAMPTZ` (UTC always) | `2026-03-24T10:00:00+00:00` |
| Booleans | `BOOLEAN` | `is_active`, `is_indexed` |
| Flexible data | `JSONB` | `metadata`, `attendees`, `action_items` |
| Soft delete | `deleted_at TIMESTAMPTZ NULL` | `NULL` = active; non-NULL = deleted |
| Enums | `VARCHAR` + `CHECK` constraint | Avoids Postgres enum migration pain |

---

## 8.0 Migrations Strategy

### Tool
**Alembic** (SQLAlchemy's migration framework), integrated into the FastAPI project.

### Migration naming convention
```
YYYY_MM_DD_HHMM_<short_description>.py
```
Example: `2026_03_24_1430_add_meeting_summaries_table.py`

### Workflow
1. Modify SQLAlchemy models.
2. `alembic revision --autogenerate -m "add_meeting_summaries_table"`
3. Review generated migration file.
4. `alembic upgrade head` (apply).

### Rollback approach
- Every migration **must** include a `downgrade()` function.
- Rollback: `alembic downgrade -1` (one step back).
- Critical: Never drop columns in production without a two-phase migration (add new → migrate data → drop old).

### Seed data strategy
- Seed scripts in `apps/api/seeds/` directory.
- Executed via `python -m seeds.run` after initial `alembic upgrade head`.
- Seeds include: default admin user, sample contacts, demo conversation.

---

## 9.0 Query Patterns

### Most common queries

**1. Load conversation history (paginated)**
```sql
SELECT id, role, content, created_at
FROM messages
WHERE conversation_id = $1
ORDER BY created_at ASC
LIMIT 50 OFFSET $2;
```
*Covered by:* `idx_msg_conv_id_created`

**2. Check user availability for a time range**
```sql
SELECT id, title, start_time, end_time
FROM calendar_events
WHERE user_id = $1
  AND status = 'confirmed'
  AND start_time < $3       -- range_end
  AND end_time   > $2       -- range_start
ORDER BY start_time;
```
*Covered by:* `idx_cal_user_time`

**3. Semantic file search (vector similarity)**
```sql
SELECT f.filename, f.storage_path,
       1 - (fe.embedding <=> $1) AS similarity
FROM file_embeddings fe
JOIN files f ON f.id = fe.file_id
WHERE f.user_id = $2
  AND f.deleted_at IS NULL
ORDER BY fe.embedding <=> $1
LIMIT 10;
```
*Covered by:* `idx_embed_vector` (IVFFlat/HNSW)

**4. Upcoming reminders (worker poll)**
```sql
SELECT id, user_id, message, remind_at
FROM reminders
WHERE status = 'pending'
  AND remind_at <= NOW() + INTERVAL '1 minute'
ORDER BY remind_at ASC;
```
*Covered by:* `idx_remind_at`

**5. Wake-up briefing aggregation**
```sql
-- Tasks due today
SELECT * FROM tasks
WHERE user_id = $1 AND status IN ('todo','in_progress')
  AND due_date BETWEEN $2 AND $3;

-- Today's meetings
SELECT * FROM calendar_events
WHERE user_id = $1 AND status = 'confirmed'
  AND start_time BETWEEN $2 AND $3
ORDER BY start_time;
```

### Query optimization notes
- All `WHERE` clauses on `user_id` benefit from per-user partitioning at scale.
- JSONB fields (`metadata`, `attendees`) should **not** be indexed unless a GIN index is justified by query frequency.
- Vector search uses approximate nearest neighbor; tune `lists` (IVFFlat) or `ef_construction` (HNSW) based on dataset size.

---

## 10.0 Backup & Recovery

| Parameter | Value |
|-----------|-------|
| Backup method | `pg_basebackup` + WAL archiving (continuous) |
| Backup frequency | Full backup: **Daily** at 02:00 UTC |
| WAL archiving | Continuous streaming to S3 |
| Recovery Time Objective (RTO) | **< 30 minutes** |
| Recovery Point Objective (RPO) | **< 5 minutes** (WAL granularity) |
| Point-in-time recovery | Supported via WAL replay to any specific timestamp |
| Retention | 30 days of full backups; 7 days WAL |
| Testing Schedule | Monthly restore drill to staging environment |

---

## 11.0 Data Retention Policy

| Data Category | Retention Period | Action After Expiry |
|---------------|-----------------|---------------------|
| Active user data | Indefinite (while account active) | — |
| Soft-deleted user data | 90 days | Hard delete + cascade |
| Conversation messages | 2 years | Archive to cold storage (S3 Glacier) |
| Action logs | 1 year | Archive to cold storage |
| Meeting transcripts (S3) | 1 year | Delete from hot storage, keep summary |
| File embeddings | Matches parent file lifecycle | CASCADE delete |
| Voice recordings (S3) | 90 days | Auto-delete via S3 lifecycle rule |
| Redis cache | TTL-based (15 min – 24 hrs) | Auto-evict |

### Archival strategy
- Expired records exported as compressed Parquet files to S3 Glacier.
- Archived data is queryable via Athena if historical analysis is needed.

### Deletion cascade rules
- Hard-deleting a `user` triggers CASCADE across all child tables.
- A scheduled CRON job (`data_retention_worker`) runs nightly to enforce retention policies.

---

## 12.0 Open Questions

1. **Multi-tenancy:** Will Antigravity support multiple organizations, or remain single-user? This impacts schema isolation (row-level security vs. schema-per-tenant).
2. **Embedding model lock-in:** If we switch from OpenAI `text-embedding-3-small` (1536 dims) to another model, do we re-index all files? Migration strategy needed.
3. **GDPR/data export:** Do we need a `data_export_requests` table to handle right-to-access requests formally?
4. **Calendar sync conflicts:** How do we resolve conflicts between local DB state and Google Calendar as the external source of truth?

---

## 13.0 Next Steps

1. Implement SQLAlchemy models matching this schema in `apps/api/app/models/`.
2. Create initial Alembic migration and validate against a local PostgreSQL 16 instance.
3. Enable pgvector extension (`CREATE EXTENSION vector;`) and test HNSW index performance with sample embeddings.
4. Build seed data scripts for development and staging environments.
5. Configure `pg_basebackup` + WAL archiving pipeline in the infrastructure layer.
