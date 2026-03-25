# Security Document
## Alex — Personal AI Operating System
**Version:** v1.0
**Date:** 24 March 2026
**Status:** Draft
**Author:** Alex Build Team
**References:** PRD.md v1.0, SYSTEM_DESIGN.md v1.0, TECH_STACK.md v1.0, USER_FLOW.md v1.0, FEATURE_LIST.md v1.0, GOAL.md

---

## Table of Contents

1.0 Purpose & Scope
2.0 Security Principles
3.0 Authentication & Authorization
4.0 Data Security
5.0 API Security
6.0 Action Permission System
7.0 Privacy Considerations
8.0 Threat Model
9.0 Security Checklist
10.0 Incident Response Plan
11.0 Open Questions
12.0 Next Steps

---

## 1.0 Purpose & Scope

### 1.1 Purpose

This Security Document defines every security control, policy, and procedure governing the Alex v1.0 system. It establishes how user identity is verified, how sensitive data is stored and transmitted, which actions Alex may take autonomously versus which require explicit user approval, and what the team does when something goes wrong.

This document is the authoritative reference for all security decisions in Alex. It addresses the open question OQ-7 from PRD.md ("What security model governs access to stored memory and communication credentials?") in full, and it is the upstream reference for any security-related implementation decision made during development.

Every control described here has been designed against a single operating reality: Alex is a personal AI assistant that holds some of the most sensitive data a person produces — their emails, voice recordings, contact lists, calendar, files, and communication credentials. The security model must be proportionate to that responsibility.

### 1.2 Scope

This document covers the complete security surface of Alex v1.0: authentication and session management, encryption at rest and in transit, API security, the action permission model, data retention and deletion, privacy policy implementation, threat modelling, pre-launch security checks, and the incident response procedure. Infrastructure-level security (Railway server hardening, Supabase network isolation) is noted where relevant but is substantially managed by the respective platform operators.

### 1.3 Security Constraints Carried Forward

The following constraints from upstream documents directly shape every decision in this document.

| Source | Constraint |
|--------|-----------|
| PRD.md §7.1 | Voice processing must support offline capability — wake word detection must function without internet |
| PRD.md §7.1 | Mode switching between free and paid AI must not interrupt active tasks or corrupt stored data |
| TECH_STACK.md | Supabase Auth provides JWT-based authentication; PostgreSQL Row Level Security enforces data isolation |
| TECH_STACK.md | Doppler manages all environment variables and secrets across development and production |
| TECH_STACK.md | Credentials for email, WhatsApp, and paid AI APIs are stored encrypted in Supabase secrets |
| USER_FLOW.md §5.1 | Irreversible external actions (email send, WhatsApp send, calendar creation) always require user confirmation |
| FEATURE_LIST.md | 51 features ship in v1.0; eight features involving external communication or AI key usage require particular security attention |

---

## 2.0 Security Principles

Alex's security model is built on six principles that govern every decision in this document. When a new security question arises during development that this document does not explicitly address, these principles provide the decision framework.

**Principle 1 — Minimal Footprint.** Alex stores only the data it needs to function. Every data field, every table column, and every secret must be justified by a specific feature requirement. Data that is no longer needed for its stated purpose is deleted on the schedule defined in §4.4.

**Principle 2 — Confirmation Before Consequence.** No action with an external effect — sending a message, booking a meeting, dispatching a file — executes without explicit user confirmation in the current session. This is both a usability principle and a security control: it prevents a compromised or misbehaving AI model from taking real-world actions autonomously. The full confirmation matrix is defined in §6.0.

**Principle 3 — Encryption by Default.** All data is encrypted in transit using TLS 1.3 or later. All sensitive data at rest — credentials, tokens, API keys, voice recordings — is encrypted using AES-256 or the equivalent managed encryption provided by the storage platform. No sensitive value is ever stored in plaintext in any environment.

**Principle 4 — Least Privilege.** Every component of Alex holds only the permissions it needs to perform its function. The FastAPI backend holds a Supabase service role key scoped to its required tables. The frontend holds only the Supabase anon key, which can read and write only the data the authenticated user owns, as enforced by Row Level Security policies. The AI Model Router holds API keys only when paid mode is active. No component holds credentials it does not need.

**Principle 5 — Auditability.** Every action Alex takes on behalf of the user — every email sent, every file accessed, every calendar event created, every AI API call made — is logged to the `audit_logs` table with the session ID, timestamp, action type, and outcome. The user can inspect this log at any time from the dashboard. Logs cannot be deleted by the user in v1.0 (they expire on schedule); this protects the audit trail's integrity.

**Principle 6 — User Sovereignty.** The user owns all data Alex stores about them. They can view it, export it, and request deletion at any time. Alex does not share user data with third parties except where the user has explicitly configured an integration (Google Calendar, Twilio, Resend) and where that integration requires transmitting specific data to function.

---

## 3.0 Authentication & Authorization

### 3.1 User Authentication

Alex v1.0 is a single-user system. Authentication is handled by Supabase Auth, which manages the full lifecycle of user identity: registration, login, session refresh, and logout. Email and password is the default authentication method. Google OAuth is supported as a secondary method and is the recommended path because it enables the Google Calendar OAuth flow required by F026–F030 to reuse the same Google identity without a separate consent screen.

On successful authentication, Supabase issues two tokens: a short-lived JWT access token (default expiry: 1 hour) and a long-lived refresh token (default expiry: 7 days). The access token is stored in browser memory only — never in `localStorage` or `sessionStorage`, which are vulnerable to XSS attacks. The refresh token is stored in an `HttpOnly`, `Secure`, `SameSite=Strict` cookie, making it inaccessible to JavaScript. Supabase's client library handles silent refresh automatically when the access token approaches expiry.

The FastAPI backend validates every authenticated request by verifying the JWT signature against Supabase's public JWKS endpoint. Validation checks the token's signature, expiry, issuer claim, and audience claim. Any request with a missing, malformed, or expired token receives a `401 Unauthorized` response. There are no unauthenticated endpoints in the Alex API except the health check at `GET /health`, which returns only a status string.

