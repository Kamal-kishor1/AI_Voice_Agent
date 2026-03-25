# Authentication Requirements Document

**File name:** AUTHENTICATION_REQUIREMENT_DOCUMENT.md
**Version:** v1.0
**Date:** 24 March 2026

---

## 1.0 Purpose & Scope

This document defines the complete authentication, authorization, and session management architecture for Antigravity (Alex AI Voice Assistant). It covers every auth method, token lifecycle, permission model, security hardening measure, and compliance requirement. It acts as the security contract between the engineering, security, and DevOps teams.

---

## 2.0 Authentication Overview

### Authentication strategy chosen and why

| Factor | JWT + OAuth 2.0 | Session Cookies | Verdict |
|--------|-----------------|-----------------|---------|
| Stateless scalability | Tokens self-contained, no server-side session store needed | Requires sticky sessions or centralized store | ✅ JWT |
| Mobile/API compatibility | Bearer tokens work everywhere | Cookie handling complex on native apps | ✅ JWT |
| Third-party OAuth | Native OAuth 2.0 token exchange | Cookie wrapping adds complexity | ✅ JWT |
| Real-time (WebSocket) | Token passed on connection handshake | Cookie partitioning issues | ✅ JWT |

**Decision: JWT (RS256) + OAuth 2.0 Authorization Code Flow** — best fit for a multi-platform (web, mobile, API) AI assistant with real-time voice/chat features.

### Supported auth methods

| Method | Use Case | Priority |
|--------|----------|----------|
| Email & Password | Primary authentication | P0 (Launch) |
| Google OAuth 2.0 | Social login + Calendar integration | P0 (Launch) |
| GitHub OAuth 2.0 | Developer-facing login | P1 (Post-launch) |
| Magic Link / OTP | Passwordless alternative | P1 (Post-launch) |
| API Key | Service-to-service, CI/CD | P1 (Post-launch) |
| MFA (TOTP) | Additional security layer | P1 (Post-launch) |

### Authentication flow diagram

```text
┌─────────────┐
│   Client     │
│ (Web/Mobile) │
└──────┬──────┘
       │
       │  1. POST /v1/auth/login { email, password }
       │     OR
       │  1. OAuth redirect → Google/GitHub
       ▼
┌──────────────────────┐
│   API Gateway        │
│   (Rate Limiter)     │
└──────────┬───────────┘
           │
           │  2. Route to Auth Service
           ▼
┌──────────────────────┐     ┌────────────────┐
│   Auth Controller    │────▶│  Password      │
│                      │     │  Hasher        │
│   - Validate creds   │     │  (bcrypt)      │
│   - Check MFA        │     └────────────────┘
│   - Issue tokens     │
└──────────┬───────────┘
           │
           │  3. Generate tokens
           ▼
┌──────────────────────┐     ┌────────────────┐
│   Token Service      │────▶│  Redis         │
│                      │     │  (Refresh      │
│   - Sign JWT (RS256) │     │   Token Store) │
│   - Store refresh    │     └────────────────┘
└──────────┬───────────┘
           │
           │  4. Return { access_token, refresh_token }
           ▼
┌──────────────────────┐
│   Client stores:     │
│   - access_token     │
│     (memory)         │
│   - refresh_token    │
│     (httpOnly cookie │
│      or secure store)│
└──────────────────────┘
```

---

## 3.0 Authentication Methods

### 3.1 Email & Password

#### Password requirements

| Rule | Specification |
|------|--------------|
| Minimum length | 10 characters |
| Maximum length | 128 characters |
| Uppercase required | ≥ 1 |
| Lowercase required | ≥ 1 |
| Digit required | ≥ 1 |
| Special character required | ≥ 1 (`!@#$%^&*()_+-=[]{}` etc.) |
| Common password check | Reject top 100,000 breached passwords (via k-anonymity HaveIBeenPwned API) |
| Username in password | Rejected |

#### Hashing algorithm

| Parameter | Value |
|-----------|-------|
| Algorithm | **bcrypt** |
| Cost factor (work factor) | 12 rounds |
| Output | 60-character hash string |

**Why bcrypt:** Purpose-built for passwords, intentionally slow, resistant to GPU/ASIC brute force. Argon2id is the alternative for future migration.

#### Salt strategy

bcrypt generates a **unique random 16-byte salt per hash** automatically embedded in the output string. No separate salt column is needed.

```text
$2b$12$LJ3m4ys8Kq5VWx0zN8kRZuK7JcYBmKp9XfA1rJDlQp3HxTkv6Wqy
 ││  ││ └─── 22-char salt ─────────┘└─── 31-char hash ──────────┘
 ││  └── cost factor (12)
 └── algorithm (2b = bcrypt)
```

#### Email & password login flow

```text
Client                          Server
  │                                │
  │  POST /v1/auth/login           │
  │  { email, password }           │
  │───────────────────────────────▶│
  │                                │── 1. Lookup user by email
  │                                │── 2. bcrypt.verify(password, hash)
  │                                │── 3. Check is_active == true
  │                                │── 4. Check MFA enrollment
  │                                │      ├─ If MFA: return mfa_token
  │                                │      └─ If no MFA: issue tokens
  │                                │── 5. Log auth event
  │  { access_token,               │
  │    refresh_token }             │
  │◀───────────────────────────────│
```

---

### 3.2 OAuth Providers

#### Google OAuth flow

```text
Client                    Server                     Google
  │                          │                          │
  │ 1. Click "Login with     │                          │
  │    Google"               │                          │
  │─────────────────────────▶│                          │
  │                          │ 2. Redirect to Google    │
  │                          │    OAuth consent screen  │
  │◀─────────────────────────│──────────────────────────▶
  │                          │                          │
  │ 3. User authorizes       │                          │
  │                          │                          │
  │ 4. Google redirects with │                          │
  │    authorization_code    │                          │
  │─────────────────────────▶│                          │
  │                          │ 5. Exchange code for     │
  │                          │    Google tokens         │
  │                          │─────────────────────────▶│
  │                          │◀─────────────────────────│
  │                          │    { id_token,           │
  │                          │      access_token }      │
  │                          │                          │
  │                          │ 6. Decode id_token:      │
  │                          │    extract email, name   │
  │                          │                          │
  │                          │ 7. Find or create user   │
  │                          │ 8. Issue OUR JWT tokens  │
  │                          │                          │
  │  { access_token,         │                          │
  │    refresh_token }       │                          │
  │◀─────────────────────────│                          │
```

**Google OAuth config:**

| Parameter | Value |
|-----------|-------|
| Scopes | `openid email profile https://www.googleapis.com/auth/calendar` |
| Redirect URI | `https://api.antigravity.ai/v1/auth/oauth/google/callback` |
| Grant type | Authorization Code (with PKCE for mobile) |
| Token storage | Google refresh token stored encrypted in `user_oauth_tokens` table for Calendar API access |

#### GitHub OAuth flow

Same Authorization Code flow as Google. Scopes: `read:user`, `user:email`.

#### Token exchange process

1. Client receives `authorization_code` from provider redirect.
2. Server exchanges code for provider tokens (server-side, never exposed to client).
3. Server extracts user identity from provider's `id_token` or `/userinfo` endpoint.
4. Server creates/finds local user record.
5. Server issues **our own** JWT access + refresh tokens.
6. Provider tokens are stored encrypted if ongoing API access is needed (e.g., Google Calendar).

---

### 3.3 Magic Link / OTP

#### Flow design

```text
Client                       Server                      Email/SMS
  │                             │                            │
  │ POST /v1/auth/magic-link    │                            │
  │ { email }                   │                            │
  │────────────────────────────▶│                            │
  │                             │ 1. Generate 6-digit OTP    │
  │                             │    + unique magic token    │
  │                             │ 2. Hash OTP, store in      │
  │                             │    Redis with TTL          │
  │                             │ 3. Send email/SMS          │
  │                             │───────────────────────────▶│
  │  "Check your email"         │                            │
  │◀────────────────────────────│                            │
  │                             │                            │
  │ User clicks link OR         │                            │
  │ enters OTP code             │                            │
  │────────────────────────────▶│                            │
  │                             │ 4. Verify OTP/token        │
  │                             │ 5. Issue JWT tokens        │
  │  { access_token,            │                            │
  │    refresh_token }          │                            │
  │◀────────────────────────────│                            │
```