Password requirements enforce a minimum of 12 characters with at least one uppercase letter, one lowercase letter, one digit, and one special character. Password reset is handled entirely by Supabase Auth's built-in email flow.

### 3.2 API Key Management

Alex uses several categories of API key, each with distinct storage and access rules.

**Internal API key (FastAPI).** A randomly generated 256-bit key used to authenticate communication between the Next.js frontend and the FastAPI backend. Generated at deployment time by a Doppler secret, injected into both the Vercel build and the Railway deployment as environment variables. Rotated manually on any suspected compromise and automatically every 90 days via a documented rotation procedure.

**Paid AI API keys (Anthropic, OpenAI).** These are user-supplied keys stored encrypted in Supabase Vault (the managed encrypted secret store within Supabase). They are never written to Doppler, environment variables, or any log. The FastAPI AI Model Router retrieves these keys from Supabase Vault at call time using the user's authenticated session, decrypts them in memory, and uses them for the duration of that API call only. They are not cached in Redis or retained in any variable after the call completes. If the user deactivates paid mode, the keys are not deleted from Vault — they are retained so the user can reactivate without re-entering them — but the AI Model Router stops retrieving or using them.

**Third-party service credentials (Twilio, Google Calendar OAuth, email SMTP/IMAP).** Stored in Supabase Vault under per-user secret keys. Encrypted at rest by Supabase using AES-256. The FastAPI service retrieves and decrypts them in memory at the point of use. SMTP passwords specifically are stored as Supabase Vault secrets and never appear in application logs, error messages, or API responses.

**Doppler (infrastructure secrets).** DATABASE_URL, REDIS_URL, SENTRY_DSN, SUPABASE_SERVICE_ROLE_KEY, and the internal API key are all managed in Doppler and injected at deployment time. No developer needs to handle these values directly after initial setup.

### 3.3 OAuth Flows

**Google OAuth (Calendar + Account Login).** Alex uses Supabase Auth's built-in Google OAuth provider. When the user authenticates with Google, Supabase Auth handles the OAuth 2.0 code exchange and stores the Google access and refresh tokens internally. The Calendar integration (F026–F030) uses the Google access token retrieved from Supabase Auth's `provider_token` field. If the token has expired, Supabase Auth silently refreshes it using the stored refresh token. The user's raw Google refresh token is never exposed to the FastAPI application — Supabase Auth holds it and issues short-lived access tokens on demand.

The required OAuth scopes for v1.0 are `openid`, `email`, `profile` (for account authentication), and `https://www.googleapis.com/auth/calendar` (for full calendar read/write). The calendar scope is requested as an incremental authorization during onboarding after the user opts in to calendar integration, not at initial login. Users who skip calendar setup during onboarding are never prompted for the calendar scope unless they explicitly connect their calendar in Settings.

**Scope principle.** Alex will never request broader OAuth scopes than those explicitly required by a feature present in the current release. Adding a new integration in v1.5 or v2.0 requires a new incremental authorization request at the time that feature is activated, not at initial login.

### 3.4 Session Management

Sessions are identified by a UUID `session_id` generated at dashboard load and passed in every API request. Session context (last five conversation turns) is stored in Redis keyed by `session:{session_id}:context` with a TTL of 1,800 seconds (30 minutes of inactivity). When the TTL expires, the context is evicted from Redis automatically; the next request starts a new session.

Session IDs are never reused after expiry. The session ID is opaque and provides no information about the user; the JWT carries all identity context. Multiple simultaneous sessions from the same user (e.g., dashboard open on two devices) are currently unsupported — the second session overwrites the Redis context key of the first.

The user can explicitly end their session via the "Log out" action in the dashboard, which calls `DELETE /api/v1/auth/session`. This revokes the Supabase Auth session server-side, clears the refresh token cookie, and evicts the Redis session context immediately.

### 3.5 Role-Based Access Control

Alex v1.0 is a single-user system. There is only one role — the authenticated user — who has full read/write access to their own data and no access to any other user's data. PostgreSQL Row Level Security (RLS) enforces this at the database layer.

Every table that contains user data includes a `user_id UUID` column. RLS policies on every such table check that `user_id = auth.uid()`, where `auth.uid()` is the user ID extracted from the validated JWT. This means that even if the FastAPI application layer has a bug that constructs an incorrect query, the database will refuse to return rows belonging to another user. The service role key (held only by the FastAPI backend) bypasses RLS for system-level operations such as Celery jobs and the nightly pruning tasks. All service role operations are logged to `audit_logs` with `source = 'system'`.

The RLS policies are defined in SQL migrations and version-controlled in the repository. They are applied automatically on database provisioning and must be reviewed in every pull request that adds a new table or modifies an existing table schema.

---

## 4.0 Data Security

### 4.1 Data Encryption at Rest

The following table documents every data store, the sensitive data it holds, and the encryption method applied.

| Data Store | Sensitive Data Held | Encryption Method |
|-----------|-------------------|------------------|
| Supabase PostgreSQL | Tasks, reminders, contacts, preferences, calendar events, audit logs, file index, conversation memory embeddings | AES-256 encryption at rest, managed by Supabase on the database volume. Supabase encrypts the entire PostgreSQL volume using cloud-provider KMS (AWS KMS on the underlying infrastructure). |
| Supabase Vault | Email credentials (SMTP/IMAP passwords), Twilio credentials, paid AI API keys (Anthropic, OpenAI), Google OAuth refresh tokens, internal API key | Supabase Vault encrypts each secret individually using AES-256-GCM with per-secret encryption keys derived from a master key held in the platform's HSM. |
| Supabase Storage | Meeting audio recordings (`.wav` files), file thumbnails, document attachments | AES-256 server-side encryption, managed by Supabase. Files in the `meeting-recordings` bucket are private by default; access requires a valid Supabase Storage signed URL obtained through the authenticated FastAPI backend only. |
| Redis | Session context (last 5 turns), cached calendar events, cached preferences, Celery task queue | Redis 7 on Railway does not provide application-level encryption — Railway encrypts the persistent volume at rest using AES-256. Sensitive data (credentials, API keys) must never be written to Redis. Session context holds only conversation text and session metadata; no credentials flow through Redis. |
| Doppler | Infrastructure secrets: DATABASE_URL, REDIS_URL, SENTRY_DSN, SUPABASE_SERVICE_ROLE_KEY, internal API key | Doppler encrypts all secrets at rest using AES-256-GCM and manages the key in a dedicated KMS. |
| pgvector (within Supabase PostgreSQL) | Conversation memory embeddings (384-dimensional float vectors derived from interaction text) | Encrypted as part of the PostgreSQL volume (same as above). Embeddings themselves do not contain raw text — they are mathematical representations — but the source text is stored in the `document` column of the same table. |