#### Expiry rules

| Parameter | Value |
|-----------|-------|
| OTP validity | 10 minutes |
| Magic link validity | 15 minutes |
| Single use | Yes — token invalidated after first successful verification |
| Max OTP length | 6 digits |

#### Rate limiting

| Rule | Limit |
|------|-------|
| OTP requests per email | 3 per 15 minutes |
| Failed OTP verifications | 5 attempts then lockout 30 minutes |

---

### 3.4 API Key Authentication

#### Use case

Service-to-service communication, CI/CD pipelines, and programmatic access where OAuth flows are impractical.

#### Key format

```text
ag_live_k1_a4f8b2c9e1d3f5a7b9c1d3e5f7a9b1c3
│   │    │  └──── 32-char random hex ────────┘
│   │    └── key version
│   └── environment (live/test)
└── prefix (antigravity)
```

#### Key management

| Aspect | Rule |
|--------|------|
| Storage | SHA-256 hash stored in DB; raw key shown only once at creation |
| Rotation | Manual rotation via dashboard; old key grace period: 24 hours |
| Scoping | Keys can be scoped to specific endpoints/actions |
| Max keys per user | 5 |
| Revocation | Immediate via `DELETE /v1/settings/api-keys/{key_id}` |

**API key is sent via header:**
```http
Authorization: Bearer ag_live_k1_a4f8b2c9e1d3f5a7b9c1d3e5f7a9b1c3
```

---

## 4.0 Token System

### 4.1 Access Token

#### Format: JWT (JSON Web Token)

#### Signing algorithm

| Parameter | Value |
|-----------|-------|
| Algorithm | **RS256** (RSA + SHA-256) |
| Key size | 2048 bits |
| Public key | Published at `/.well-known/jwks.json` for external verification |

**Why RS256 over HS256:** Asymmetric keys allow microservices to verify tokens with the public key without sharing the private signing secret.

#### Payload structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "key-2026-03"
  },
  "payload": {
    "sub": "a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
    "email": "kamal@example.com",
    "name": "Kamal Kishor",
    "role": "user",
    "iat": 1711274400,
    "exp": 1711278000,
    "iss": "https://api.antigravity.ai",
    "aud": "antigravity-client",
    "jti": "tok_7f8a9b0c1d2e3f4a"
  }
}
```

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | UUID | User ID |
| `email` | string | User email |
| `name` | string | Display name |
| `role` | string | `user` or `admin` |
| `iat` | number | Issued at (Unix timestamp) |
| `exp` | number | Expiry (Unix timestamp) |
| `iss` | string | Issuer URL |
| `aud` | string | Intended audience |
| `jti` | string | Unique token ID (for revocation) |

#### Expiry time

| Token | Validity |
|-------|----------|
| Access token | **1 hour** |
| Refresh token | **30 days** |
| Magic link token | 15 minutes |
| OTP code | 10 minutes |
| MFA session token | 5 minutes |

---

### 4.2 Refresh Token

#### Storage strategy

| Platform | Storage |
|----------|---------|
| Web (browser) | `httpOnly`, `Secure`, `SameSite=Strict` cookie |
| Mobile app | OS secure storage (Keychain / Keystore) |
| Server-side | SHA-256 hash stored in Redis + PostgreSQL `refresh_tokens` table |

#### Rotation policy

**Rotating refresh tokens:** Every time a refresh token is used to obtain a new access token, a **new refresh token** is also issued and the old one is invalidated.

```text
Client                         Server
  │                               │
  │  POST /v1/auth/refresh        │
  │  { refresh_token: RT_old }    │
  │──────────────────────────────▶│
  │                               │── 1. Validate RT_old
  │                               │── 2. Invalidate RT_old
  │                               │── 3. Issue new AT + RT_new
  │  { access_token: AT_new,      │
  │    refresh_token: RT_new }    │
  │◀──────────────────────────────│
```

**Reuse detection:** If an already-invalidated refresh token is presented, it indicates token theft. The server immediately revokes the **entire token family** (all refresh tokens for that user session) and forces re-authentication.

#### Revocation process

1. `POST /v1/auth/logout` revokes the current access + refresh tokens.
2. Token `jti` is added to a Redis blocklist with TTL matching the token's remaining validity.
3. All middleware checks the blocklist before accepting a token.

---

### 4.3 Token Validation

#### Validation steps (executed on every authenticated request)

```text
1. Extract token from Authorization header
2. Decode JWT header (check alg = RS256)
3. Verify signature using public key
4. Check `exp` claim → reject if expired
5. Check `iss` claim → must match our issuer
6. Check `aud` claim → must match our audience
7. Check `jti` against Redis blocklist → reject if revoked
8. Extract `sub` (user ID) and `role` for authorization
9. Attach user context to request
```

#### Failure handling

| Failure | Response | Client Action |
|---------|----------|--------------|
| Missing token | `401 AUTH_TOKEN_MISSING` | Redirect to login |
| Malformed token | `401 AUTH_TOKEN_INVALID` | Redirect to login |
| Expired token | `401 AUTH_TOKEN_EXPIRED` | Attempt silent refresh |
| Revoked token | `401 AUTH_TOKEN_REVOKED` | Force re-login |
| Wrong audience | `401 AUTH_TOKEN_INVALID` | Redirect to login |

---

## 5.0 Session Management

### Session creation

A "session" is represented by a refresh token family. On login, a new session record is created:

```json
{
  "session_id": "sess_a1b2c3d4",
  "user_id": "a1b2c3d4-...",
  "device_info": "Chrome 120 / Windows 11",
  "ip_address": "203.0.113.42",
  "created_at": "2026-03-24T10:00:00Z",
  "last_active_at": "2026-03-24T12:30:00Z",
  "is_active": true
}
```

### Session storage

| Store | Data |
|-------|------|
| PostgreSQL `sessions` table | Session metadata (device, IP, timestamps) |
| Redis | Active session lookup, refresh token hash, blocklist |

### Session expiry

| Rule | Value |
|------|-------|
| Absolute timeout | 30 days (matches refresh token) |
| Idle timeout | 7 days without any refresh |
| After password change | All other sessions revoked |

### Concurrent session rules

| Rule | Specification |
|------|--------------|
| Max concurrent sessions | 5 per user |
| Exceeded behavior | Oldest session is automatically revoked |
| Admin override | Admins can revoke any user session |

### Session revocation

Users can view and revoke sessions via `GET /v1/settings/sessions` and `DELETE /v1/settings/sessions/{session_id}`.

---

## 6.0 Authorization System

### 6.1 Role definitions

| Role | Description | Assignment |
|------|-------------|------------|
| `user` | Standard user with access to own data | Default on registration |
| `admin` | Full system access, user management, system health | Manually assigned |

### 6.2 Permission matrix

| Resource | Action | `user` | `admin` |
|----------|--------|--------|---------|
| **Users** | Create (register) | ✅ (self only) | ✅ |
| **Users** | Read profile | ✅ (self only) | ✅ (any) |
| **Users** | Update profile | ✅ (self only) | ✅ (any) |
| **Users** | Delete account | ✅ (self only) | ✅ (any) |
| **Users** | List all users | ❌ | ✅ |
| **Users** | Deactivate | ❌ | ✅ |
| **Conversations** | Create | ✅ | ✅ |
| **Conversations** | Read | ✅ (own only) | ✅ (any) |
| **Conversations** | Delete | ✅ (own only) | ✅ (any) |
| **Messages** | Send | ✅ | ✅ |
| **Messages** | Read | ✅ (own conv) | ✅ (any) |
| **Calendar Events** | Create | ✅ | ✅ |
| **Calendar Events** | Read | ✅ (own only) | ✅ (any) |
| **Calendar Events** | Update | ✅ (own only) | ✅ (any) |
| **Calendar Events** | Delete | ✅ (own only) | ✅ (any) |
| **Tasks** | Create | ✅ | ✅ |
| **Tasks** | Read | ✅ (own only) | ✅ (any) |
| **Tasks** | Update | ✅ (own only) | ✅ (any) |
| **Tasks** | Delete | ✅ (own only) | ✅ (any) |
| **Reminders** | Create | ✅ | ✅ |
| **Reminders** | Read | ✅ (own only) | ✅ (any) |
| **Reminders** | Dismiss | ✅ (own only) | ✅ (any) |
| **Contacts** | CRUD | ✅ (own only) | ✅ (any) |
| **Files** | Upload | ✅ | ✅ |
| **Files** | Read / Download | ✅ (own only) | ✅ (any) |
| **Files** | Search | ✅ (own only) | ✅ (any) |
| **Files** | Delete | ✅ (own only) | ✅ (any) |
| **Communications** | Send email | ✅ | ✅ |
| **Communications** | Send WhatsApp | ✅ | ✅ |
| **Settings** | Read preferences | ✅ (own only) | ✅ (any) |
| **Settings** | Update preferences | ✅ (own only) | ✅ (any) |
| **Settings** | Integrations | ✅ (own only) | ✅ (any) |
| **Admin** | Health check | ❌ | ✅ |
| **Admin** | System config | ❌ | ✅ |

### 6.3 Resource ownership rules

- Every resource has a `user_id` foreign key.
- Middleware automatically scopes queries: `WHERE user_id = current_user.id`.
- Direct UUID access to another user's resource → `404 RESOURCE_NOT_FOUND` (not `403`, to prevent enumeration).

### 6.4 Admin override rules

- Admins bypass ownership checks.
- Admin actions are logged with `actor_id` in the audit trail.
- Admin cannot delete their own admin role (prevents lockout).

---

## 7.0 Security Measures

### 7.1 Brute force protection

| Parameter | Value |
|-----------|-------|
| Max failed login attempts | 5 per account per 15 minutes |
| Lockout duration | 30 minutes (progressive) |
| Progressive delays | Attempt 3: 2s delay, Attempt 4: 5s delay, Attempt 5: lockout |
| IP-based rate limit | 20 login attempts per IP per 15 minutes |
| Notification | Email alert sent to user after 3 failed attempts |

#### Lockout flow

```text
Attempt 1: Instant response → "Invalid credentials"
Attempt 2: Instant response → "Invalid credentials"
Attempt 3: 2-second delay  → "Invalid credentials"
Attempt 4: 5-second delay  → "Invalid credentials"
Attempt 5: Account locked  → "Account locked for 30 minutes"
           └─ Email: "Suspicious login attempt detected"