### 4.2 Data Encryption in Transit

All communication between system components uses TLS 1.3 or TLS 1.2 minimum (1.2 is accepted only for legacy compatibility with certain email servers). TLS configuration is enforced at the platform level — Vercel, Railway, and Supabase all provision and renew TLS certificates automatically using Let's Encrypt.

The following connections all require TLS:

- Browser to Vercel (Next.js dashboard) — TLS 1.3, HSTS enforced.
- Browser WebSocket to FastAPI (Railway) — WSS (WebSocket Secure), TLS 1.3.
- FastAPI to Supabase PostgreSQL — TLS 1.3 via Supabase connection pooler (PgBouncer).
- FastAPI to Supabase Storage — HTTPS, TLS 1.3.
- FastAPI to Redis (Railway internal network) — Railway's private internal network provides transport isolation; TLS is not added on top of internal Railway networking in v1.0, which is noted as a limitation in §11.0.
- FastAPI to Anthropic / OpenAI APIs — HTTPS, TLS 1.3 (enforced by the respective SDKs).
- FastAPI to Twilio — HTTPS, TLS 1.3.
- FastAPI to Google Calendar API — HTTPS, TLS 1.3.
- FastAPI to Resend — HTTPS, TLS 1.3.
- Email SMTP (outbound) — STARTTLS on port 587, upgraded to TLS 1.2+.
- Email IMAP (inbound) — SSL/TLS on port 993.