```

### 7.2 CSRF protection

| Strategy | Implementation |
|----------|---------------|
| Primary | SameSite=Strict cookies for refresh tokens |
| Secondary | Double-submit CSRF token pattern for state-changing requests from web |
| API clients | Not applicable (Bearer token auth, not cookies) |

### 7.3 XSS prevention

| Measure | Implementation |
|---------|---------------|
| Output encoding | All user-generated content HTML-escaped before rendering |
| Content-Security-Policy | `default-src 'self'; script-src 'self'` |
| X-Content-Type-Options | `nosniff` |
| HttpOnly cookies | Refresh tokens inaccessible to JavaScript |
| Input sanitization | DOMPurify on frontend, bleach on backend |

### 7.4 SQL injection prevention

| Measure | Implementation |
|---------|---------------|
| ORM usage | SQLAlchemy parameterized queries exclusively |
| No raw SQL | Raw SQL forbidden in codebase; enforced via linter rule |
| Input validation | Pydantic models validate and type-coerce all inputs |

### 7.5 Rate limiting on auth endpoints

| Endpoint | Limit |
|----------|-------|
| `POST /v1/auth/register` | 5 req/min per IP |
| `POST /v1/auth/login` | 10 req/min per IP |
| `POST /v1/auth/refresh` | 15 req/min per user |
| `POST /v1/auth/magic-link` | 3 req/15min per email |
| `POST /v1/auth/mfa/verify` | 5 req/5min per user |
| `POST /v1/auth/password/reset` | 3 req/hour per email |

---

## 8.0 Multi-Factor Authentication

### MFA methods supported

| Method | Priority | Mechanism |
|--------|----------|-----------|
| TOTP (Time-based OTP) | P1 | Google Authenticator / Authy compatible |
| Backup recovery codes | P1 | 10 one-time-use codes |

### MFA enrollment flow

```text
Client                          Server
  │                                │
  │ POST /v1/auth/mfa/enroll      │
  │──────────────────────────────▶ │
  │                                │── 1. Generate TOTP secret
  │                                │── 2. Generate QR code URI
  │  { secret, qr_code_uri,       │
  │    recovery_codes: [10] }      │
  │◀────────────────────────────── │
  │                                │
  │ User scans QR in app           │
  │                                │
  │ POST /v1/auth/mfa/verify       │
  │ { otp: "482910" }             │
  │──────────────────────────────▶ │
  │                                │── 3. Verify OTP against secret
  │                                │── 4. Mark MFA as active
  │  { mfa_enabled: true }        │
  │◀────────────────────────────── │
```

### MFA login flow

```text
Client                          Server
  │                                │
  │ POST /v1/auth/login            │
  │ { email, password }            │
  │──────────────────────────────▶ │
  │                                │── Password valid + MFA enabled
  │  { mfa_required: true,        │
  │    mfa_token: "mfa_temp_..." } │
  │◀────────────────────────────── │
  │                                │
  │ POST /v1/auth/mfa/challenge    │
  │ { mfa_token, otp: "482910" }  │
  │──────────────────────────────▶ │
  │                                │── Verify TOTP
  │  { access_token,              │
  │    refresh_token }             │
  │◀────────────────────────────── │
```

### MFA bypass rules

- MFA cannot be bypassed.
- Admins can disable a user's MFA only after identity verification (support ticket + email confirmation).

### Recovery codes

| Parameter | Value |
|-----------|-------|
| Count | 10 codes generated at enrollment |
| Format | 8-character alphanumeric (e.g., `A3K9-M2P7`) |
| Usage | Each code is single-use |
| Storage | bcrypt-hashed in DB |
| Regeneration | User can regenerate all codes (invalidates old ones) |

---

## 9.0 Password Management

### Reset flow

```text
Client                       Server                      Email
  │                             │                           │
  │ POST /v1/auth/password/     │                           │
  │       reset-request         │                           │
  │ { email }                   │                           │
  │────────────────────────────▶│                           │
  │                             │── 1. Generate reset token │
  │                             │── 2. Hash, store in Redis │
  │                             │      (TTL: 1 hour)        │
  │                             │── 3. Send reset email     │
  │                             │──────────────────────────▶│
  │  "Check your email"         │                           │
  │◀────────────────────────────│                           │
  │                             │                           │
  │ User clicks reset link      │                           │
  │                             │                           │
  │ POST /v1/auth/password/     │                           │
  │       reset-confirm         │                           │
  │ { token, new_password }     │                           │
  │────────────────────────────▶│                           │
  │                             │── 4. Verify token         │
  │                             │── 5. Hash new password    │
  │                             │── 6. Invalidate all       │
  │                             │      existing sessions    │
  │  "Password reset complete"  │                           │
  │◀────────────────────────────│                           │