HTTP-to-HTTPS redirects are enforced at the Vercel and Railway proxy layers. All API responses include the following security headers: `Strict-Transport-Security: max-age=31536000; includeSubDomains`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy` (defined in Next.js `headers()` config), and `Referrer-Policy: strict-origin-when-cross-origin`.

### 4.3 Sensitive Data Handling

**Email credentials and message content.** SMTP and IMAP credentials (email address, password or app password) are stored exclusively in Supabase Vault. They are retrieved by the FastAPI backend in memory only at the moment an SMTP/IMAP operation is performed and are released from memory when the operation completes. Email body content composed by Alex is not stored in any persistent store after the send is confirmed and logged. The audit log records the recipient, subject, and timestamp — never the body content. Incoming email data read via IMAP for briefing purposes is fetched at briefing time, processed in memory, and never written to the database. The API response that delivers briefing content to the frontend is not logged.

**WhatsApp message content.** Identical handling to email. The Twilio credentials (Account SID, Auth Token) are stored in Supabase Vault. Message body content is not persisted after send confirmation. The audit log records the recipient's WhatsApp ID (hashed), the timestamp, and the delivery status — not the message body.

**Voice recordings.** Raw audio files captured during meeting transcription (F040) are stored in Supabase Storage under the `meeting-recordings` bucket, which is private and requires a signed URL for access. Signed URLs are issued by the FastAPI backend with a 15-minute expiry for in-browser playback. Voice command audio — the short audio clips captured in response to the wake word — is processed in memory by `faster-whisper` and is never written to disk or any database. It exists only for the duration of the transcription operation.

**Personal preferences.** Preferences (communication style, working hours, briefing time, AI mode) are stored in the `preferences` table in PostgreSQL, scoped to the user via RLS. They are not encrypted at the column level beyond the volume-level encryption Supabase provides, because preferences are not credentials or high-sensitivity identifiers. Users can view, edit, and delete any preference at any time from the Settings panel.

**File metadata and embeddings.** File paths, names, and content embeddings are stored in PostgreSQL and pgvector, scoped to the user via RLS. The actual file content is not stored in the database — only a 384-dimensional embedding vector and a 200-character content summary. Files remain on the user's local machine and in Supabase Storage only when explicitly uploaded as meeting attachments. Alex never silently uploads the user's local files to any cloud service.

### 4.4 Data Retention Policy

| Data Category | Retention Period | Notes |
|--------------|----------------|-------|
| Audit logs | 90 days (general actions); 180 days (errors and failed actions) | Purged by nightly Celery job; cannot be manually deleted in v1.0 |
| Conversation memory (pgvector) | 90 days from interaction date | Purged by nightly Celery job; user can delete individual entries manually |
| Session context (Redis) | 30 minutes of inactivity | Automatic TTL eviction by Redis |
| Meeting transcripts (text) | Indefinite until user deletes | Stored in Supabase Storage; user-deletable from Meeting History |
| Meeting audio recordings | 30 days from session end | Auto-deleted by Celery job after 30 days; user can delete sooner |
| Calendar event cache | 7 days (cached entries only) | Purged on cache rebuild; source of truth remains in Google Calendar |
| Tasks and reminders | Indefinite until user completes/deletes | Completed tasks are soft-deleted (status = 'completed'); hard-deleted after 180 days |
| Contact records | Indefinite until user deletes | User-deletable from Contacts panel |
| File index (metadata + embeddings) | Until file is deleted from watched directory | Watchdog removes index entry on file deletion; user can remove from index manually |
| Email credentials | Until user disconnects email integration | Deleted from Supabase Vault on disconnect |
| Paid AI API keys | Until user deletes from Settings | Keys are retained when paid mode is deactivated; user must explicitly delete |
| Twilio credentials | Until user disconnects WhatsApp integration | Deleted from Supabase Vault on disconnect |
| OAuth tokens (Google) | Until user disconnects Google integration | Supabase Auth revokes and removes tokens on disconnect |

### 4.5 Data Deletion Process

**Account deletion.** When a user requests account deletion (Settings → Delete Account), the following sequence runs as an atomic transaction: (1) all rows in all user-scoped tables are hard-deleted, (2) all Supabase Vault secrets associated with the user are deleted, (3) all Supabase Storage objects in the user's `meeting-recordings` and `user-files` buckets are deleted, (4) the Supabase Auth user record is deleted, (5) the user's Redis session is evicted, and (6) a confirmation email is sent to the user's registered address. The entire deletion process completes within 24 hours of request. Account deletion is irreversible and requires the user to type their email address to confirm before the deletion job is dispatched.

**Selective data deletion.** The user can delete specific categories of data without deleting their account: conversation memory entries (individually or all at once via `DELETE /api/v1/memory/history`), meeting transcripts and recordings, individual tasks, contacts, and file index entries. All selective deletions are permanent and immediate.

**Third-party data.** Alex cannot delete data that has already been transmitted to third parties (a sent email cannot be un-sent; a dispatched WhatsApp message cannot be recalled). The audit log entry for such actions is retained per the 90-day retention policy above, but the message content is not stored and therefore not deletable because it was never retained.

---

## 5.0 API Security

### 5.1 Rate Limiting

Rate limiting is applied at two layers: the FastAPI application layer and the Supabase API layer.

At the FastAPI layer, rate limits are enforced per authenticated user using Redis as the rate limit counter store. The limits below apply per user per time window:

| Endpoint Group | Rate Limit | Window |
|--------------|-----------|--------|
| `POST /api/v1/command` | 60 requests | per minute |
| `POST /api/v1/communication/email/send` | 20 requests | per hour |
| `POST /api/v1/communication/whatsapp/send` | 30 requests | per hour |
| `POST /api/v1/calendar/events` | 20 requests | per hour |
| `GET /api/v1/files/search` | 120 requests | per minute |
| `POST /api/v1/tasks` and `POST /api/v1/reminders` | 60 requests | per minute |
| All other authenticated endpoints | 200 requests | per minute |

Requests that exceed the rate limit receive a `429 Too Many Requests` response with a `Retry-After` header indicating when the next request will be accepted. Repeated rate limit violations (more than five `429` responses within a 10-minute window) trigger a Sentry alert and a temporary 15-minute block on that user's session.

Supabase applies its own rate limits at the Auth layer (100 sign-ins per hour per IP) and the PostgREST layer. The FastAPI backend interacts with Supabase directly via the service role SDK, which is not subject to the same per-request PostgREST rate limits.

### 5.2 Input Validation

All request bodies to FastAPI endpoints are validated using Pydantic v2 models before any processing occurs. Pydantic validation is applied at the route handler level, so invalid requests are rejected with a `422 Unprocessable Entity` response before reaching any business logic. Validation rules cover required fields, field types, string length limits, enum constraints, and UUID format enforcement.

String inputs from the command endpoint (`/api/v1/command`) are treated as untrusted user input throughout the processing pipeline. They are never interpolated directly into SQL queries — all database interactions use SQLAlchemy ORM with parameterised queries, eliminating SQL injection as an attack vector. String inputs passed to the AI Model Router are included in the user message portion of the prompt, not the system prompt, so they cannot override system-level instructions.

File paths supplied by the user in watched directory configuration are validated against an allowlist of the user's confirmed local directories. Path traversal sequences (`../`, `..\\`) in any file path input are rejected with a `400 Bad Request` before any file system operation occurs.

Webhook payloads from Twilio and Google Calendar are validated using the respective providers' signature verification mechanisms (Twilio request signature via `X-Twilio-Signature`; Google Calendar webhook push notifications via a channel token). Payloads that fail signature verification are rejected before processing.

### 5.3 API Key Rotation

The following rotation schedule applies to all API keys managed by Alex:

| Key | Rotation Trigger | Rotation Method |
|-----|-----------------|----------------|
| Internal FastAPI API key | Every 90 days (scheduled) or immediately on suspected compromise | Generate new key in Doppler; redeploy Railway and Vercel; old key deactivated |
| Supabase service role key | Every 180 days or on suspected compromise | Regenerate in Supabase dashboard; update in Doppler; redeploy |
| User's paid AI API keys | On user request or suspected compromise | User re-enters key in Settings; old value overwritten in Supabase Vault |
| Twilio credentials | On user request | User re-enters in Settings; old value overwritten in Supabase Vault |
| Google OAuth refresh token | Automatic (Supabase Auth manages rotation) | Supabase rotates silently using the Google refresh token |
| SMTP app password | On user request | User re-enters in Settings; old value overwritten in Supabase Vault |

An automated check runs weekly via GitHub Actions to verify that all Doppler-managed keys are within their rotation window. Keys approaching or past their rotation date generate a Sentry alert to the development team.

### 5.4 Webhook Security

Alex exposes two webhook endpoints to receive inbound payloads from external services: `POST /api/v1/webhooks/twilio` (delivery status callbacks from Twilio) and `POST /api/v1/webhooks/google-calendar` (push notification from Google Calendar on event changes).

Both endpoints enforce the following controls: request signature verification (as described in §5.2), strict content-type validation (`application/x-www-form-urlencoded` for Twilio; `application/json` for Google), payload size limits (1 MB maximum), and idempotency checks using the Twilio message SID and Google Calendar event ID to prevent duplicate processing of replayed or retried webhook deliveries.

n8n webhook endpoints (used to trigger Alex workflows from n8n) are secured with a shared secret in the request header, validated by the FastAPI webhook handler before any workflow logic executes.

---

## 6.0 Action Permission System

### 6.1 Permission Levels

Alex's action permission system defines four levels of autonomy for every action the system can take. The level assigned to an action reflects its consequence, reversibility, and external reach.

| Permission Level | Definition | User Interaction Required |
|----------------|-----------|--------------------------|
| **AUTO** | Alex executes the action immediately without any confirmation prompt. The action is read-only or internally scoped, produces no external effect, and is trivially reversible. | None |
| **CONFIRM** | Alex presents a plain-language summary of the action and waits for explicit user approval before executing. Required for all actions with external effects or that cannot be easily undone. | Explicit "Yes" / "Go ahead" before execution |
| **ELEVATED** | Alex requires confirmation plus additional verification — typing a key phrase or re-entering a credential — before executing. Reserved for high-consequence or security-sensitive operations. | Confirmation plus secondary verification |
| **RESTRICTED** | Alex will not perform this action under any circumstances in v1.0, regardless of user instruction. | None — action is declined with explanation |

### 6.2 Full Permission Matrix

| Action | Permission Level | Reason |
|--------|-----------------|--------|
| Read calendar events | AUTO | Read-only; no external effect |
| Read task list or reminders | AUTO | Read-only; no external effect |
| Read contact records | AUTO | Read-only; no external effect |
| Generate and display a morning briefing | AUTO (when scheduled) | User pre-authorised at configured time |
| Generate and display meeting summary | AUTO | User explicitly triggered recording session |
| Store a task or reminder | AUTO | Reversible; internally scoped; no external effect |
| Update task status (complete, cancel) | AUTO | Reversible via status update; internally scoped |
| Index files in watched directories | AUTO | Read-only file access; no external effect |
| Search files | AUTO | Read-only; no external effect |
| Store a contact | AUTO | Internally scoped; reversible |
| Cache calendar events | AUTO | System maintenance; no external effect |
| Write to audit_logs | AUTO | System operation; always logged |
| Store conversation memory (pgvector) | AUTO | Internally scoped; user can delete |
| Send an email | CONFIRM | Irreversible external communication |
| Send a WhatsApp message | CONFIRM | Irreversible external communication |
| Attach a file to an email or WhatsApp | CONFIRM | Irreversible; combines file access with external dispatch |
| Create a calendar event with attendees | CONFIRM | Sends invitations to third parties |
| Create a calendar event without attendees | CONFIRM | Creates a record in the user's connected Google Calendar |
| Execute a multi-step plan (3+ steps) | CONFIRM | High consequence; user must verify the full sequence |
| Execute a multi-step plan (1–2 steps) | CONFIRM | Any plan with external effects requires confirmation |
| Delete a task, reminder, or contact | CONFIRM | Data deletion is not easily reversible |
| Trigger an n8n workflow | CONFIRM | External integrations may have irreversible effects |
| Use paid AI API for the first time | CONFIRM | Cost implication; requires informed consent |
| Activate paid AI mode | CONFIRM | Billing implication; explicit user opt-in |
| Add a new watched directory | CONFIRM | File system access scope change |
| Connect a new integration (calendar, email, WhatsApp) | CONFIRM | Third-party data access grant |
| Delete conversation memory (all) | ELEVATED | Permanent, irreversible bulk data deletion |
| Delete account and all data | ELEVATED | Permanent, irreversible; must type email address to confirm |
| Revoke an OAuth integration (Google) | ELEVATED | Removes a previously granted data access |
| Rotate internal API keys | ELEVATED | Security-sensitive infrastructure change |
| Send a bulk communication (multiple recipients at once) | ELEVATED | Higher external impact than single-recipient send |
| Read or export another user's data | RESTRICTED | Violates single-user data isolation; blocked by RLS |
| Execute any action without a valid authenticated session | RESTRICTED | No unauthenticated action execution |
| Execute any action in autonomous mode (without confirmation) | RESTRICTED | Autonomous agent mode is v2.0 and not enabled in v1.0 |
| Store email body content in the database | RESTRICTED | Privacy — message bodies are never persisted |
| Store voice command audio to disk | RESTRICTED | Privacy — command audio is ephemeral |
| Transmit local file content to any cloud service without explicit user action | RESTRICTED | Privacy — files stay local unless user explicitly uploads |
| Access files outside configured watched directories | RESTRICTED | File system access is limited to user-configured directories |
| Make API calls to any provider not listed in integrations | RESTRICTED | Unknown third-party data transmission |
| Modify audit log entries | RESTRICTED | Audit log integrity must be preserved |

### 6.3 Confirmation Gate Implementation

CONFIRM-level actions are gated in the FastAPI automation layer as follows: the Task Planner sets `confirmation_required: true` on any plan that contains a CONFIRM-level or ELEVATED-level action. The plan is serialised to a human-readable preview and returned to the frontend with `status: "awaiting_confirmation"`. A pending confirmation plan is stored in Redis keyed by `plan:{plan_id}:pending` with a 60-second TTL. If the user confirms within 60 seconds via `POST /api/v1/confirm`, the Automation Engine executes. If the TTL expires before confirmation, the plan is cancelled and the pending Redis key is evicted. The confirmation endpoint validates that the `plan_id` exists, belongs to the authenticated user's session, and has not expired before executing any step.

---

## 7.0 Privacy Considerations

### 7.1 What Data Alex Stores

The complete inventory of personal data stored by Alex v1.0, organised by data type and storage location, is as follows.

**Identity data:** Email address and hashed password (or Google account identifier) — stored in Supabase Auth. Used only for authentication.

**Contacts:** Display name, aliases, email address, phone number, WhatsApp ID, interaction frequency — stored in PostgreSQL `contacts` table. User-created and user-managed.

**Tasks and reminders:** Title, description, status, priority, due date, source, and optional meeting association — stored in PostgreSQL `tasks` and `reminders` tables.

**Calendar events:** Title, description, start/end time, location, attendees, provider ID — stored in PostgreSQL `calendar_events` table as a local cache of Google Calendar data.

**File index:** File name, path, extension, size, content hash, modification date, and a 384-dimensional embedding vector derived from the first 512 tokens of file content — stored in PostgreSQL `file_index` and pgvector. Actual file content is never stored.

**Conversation memory:** A text summary of each completed interaction and a 384-dimensional embedding of that summary — stored in PostgreSQL with pgvector. The raw interaction transcript is not stored; only the summary that Alex generates.

**Meeting data:** Meeting title, start/end time, participant names (extracted from transcript), AI-generated summary, extracted action items as JSON, and the file path to the raw audio and transcript in Supabase Storage.

**Preferences:** All user-configured preferences including AI mode, email tone, working hours, watched directories, briefing time, voice settings — stored in PostgreSQL `preferences` table.

**Audit logs:** Session ID, input text (voice command or typed message), parsed intent type (not full intent object), executed action types, outcome status, duration, and AI model used — stored in PostgreSQL `audit_logs` table. Email and message body content is never stored in audit logs.

**Secrets:** SMTP credentials, Twilio credentials, paid AI API keys, OAuth refresh tokens — stored in Supabase Vault. Never stored in the application database or logs.

### 7.2 What Alex Never Stores

The following data is never written to any persistent store by Alex:

- Email body content of composed or received emails.
- WhatsApp message body content after send confirmation.
- Raw voice command audio (processed in memory only; immediately discarded).
- The full content of local files (only metadata and embedding vectors are stored).
- Passwords in plaintext.
- API keys in plaintext in any database, log, or environment file.
- Browser history, clipboard contents, or screen contents.
- Location data.
- Device identifiers beyond the session ID used for conversation context.

### 7.3 User Data Control

Every category of personal data stored by Alex is visible, editable, and deletable by the authenticated user:

- **View all stored data:** Settings → Data & Privacy → View My Data. Returns a JSON export of all user-owned rows across all tables.
- **Delete conversation memory:** Settings → Memory → Clear All Memory, or `DELETE /api/v1/memory/history`.
- **Delete individual items:** From the relevant dashboard panel (tasks, contacts, meetings, file index entries).
- **Disconnect integrations:** Settings → Integrations. Disconnecting an integration deletes the associated credentials from Supabase Vault and revokes the OAuth token if applicable.
- **Export all data:** Settings → Data & Privacy → Export My Data. Generates a ZIP file containing JSON exports of all tables and a manifest of all files in Supabase Storage. Delivered as a signed download URL valid for 24 hours.
- **Delete account:** Settings → Data & Privacy → Delete Account. Requires email address confirmation. All data is permanently deleted within 24 hours.

### 7.4 GDPR Considerations

Alex v1.0 is a personal productivity tool used by a single individual. The system does not collect data about third parties beyond contact names and email addresses entered explicitly by the user. The user is the data controller for all personal data stored in Alex. The Alex Build Team, as operator of the hosted infrastructure, acts as the data processor.

The following rights apply under GDPR and are implemented as described above:

- **Right to access:** Implemented via the Data Export feature (§7.3).
- **Right to rectification:** Implemented — users can edit any stored data at any time.
- **Right to erasure:** Implemented via selective deletion and the full account deletion flow (§4.5).
- **Right to data portability:** Implemented via the JSON export feature (§7.3).
- **Right to restrict processing:** Implemented by disabling specific integrations or deactivating the briefing, which stops the relevant processing.

Data is stored on Supabase's infrastructure in the region selected during project creation (recommended: `ap-south-1` for Indian users in line with the target user persona). Railway deploys in the nearest available region at project creation. Vercel serves the frontend from the global edge network with no region-specific data storage.

---

## 8.0 Threat Model

### 8.1 Threat Assessment Matrix

| # | Threat | Attack Vector | Risk Level | Mitigation |
|---|--------|-------------|-----------|-----------|
| T1 | Stolen JWT used to impersonate user | Intercepted token from XSS or network | **High** | JWT stored in memory (not localStorage); HttpOnly refresh cookie prevents JS access; short JWT expiry (1 hour); HTTPS enforced everywhere |
| T2 | Compromised Supabase Vault secret (API key exfiltration) | Insider threat or Supabase breach | **High** | Vault secrets accessible only through authenticated service role; key rotation schedule enforced; paid AI keys retrieved in memory only, never cached or logged |
| T3 | Prompt injection via malicious file content | User indexes a file containing adversarial text designed to override AI instructions | **High** | User input (including file content summaries) is placed only in the user message, never in the system prompt; AI model instructions cannot be overridden by user-turn content in structured generation modes |
| T4 | SMTP credential theft enabling email account takeover | Exfiltration of SMTP credentials from Vault | **High** | Credentials stored in Supabase Vault only; never appear in logs, API responses, or Redis; retrieved in memory at use time and immediately released |
| T5 | Unauthorised data access via RLS bypass | SQL injection or misconfigured RLS policy | **High** | Parameterised queries via SQLAlchemy ORM prevent SQL injection; RLS policies version-controlled and reviewed in every PR; service role key not exposed to frontend |
| T6 | Replay attack on confirmation endpoint | Attacker captures and resends a confirmation request | **Medium** | Plan IDs are UUIDs; pending plans have 60-second TTL; each plan ID is consumed on first confirmation and cannot be re-confirmed |
| T7 | Man-in-the-middle attack on API communication | Network interception between frontend and backend | **Medium** | TLS 1.3 enforced on all connections; HSTS prevents downgrade attacks; certificate pinning not implemented in v1.0 (noted in §11.0) |
| T8 | Session hijacking via session ID theft | Session ID intercepted from API requests | **Medium** | Session IDs are opaque UUIDs; they provide no access without the accompanying JWT; JWT validation is required for every authenticated request |
| T9 | n8n workflow abuse | Attacker triggers n8n webhooks to execute arbitrary workflows | **Medium** | n8n webhook endpoints require shared secret header validation; workflows are version-controlled and reviewed; n8n runs on Railway's private internal network |
| T10 | Webhook replay from Twilio or Google | Attacker replays a previously captured webhook payload | **Medium** | Twilio signature verification prevents replay; Google Calendar push notifications use a channel token validated per request; idempotency checks prevent duplicate processing |
| T11 | Excessive AI API calls draining user's paid API credits | Bug or malicious command causing runaway AI calls | **Low** | Per-user rate limiting (60 requests/minute) on the command endpoint; Celery task deduplication; circuit breaker on AI provider calls after 5 consecutive errors |
| T12 | File path traversal accessing files outside watched directories | Attacker crafts a file path containing `../` to escape watched directories | **Low** | Path traversal sequences rejected at input validation layer; file access strictly limited to paths within configured watched directories |
| T13 | Voice command spoofing via audio injection | Attacker plays audio near the microphone to trigger unintended commands | **Low** | All commands with external effects require dashboard confirmation (CONFIRM level); confirmation prompt appears on screen and requires visual/keyboard interaction |
| T14 | Denial of service via high-volume API requests | Automated requests to exhaust Railway compute | **Low** | Rate limiting enforced per user; Railway auto-scales within plan limits; Sentry alert on sustained high error rates |
| T15 | Sensitive data in Sentry error reports | Stack traces or log lines containing credentials | **Low** | Sentry SDK configured with data scrubbing rules to remove known sensitive field names (password, api_key, token, smtp_password) before transmission; credentials never appear in log lines |

### 8.2 Prompt Injection Mitigation (T3)

Prompt injection deserves extended treatment given that Alex sends user-controlled content — file summaries, email drafts, meeting transcripts — to AI models. The mitigation strategy uses three layers of defence.

The first layer is prompt structure. The AI Instructions Document (authored next) specifies that all user-controlled content is placed in the `user` message role only, never in the `system` role. The system prompt contains all instructions governing Alex's behaviour. Since the AI model distinguishes between system and user content, placing adversarial content in the user role limits its ability to override system instructions.

The second layer is output schema enforcement. All AI calls that are expected to return structured data (intent objects, action plans, extracted action items) use JSON schema validation. If the model returns output that does not conform to the expected schema — including outputs that appear to contain injected instructions rather than structured data — the response is rejected and the user receives an error rather than Alex executing an unintended action.

The third layer is the confirmation gate. Even if a prompt injection were to succeed in producing a malformed intent object that passes schema validation, the resulting action plan would be presented to the user for confirmation before execution. A user reviewing a plan preview would see any anomalous action (e.g., "Send email to unknown-attacker@example.com") before it executes.

---

## 9.0 Security Checklist

### 9.1 Pre-Launch Security Checklist

The following items must be verified as complete before any public deployment of Alex v1.0. Each item is assigned an owner and a verification method.

**Authentication & Access Control**
- [ ] Supabase Auth configured with email/password and Google OAuth providers. Verified by: manual login test with both methods.
- [ ] JWT validation enforced on every FastAPI endpoint except `GET /health`. Verified by: Postman test sending requests without a token to every endpoint.
- [ ] Row Level Security policies applied to every user-scoped table. Verified by: direct Supabase SQL queries attempting to read user B's data while authenticated as user A.
- [ ] Service role key absent from all frontend code, browser network requests, and client-side environment variables. Verified by: code review and browser network inspector.
- [ ] Refresh token stored in HttpOnly, Secure, SameSite=Strict cookie only. Verified by: browser DevTools inspection confirming token is not accessible via `document.cookie` or `localStorage`.

**Encryption & Secrets**
- [ ] All sensitive credentials stored in Supabase Vault. Verified by: code review confirming no credentials in application database, Redis, or logs.
- [ ] Doppler configured for all three environments (development, staging, production) with no secrets in `.env` files committed to the repository. Verified by: GitHub search for common secret patterns in repository history.
- [ ] TLS enforced on all external connections. Verified by: SSL Labs test on production domain; curl requests to HTTP endpoint confirming redirect to HTTPS.
- [ ] Security headers present on all responses. Verified by: securityheaders.com scan of production domain.
- [ ] SMTP connection using STARTTLS on port 587. Verified by: Wireshark capture of SMTP connection confirming TLS upgrade.

**API Security**
- [ ] Rate limiting active on all endpoints. Verified by: automated test sending 70 requests/minute to the command endpoint and confirming 429 response.
- [ ] Pydantic validation rejecting malformed request bodies. Verified by: Postman tests sending invalid inputs to every endpoint.
- [ ] SQL injection not possible via ORM parameterisation. Verified by: OWASP ZAP automated scan and manual test of known injection payloads.
- [ ] Twilio webhook signature verification active. Verified by: test sending an unsigned request to the Twilio webhook endpoint and confirming 401 response.
- [ ] Path traversal inputs rejected. Verified by: test sending `../etc/passwd` as a file path and confirming 400 response.

**Data & Privacy**
- [ ] Email body content not present in any database table, audit log, or Redis key. Verified by: database inspection after a test email send.
- [ ] Voice command audio not written to disk. Verified by: file system inspection of the Railway container after a voice command.
- [ ] Audit logs populated correctly after every action. Verified by: manual audit log inspection after each action type.
- [ ] Data export feature returns complete, accurate user data. Verified by: end-to-end test of export, verification of all expected fields present.
- [ ] Account deletion removes all user data within 24 hours. Verified by: test account deletion followed by database query confirming zero rows for deleted user ID.

**Infrastructure**
- [ ] Sentry data scrubbing rules active for known sensitive field names. Verified by: trigger a test error containing a mock API key and confirm it is scrubbed in Sentry.
- [ ] n8n webhook endpoints require shared secret. Verified by: test sending a request without the secret and confirming 401 response.
- [ ] Redis does not contain any credential values. Verified by: `redis-cli KEYS *` inspection confirming no credential-pattern keys.
- [ ] GitHub Actions CI pipeline fails on any lint error or test failure. Verified by: intentionally introduce a lint error and confirm CI fails.

### 9.2 Regular Security Audit Schedule

| Activity | Frequency | Owner |
|----------|-----------|-------|
| API key rotation check (Doppler) | Weekly (automated, GitHub Actions) | DevOps |
| Supabase RLS policy review | Every pull request adding or modifying a table | Engineering lead |
| Dependency vulnerability scan (`uv audit`, `pnpm audit`) | Weekly (automated, GitHub Actions) | DevOps |
| OWASP ZAP dynamic scan of production API | Monthly | Security lead |
| Review of audit_logs for anomalous patterns | Monthly | Engineering lead |
| Sentry error volume review | Weekly | Engineering lead |
| Rate limit configuration review | Quarterly | Engineering lead |
| Full pre-launch security checklist re-run | Before every major release | Security lead |
| Third-party service security advisory review (Supabase, Railway, Twilio) | Monthly | DevOps |

---

## 10.0 Incident Response Plan

### 10.1 Incident Classification

| Severity | Definition | Examples |
|----------|-----------|---------|
| **Critical** | Active exfiltration of user credentials or personal data; unauthorised action execution; full service unavailability | Supabase Vault breach; SMTP credential theft; RLS bypass enabling cross-user data access |
| **High** | Suspected compromise; partial data exposure; significant degraded functionality | JWT not validating correctly; AI model returning anomalous actions; Sentry reporting credential pattern in logs |
| **Medium** | Non-critical data exposure; single user affected; functionality impaired but not breached | Rate limiting not enforcing correctly; OAuth token expiry causing calendar unavailability |
| **Low** | Minor configuration drift; non-sensitive log information leakage; dependency vulnerability with no known exploit | Outdated dependency version; missing security header on one endpoint |

### 10.2 Response Procedure by Severity

**Critical — Immediate Response (within 30 minutes)**

The first step is containment: revoke the compromised credential or disable the affected component immediately. If a Supabase Vault breach is suspected, rotate all Vault secrets immediately and invalidate all active Supabase Auth sessions, forcing all users to re-authenticate. If the FastAPI API key is suspected compromised, redeploy Railway with a new key, which immediately invalidates all existing frontend connections. If the SMTP credentials are compromised, revoke the app password directly in the user's Google account, then update the Vault secret.

After containment, assess the blast radius: identify which records, credentials, or actions were potentially affected using the audit_logs table, Sentry events, and Railway application logs. Document the timeline of events.

Notify the affected user within 24 hours with a plain-language description of what occurred, what data may have been affected, what immediate steps have been taken, and what actions the user should take (e.g., changing their email password if SMTP credentials were exposed).

Conduct a post-mortem within 72 hours of resolution to identify the root cause and add the necessary control to the security checklist and this document.

**High — Response within 4 hours**

Investigate the suspected compromise using audit logs and Sentry. Apply targeted containment (e.g., disable the specific endpoint, invalidate the specific user's session) rather than a full shutdown. Notify the user if personal data is potentially involved. Document findings and update the relevant security control.

**Medium and Low — Response within 48 hours**

Log the issue in the project's issue tracker. Apply the fix in the next planned release cycle. Update the security checklist if a new check type is identified.

### 10.3 Post-Breach Recovery Checklist

After any Critical or High incident is contained, the following recovery steps apply before service is restored:

1. Rotate all credentials that could have been exposed in the incident scope.
2. Audit all audit_log entries from the 24 hours prior to incident detection for unauthorised actions.
3. Verify RLS policies are intact and no table policies have been modified.
4. Confirm Sentry data scrubbing rules are active and not bypassed.
5. Run the full pre-launch security checklist (§9.1) before restoring full service.
6. Update the threat model (§8.1) with the new attack vector if not previously documented.
7. Communicate clearly to the affected user what was restored and what permanent risk (if any) remains.

---

## 11.0 Open Questions

| # | Question | Owner | Resolution Target |
|---|----------|-------|------------------|
| SEC-OQ-1 | Redis communication between FastAPI and the Redis service on Railway uses Railway's private internal network without application-level TLS. Is this acceptable, or should Redis connections be TLS-encrypted even on the private network? Supabase Transit Encryption does add TLS to PostgreSQL connections; Railway does not provide equivalent transparent TLS on internal Redis. | Engineering | Before production deployment |
| SEC-OQ-2 | The account deletion process deletes data within 24 hours. Should the process be synchronous (immediate deletion on request) or asynchronous (queued Celery job)? Synchronous deletion provides stronger privacy guarantees; asynchronous allows for a revocation window in case the user acts accidentally. | Product | Before account deletion feature development |
| SEC-OQ-3 | Meeting audio recordings are stored in Supabase Storage for 30 days. For users who record many long meetings, this could accumulate significant personal audio data. Should the retention period be user-configurable (from 0 days to 180 days), or is a fixed 30-day default appropriate? | Product | Before F040 development |
| SEC-OQ-4 | The prompt injection mitigation strategy (§8.2) relies on output schema validation to catch anomalous model responses. This works for structured generation calls (intent parsing, action item extraction) but not for free-text generation (email body, briefing text). Should a secondary content moderation pass be applied to all free-text outputs before they are displayed to the user or dispatched externally? | Engineering / AI | Before AI Instructions Document finalisation |
| SEC-OQ-5 | The confirmation gate has a 60-second TTL on pending plans. If a user is on a mobile connection with intermittent network access, they may lose the confirmation window while reading the plan preview. Should the TTL be configurable per user, or should the 60-second limit be relaxed to 120 seconds for all users? | Product | Before F066 development |
| SEC-OQ-6 | Alex stores the user's file index including file paths, which reveals the directory structure of the user's local machine. In a shared computer scenario, this could expose sensitive path information. Should file path storage be hashed or obfuscated in the index, with plaintext paths held only in Redis for the active session? | Engineering | Before F009 development |

---

## 12.0 Next Steps

With the Security Document complete, all six planning documents for Alex v1.0 are now authored. The following decisions are locked by this document and carried forward to the final artifact:

**Authentication:** Supabase Auth with JWT stored in browser memory and HttpOnly refresh cookie. All endpoints require JWT validation. Google OAuth for calendar integration reuses the same Supabase Auth identity.

**Encryption:** AES-256 at rest on all Supabase infrastructure. TLS 1.3 on all external connections. Credentials stored exclusively in Supabase Vault. Redis holds no sensitive values.

**Permission model:** Four-level system (AUTO / CONFIRM / ELEVATED / RESTRICTED). All external communication actions are CONFIRM level. Account deletion and bulk data operations are ELEVATED. Autonomous execution without confirmation is RESTRICTED in v1.0.

**Data retention:** 90 days for audit logs and conversation memory; 30 days for meeting audio; indefinite for tasks, contacts, and preferences until user deletion.

**Privacy:** Email body content, WhatsApp message body, and voice command audio are never persisted. User can export all data, delete any data, and delete their account at any time.

The final document to author is the **AI Instructions Document (v1.0)**, which specifies the prompt templates, output schemas, and behavioural constraints for every AI-powered feature. It must reflect the prompt injection mitigations described in §8.2 of this document — specifically that user-controlled content is always placed in the user message role and never in the system prompt, and that all structured generation calls use schema-validated JSON output.

---

*Document maintained by the Alex Build Team. All security controls defined here are minimum requirements. Any implementation that provides weaker guarantees than those defined in this document requires explicit sign-off from the security lead before deployment. Version history tracked in the project changelog.*