```

### Change password flow

`PUT /v1/users/me/password` — requires `current_password` verification before accepting `new_password`. All other sessions revoked on success.

### Password history rules

| Rule | Value |
|------|-------|
| History depth | Last 5 passwords stored (hashed) |
| Reuse prevention | New password must not match any of the last 5 |

### Compromised password check

Before accepting any new password (registration, change, reset), the server checks the password against the **HaveIBeenPwned Passwords API** using the **k-anonymity** model (only first 5 chars of SHA-1 hash sent; full password never leaves server).

---

## 10.0 Audit & Logging

### What auth events are logged

| Event | Severity | Details Captured |
|-------|----------|-----------------|
| `auth.login.success` | INFO | user_id, IP, device, method (password/oauth/magic_link) |
| `auth.login.failure` | WARN | email_attempted, IP, failure_reason |
| `auth.logout` | INFO | user_id, session_id |
| `auth.token.refresh` | INFO | user_id, session_id |
| `auth.token.revoked` | WARN | user_id, reason (manual/password_change/theft_detection) |
| `auth.password.reset_request` | INFO | email, IP |
| `auth.password.changed` | WARN | user_id, IP |
| `auth.mfa.enrolled` | INFO | user_id |
| `auth.mfa.challenge.success` | INFO | user_id |
| `auth.mfa.challenge.failure` | WARN | user_id, IP |
| `auth.account.locked` | ALERT | email, IP, attempt_count |
| `auth.account.deleted` | ALERT | user_id, IP |
| `auth.session.revoked` | WARN | user_id, session_id, revoked_by |
| `auth.admin.action` | ALERT | admin_id, target_user_id, action |

### Log format

```json
{
  "timestamp": "2026-03-24T10:00:00Z",
  "level": "WARN",
  "event": "auth.login.failure",
  "request_id": "req_abc123",
  "ip": "203.0.113.42",
  "user_agent": "Mozilla/5.0...",
  "data": {
    "email_attempted": "kamal@example.com",
    "failure_reason": "INVALID_PASSWORD",
    "attempt_number": 3
  }
}
```

### Log retention

| Log Type | Retention |
|----------|-----------|
| Auth events | 1 year |
| Failed login attempts | 6 months |
| Admin actions | 2 years (compliance) |

### Alert triggers

| Trigger | Action |
|---------|--------|
| 5 failed logins in 15 min | Email user + lock account |
| Login from new country/IP | Email user with location info |
| Refresh token reuse detected | Revoke all sessions + email user |
| Admin deactivates user | Slack alert to security channel |
| Password reset for admin account | Email all admins |

---

## 11.0 Compliance Requirements

### GDPR considerations

| Requirement | Implementation |
|-------------|---------------|
| Right to access | `GET /v1/users/me/data-export` returns all personal data as JSON/ZIP |
| Right to erasure | `DELETE /v1/users/me` triggers 30-day grace period then full data purge |
| Consent tracking | Login consent stored with timestamp and IP |
| Data minimization | Only strictly necessary data collected at registration (email, name, password) |
| Breach notification | Security team alerted within 1 hour; users notified within 72 hours |

### Data residency

| Data Type | Storage Region | Notes |
|-----------|---------------|-------|
| User credentials | Primary DB region (configurable) | Never replicated to unauthorized regions |
| OAuth tokens | Encrypted at rest (AES-256) | Stored in same region as primary DB |
| Audit logs | Same region | Archived to cold storage after retention period |

### Right to deletion impact on auth

When a user exercises right to deletion:
1. User record soft-deleted immediately (blocks login).
2. All sessions revoked.
3. All refresh tokens invalidated.
4. After 30-day grace period: hard delete cascades through all tables.
5. OAuth provider tokens deleted.
6. Audit logs anonymized (user_id replaced with `DELETED_USER_<hash>`).

---

## 12.0 Open Questions

1. **Biometric auth:** Should we support device biometric (Face ID / fingerprint) as an MFA method for mobile apps?
2. **SSO / SAML:** Will enterprise customers need SAML 2.0 SSO integration?
3. **Passkeys / WebAuthn:** Should we prioritize FIDO2 passkeys as a passwordless option over Magic Links?
4. **Token revocation at scale:** Should we move from Redis blocklist to a dedicated token revocation service if the blocklist grows large?
5. **Account recovery:** If a user loses both password and MFA device, what is the identity verification process?

---

## 13.0 Next Steps

1. Implement `auth` module in FastAPI with `POST /login`, `/register`, `/refresh`, `/logout` routes.
2. Generate RS256 key pair and publish JWKS endpoint at `/.well-known/jwks.json`.
3. Integrate Google OAuth using `authlib` or `httpx-oauth`.
4. Setup Redis-backed token blocklist and refresh token storage.
5. Implement brute force protection middleware with progressive delays.
6. Build MFA enrollment and challenge endpoints using `pyotp` library.
7. Configure structured JSON logging for all auth events.
8. Conduct penetration testing on auth endpoints before launch.
