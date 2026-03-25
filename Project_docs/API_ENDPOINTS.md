# API Endpoints Document

**File name:** API_ENDPOINTS.md
**Version:** v1.0
**Date:** 24 March 2026

---

## 1.0 Purpose & Scope

This document provides the exhaustive API contract for the Antigravity (Alex AI Voice Assistant) backend. Every endpoint, its request/response schemas, error codes, rate limits, and webhook designs are defined here. It serves as the single source of truth for frontend engineers, third-party integrators, and QA teams.

---

## 2.0 API Overview

### REST vs GraphQL decision and why

| Factor | REST | GraphQL | Verdict |
|--------|------|---------|---------|
| Simplicity | Straightforward CRUD mapping | Requires schema stitching, resolvers | ✅ REST |
| Caching | Native HTTP caching (CDN, ETag) | Complex cache invalidation | ✅ REST |
| Real-time | WebSocket companion | Subscriptions add complexity | ✅ REST |
| Team familiarity | Industry standard for FastAPI | Strawberry/Ariadne less mature | ✅ REST |
| Over-fetching | Mitigated by `?fields=` sparse fieldsets | Native advantage of GraphQL | Acceptable |

**Decision: REST** — aligns with FastAPI strengths, simplifies caching, and keeps the real-time layer (WebSocket/WebRTC) cleanly separated.

### Base URL structure

```
Production:  https://api.antigravity.ai/v1
Staging:     https://staging-api.antigravity.ai/v1
Development: http://localhost:8000/v1
```

### API versioning strategy

- **URL-path versioning** (`/v1/`, `/v2/`).
- Major version bumps only for breaking changes.
- Deprecated endpoints return `Sunset` header 90 days before removal.

### Content type standards

- Request: `application/json` (except file uploads: `multipart/form-data`)
- Response: `application/json`
- Character encoding: `UTF-8`

---

## 3.0 Global Conventions

### Request format

```json
{
  "field_name": "value",
  "nested_object": {
    "key": "value"
  }
}
```

All field names use `snake_case`.

### Response format (success)

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-03-24T10:00:00Z"
  }
}
```

### Response format (list/paginated)

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 142,
    "total_pages": 8
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-03-24T10:00:00Z"
  }
}
```

### Error response format

```json
{
  "success": false,
  "error": {
    "code": "AUTH_TOKEN_EXPIRED",
    "message": "Your authentication token has expired. Please log in again.",
    "details": null
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-03-24T10:00:00Z"
  }
}
```

### Status codes used

| Code | Meaning | When Used |
|------|---------|-----------|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST creating a resource |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Validation errors, malformed JSON |
| `401` | Unauthorized | Missing or invalid token |
| `403` | Forbidden | Valid token but insufficient permissions |
| `404` | Not Found | Resource does not exist |
| `409` | Conflict | Duplicate resource (e.g., email already registered) |
| `422` | Unprocessable Entity | Semantic validation failure |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unhandled server exception |
| `503` | Service Unavailable | Dependency down (LLM API, external service) |

### Pagination format

Query params: `?page=1&per_page=20`
Defaults: `page=1`, `per_page=20`, max `per_page=100`.

### Filtering & sorting conventions

- Filter: `?status=active&priority=high`
- Sort: `?sort_by=created_at&sort_order=desc`
- Sparse fields: `?fields=id,title,status`

---

## 4.0 Authentication Headers

### Required headers for all authenticated requests

| Header | Format | Description |
|--------|--------|-------------|
| `Authorization` | `Bearer <access_token>` | JWT access token |
| `Content-Type` | `application/json` | Request body format |

### Optional headers

| Header | Format | Description |
|--------|--------|-------------|
| `X-Request-ID` | UUID string | Client-generated trace ID for debugging |
| `Accept-Language` | `en-US` | Preferred response language |
| `X-Device-Type` | `mobile` / `desktop` | Helps tailor response format |

### Header format example

```http
GET /v1/conversations HTTP/1.1
Host: api.antigravity.ai
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

---

## 5.0 API Endpoints

---

### 5.1 Authentication Endpoints

---

#### API001 — Register User

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/auth/register` |
| **Description** | Creates a new user account |
| **Auth required** | No |
| **Rate limit** | 5 req/min per IP |

**Request Body:**
```json
{
  "email": "kamal@example.com",
  "password": "S3cur3P@ss!",
  "full_name": "Kamal Kishor"
}
```

**Success Response (`201 Created`):**
```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
    "email": "kamal@example.com",
    "full_name": "Kamal Kishor",
    "role": "user",
    "created_at": "2026-03-24T10:00:00Z"
  },
  "meta": { "request_id": "req_001", "timestamp": "2026-03-24T10:00:00Z" }
}
```

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `400` | `VALIDATION_ERROR` | Missing/invalid fields |
| `409` | `EMAIL_ALREADY_EXISTS` | Email already registered |

---

#### API002 — Login

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/auth/login` |
| **Description** | Authenticates a user and returns JWT tokens |
| **Auth required** | No |
| **Rate limit** | 10 req/min per IP |

**Request Body:**
```json
{
  "email": "kamal@example.com",
  "password": "S3cur3P@ss!"
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJl...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "a1b2c3d4-...",
      "email": "kamal@example.com",
      "full_name": "Kamal Kishor",
      "role": "user"
    }
  },
  "meta": { "request_id": "req_002", "timestamp": "2026-03-24T10:00:01Z" }
}
```

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `401` | `INVALID_CREDENTIALS` | Wrong email or password |
| `403` | `ACCOUNT_DISABLED` | Account has been deactivated |

---

#### API003 — Refresh Token

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/auth/refresh` |
| **Description** | Exchanges a refresh token for a new access token |
| **Auth required** | No (uses refresh token in body) |
| **Rate limit** | 15 req/min per user |

**Request Body:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJl..."
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...(new)",
    "expires_in": 3600
  },
  "meta": { "request_id": "req_003", "timestamp": "2026-03-24T10:05:00Z" }
}
```

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `401` | `INVALID_REFRESH_TOKEN` | Expired or revoked refresh token |

---

#### API004 — Logout

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/auth/logout` |
| **Description** | Revokes the current access and refresh tokens |
| **Auth required** | Yes |
| **Rate limit** | 10 req/min |

**Request Headers:** `Authorization: Bearer <access_token>`

**Request Body:** None

**Success Response (`204 No Content`):** Empty body.

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `401` | `AUTH_TOKEN_EXPIRED` | Token already expired |

---

### 5.2 User Management Endpoints

---

#### API005 — Get Current User Profile

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/users/me` |
| **Description** | Returns the authenticated user's profile |
| **Auth required** | Yes |
| **Rate limit** | 30 req/min |

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4-...",
    "email": "kamal@example.com",
    "full_name": "Kamal Kishor",
    "avatar_url": "https://cdn.antigravity.ai/avatars/a1b2c3d4.webp",
    "role": "user",
    "is_active": true,
    "last_login_at": "2026-03-24T10:00:01Z",
    "created_at": "2026-03-20T08:00:00Z"
  },
  "meta": { "request_id": "req_005", "timestamp": "2026-03-24T10:06:00Z" }
}
```

---

#### API006 — Update User Profile

| Property | Value |
|----------|-------|
| **Method** | `PATCH` |
| **URL** | `/v1/users/me` |
| **Description** | Updates the authenticated user's profile fields |
| **Auth required** | Yes |
| **Rate limit** | 10 req/min |

**Request Body:**
```json
{
  "full_name": "Kamal K.",
  "avatar_url": "https://cdn.antigravity.ai/avatars/new.webp"
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4-...",
    "email": "kamal@example.com",
    "full_name": "Kamal K.",
    "avatar_url": "https://cdn.antigravity.ai/avatars/new.webp",
    "updated_at": "2026-03-24T10:07:00Z"
  },
  "meta": { "request_id": "req_006", "timestamp": "2026-03-24T10:07:00Z" }
}
```

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `400` | `VALIDATION_ERROR` | Invalid field value |

---

#### API007 — Change Password

| Property | Value |
|----------|-------|
| **Method** | `PUT` |
| **URL** | `/v1/users/me/password` |
| **Description** | Changes the authenticated user's password |
| **Auth required** | Yes |
| **Rate limit** | 5 req/min |

**Request Body:**
```json
{
  "current_password": "S3cur3P@ss!",
  "new_password": "N3wS3cur3P@ss!"
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": { "message": "Password updated successfully." },
  "meta": { "request_id": "req_007", "timestamp": "2026-03-24T10:08:00Z" }
}
```

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `400` | `WEAK_PASSWORD` | New password doesn't meet complexity rules |
| `401` | `INVALID_CREDENTIALS` | Current password is wrong |

---

#### API008 — Delete Account

| Property | Value |
|----------|-------|
| **Method** | `DELETE` |
| **URL** | `/v1/users/me` |
| **Description** | Soft-deletes the user account and schedules data purge |
| **Auth required** | Yes |
| **Rate limit** | 2 req/day |

**Request Body:**
```json
{
  "confirmation": "DELETE MY ACCOUNT"
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "message": "Account scheduled for deletion. You have 30 days to recover.",
    "deletion_date": "2026-04-23T10:00:00Z"
  },
  "meta": { "request_id": "req_008", "timestamp": "2026-03-24T10:09:00Z" }
}
```

---

### 5.3 Core Feature Endpoints — Conversations & AI

---

#### API009 — List Conversations

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/conversations` |
| **Description** | Returns paginated list of user's conversations |
| **Auth required** | Yes |
| **Rate limit** | 30 req/min |

**Query Params:** `?page=1&per_page=20&status=active&sort_by=updated_at&sort_order=desc`

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "id": "e5f6a7b8-...",
      "title": "Schedule team sync",
      "status": "active",
      "updated_at": "2026-03-24T10:05:00Z",
      "created_at": "2026-03-24T09:00:00Z"
    }
  ],
  "pagination": { "page": 1, "per_page": 20, "total_items": 5, "total_pages": 1 },
  "meta": { "request_id": "req_009", "timestamp": "2026-03-24T10:10:00Z" }
}
```

---

#### API010 — Create Conversation

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/conversations` |
| **Description** | Starts a new conversation thread |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Request Body:**
```json
{
  "title": "Plan weekend trip"
}
```

**Success Response (`201 Created`):**
```json
{
  "success": true,
  "data": {
    "id": "conv_new123-...",
    "title": "Plan weekend trip",
    "status": "active",
    "created_at": "2026-03-24T10:11:00Z"
  },
  "meta": { "request_id": "req_010", "timestamp": "2026-03-24T10:11:00Z" }
}
```

---

#### API011 — Get Conversation Messages

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/conversations/{conversation_id}/messages` |
| **Description** | Returns paginated messages for a conversation |
| **Auth required** | Yes |
| **Rate limit** | 60 req/min |

**Path Params:** `conversation_id` (UUID)
**Query Params:** `?page=1&per_page=50`

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "id": "m1n2o3p4-...",
      "role": "user",
      "content": "Book a meeting with Raj tomorrow at 3 PM",
      "intent": "schedule_meeting",
      "confidence": 0.96,
      "created_at": "2026-03-24T10:12:00Z"
    },
    {
      "id": "m5n6o7p8-...",
      "role": "assistant",
      "content": "I've scheduled a meeting with Raj for tomorrow at 3:00 PM. A calendar invite has been sent.",
      "intent": null,
      "confidence": null,
      "created_at": "2026-03-24T10:12:02Z"
    }
  ],
  "pagination": { "page": 1, "per_page": 50, "total_items": 2, "total_pages": 1 },
  "meta": { "request_id": "req_011", "timestamp": "2026-03-24T10:12:05Z" }
}
```

---

#### API012 — Send Message (Chat with Alex)

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/conversations/{conversation_id}/messages` |
| **Description** | Sends a user message and returns Alex's AI response |
| **Auth required** | Yes |
| **Rate limit** | 30 req/min |

**Path Params:** `conversation_id` (UUID)

**Request Body:**
```json
{
  "content": "What's on my calendar for tomorrow?",
  "metadata": {
    "input_type": "text"
  }
}
```

**Success Response (`201 Created`):**
```json
{
  "success": true,
  "data": {
    "user_message": {
      "id": "msg_user_01-...",
      "role": "user",
      "content": "What's on my calendar for tomorrow?",
      "intent": "check_calendar",
      "confidence": 0.98,
      "created_at": "2026-03-24T10:15:00Z"
    },
    "assistant_message": {
      "id": "msg_asst_01-...",
      "role": "assistant",
      "content": "You have 2 events tomorrow:\n1. Team Standup at 10:00 AM\n2. Design Review at 2:00 PM",
      "created_at": "2026-03-24T10:15:02Z"
    },
    "actions_triggered": [
      {
        "action_log_id": "act_01-...",
        "action_type": "query_calendar",
        "status": "success"
      }
    ]
  },
  "meta": { "request_id": "req_012", "timestamp": "2026-03-24T10:15:02Z" }
}
```

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `404` | `CONVERSATION_NOT_FOUND` | Invalid conversation ID |
| `503` | `LLM_SERVICE_UNAVAILABLE` | AI model provider is down |

---

#### API013 — Delete Conversation

| Property | Value |
|----------|-------|
| **Method** | `DELETE` |
| **URL** | `/v1/conversations/{conversation_id}` |
| **Description** | Archives/soft-deletes a conversation |
| **Auth required** | Yes |
| **Rate limit** | 10 req/min |

**Success Response (`204 No Content`):** Empty body.

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `404` | `CONVERSATION_NOT_FOUND` | Conversation does not exist |

---

### 5.3.2 Core Feature Endpoints — Calendar

---

#### API014 — List Calendar Events

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/calendar/events` |
| **Description** | Returns events for a date range |
| **Auth required** | Yes |
| **Rate limit** | 30 req/min |

**Query Params:** `?start_date=2026-03-25&end_date=2026-03-26`

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "id": "c1d2e3f4-...",
      "title": "Team Standup",
      "start_time": "2026-03-25T10:00:00Z",
      "end_time": "2026-03-25T10:30:00Z",
      "location": "Google Meet",
      "status": "confirmed",
      "attendees": [
        { "name": "Raj", "email": "raj@co.in", "status": "accepted" }
      ]
    }
  ],
  "meta": { "request_id": "req_014", "timestamp": "2026-03-24T10:20:00Z" }
}
```

---

#### API015 — Create Calendar Event

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/calendar/events` |
| **Description** | Creates a new calendar event and optionally syncs to Google Calendar |
| **Auth required** | Yes |
| **Rate limit** | 15 req/min |

**Request Body:**
```json
{
  "title": "Design Review",
  "start_time": "2026-03-25T14:00:00Z",
  "end_time": "2026-03-25T15:00:00Z",
  "location": "Zoom",
  "attendees": [
    { "name": "Priya", "email": "priya@co.in" }
  ],
  "sync_google": true
}
```

**Success Response (`201 Created`):**
```json
{
  "success": true,
  "data": {
    "id": "cal_new_01-...",
    "title": "Design Review",
    "start_time": "2026-03-25T14:00:00Z",
    "end_time": "2026-03-25T15:00:00Z",
    "external_id": "google_evt_abc123",
    "status": "confirmed",
    "created_at": "2026-03-24T10:21:00Z"
  },
  "meta": { "request_id": "req_015", "timestamp": "2026-03-24T10:21:00Z" }
}
```

---

#### API016 — Update Calendar Event

| Property | Value |
|----------|-------|
| **Method** | `PATCH` |
| **URL** | `/v1/calendar/events/{event_id}` |
| **Description** | Updates an existing calendar event |
| **Auth required** | Yes |
| **Rate limit** | 15 req/min |

**Request Body:**
```json
{
  "title": "Design Review (Updated)",
  "start_time": "2026-03-25T15:00:00Z",
  "end_time": "2026-03-25T16:00:00Z"
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "id": "cal_new_01-...",
    "title": "Design Review (Updated)",
    "start_time": "2026-03-25T15:00:00Z",
    "end_time": "2026-03-25T16:00:00Z",
    "updated_at": "2026-03-24T10:25:00Z"
  },
  "meta": { "request_id": "req_016", "timestamp": "2026-03-24T10:25:00Z" }
}
```

---

#### API017 — Delete Calendar Event

| Property | Value |
|----------|-------|
| **Method** | `DELETE` |
| **URL** | `/v1/calendar/events/{event_id}` |
| **Description** | Cancels a calendar event |
| **Auth required** | Yes |
| **Rate limit** | 10 req/min |

**Success Response (`204 No Content`):** Empty body.

---

### 5.3.3 Core Feature Endpoints — Tasks & Reminders

---

#### API018 — List Tasks

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/tasks` |
| **Description** | Returns user's tasks with filtering and pagination |
| **Auth required** | Yes |
| **Rate limit** | 30 req/min |

**Query Params:** `?status=todo&priority=high&sort_by=due_date&sort_order=asc&page=1&per_page=20`

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "id": "task_01-...",
      "title": "Prepare Q1 report slides",
      "priority": "high",
      "status": "todo",
      "due_date": "2026-03-26T18:00:00Z",
      "source": "meeting_extract",
      "created_at": "2026-03-24T10:00:00Z"
    }
  ],
  "pagination": { "page": 1, "per_page": 20, "total_items": 1, "total_pages": 1 },
  "meta": { "request_id": "req_018", "timestamp": "2026-03-24T10:30:00Z" }
}
```

---

#### API019 — Create Task

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/tasks` |
| **Description** | Creates a new task |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Request Body:**
```json
{
  "title": "Review design mockups",
  "description": "Final review of the Figma screens before dev handoff",
  "priority": "high",
  "due_date": "2026-03-27T12:00:00Z"
}
```

**Success Response (`201 Created`):**
```json
{
  "success": true,
  "data": {
    "id": "task_new_01-...",
    "title": "Review design mockups",
    "priority": "high",
    "status": "todo",
    "due_date": "2026-03-27T12:00:00Z",
    "source": "manual",
    "created_at": "2026-03-24T10:31:00Z"
  },
  "meta": { "request_id": "req_019", "timestamp": "2026-03-24T10:31:00Z" }
}
```

---

#### API020 — Update Task

| Property | Value |
|----------|-------|
| **Method** | `PATCH` |
| **URL** | `/v1/tasks/{task_id}` |
| **Description** | Updates task fields (status, priority, title, etc.) |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Request Body:**
```json
{
  "status": "done"
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "id": "task_01-...",
    "title": "Prepare Q1 report slides",
    "status": "done",
    "completed_at": "2026-03-24T15:00:00Z",
    "updated_at": "2026-03-24T15:00:00Z"
  },
  "meta": { "request_id": "req_020", "timestamp": "2026-03-24T15:00:00Z" }
}
```

---

#### API021 — Delete Task

| Property | Value |
|----------|-------|
| **Method** | `DELETE` |
| **URL** | `/v1/tasks/{task_id}` |
| **Description** | Deletes a task |
| **Auth required** | Yes |
| **Rate limit** | 10 req/min |

**Success Response (`204 No Content`):** Empty body.

---

#### API022 — List Reminders

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/reminders` |
| **Description** | Returns user's reminders |
| **Auth required** | Yes |
| **Rate limit** | 30 req/min |

**Query Params:** `?status=pending&page=1&per_page=20`

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "id": "rem_01-...",
      "message": "Call the dentist",
      "remind_at": "2026-03-25T09:00:00Z",
      "status": "pending",
      "is_recurring": false,
      "task_id": null
    }
  ],
  "pagination": { "page": 1, "per_page": 20, "total_items": 1, "total_pages": 1 },
  "meta": { "request_id": "req_022", "timestamp": "2026-03-24T10:35:00Z" }
}
```

---

#### API023 — Create Reminder

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/reminders` |
| **Description** | Creates a new reminder |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Request Body:**
```json
{
  "message": "Follow up with vendor",
  "remind_at": "2026-03-26T10:00:00Z",
  "is_recurring": false,
  "task_id": null
}
```

**Success Response (`201 Created`):**
```json
{
  "success": true,
  "data": {
    "id": "rem_new_01-...",
    "message": "Follow up with vendor",
    "remind_at": "2026-03-26T10:00:00Z",
    "status": "pending",
    "created_at": "2026-03-24T10:36:00Z"
  },
  "meta": { "request_id": "req_023", "timestamp": "2026-03-24T10:36:00Z" }
}
```

---

#### API024 — Dismiss Reminder

| Property | Value |
|----------|-------|
| **Method** | `PATCH` |
| **URL** | `/v1/reminders/{reminder_id}` |
| **Description** | Dismisses or snoozes a reminder |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Request Body:**
```json
{
  "status": "dismissed"
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "id": "rem_01-...",
    "status": "dismissed",
    "updated_at": "2026-03-25T09:01:00Z"
  },
  "meta": { "request_id": "req_024", "timestamp": "2026-03-25T09:01:00Z" }
}
```

---

### 5.3.4 Core Feature Endpoints — Contacts

---

#### API025 — List Contacts

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/contacts` |
| **Description** | Returns user's contact list |
| **Auth required** | Yes |
| **Rate limit** | 30 req/min |

**Query Params:** `?search=Raj&is_favorite=true&page=1&per_page=50`

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "id": "con_01-...",
      "name": "Raj Sharma",
      "email": "raj@co.in",
      "phone": "+919876543210",
      "relationship": "colleague",
      "is_favorite": true
    }
  ],
  "pagination": { "page": 1, "per_page": 50, "total_items": 1, "total_pages": 1 },
  "meta": { "request_id": "req_025", "timestamp": "2026-03-24T10:40:00Z" }
}
```

---

#### API026 — Create Contact

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/contacts` |
| **Description** | Adds a new contact |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Request Body:**
```json
{
  "name": "Priya Patel",
  "email": "priya@co.in",
  "phone": "+919876543211",
  "relationship": "client"
}
```

**Success Response (`201 Created`):**
```json
{
  "success": true,
  "data": {
    "id": "con_new_01-...",
    "name": "Priya Patel",
    "email": "priya@co.in",
    "phone": "+919876543211",
    "relationship": "client",
    "is_favorite": false,
    "created_at": "2026-03-24T10:41:00Z"
  },
  "meta": { "request_id": "req_026", "timestamp": "2026-03-24T10:41:00Z" }
}
```

---

#### API027 — Update Contact

| Property | Value |
|----------|-------|
| **Method** | `PATCH` |
| **URL** | `/v1/contacts/{contact_id}` |
| **Description** | Updates a contact |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Request Body:**
```json
{
  "is_favorite": true
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "id": "con_new_01-...",
    "name": "Priya Patel",
    "is_favorite": true,
    "updated_at": "2026-03-24T10:42:00Z"
  },
  "meta": { "request_id": "req_027", "timestamp": "2026-03-24T10:42:00Z" }
}
```

---

#### API028 — Delete Contact

| Property | Value |
|----------|-------|
| **Method** | `DELETE` |
| **URL** | `/v1/contacts/{contact_id}` |
| **Description** | Removes a contact |
| **Auth required** | Yes |
| **Rate limit** | 10 req/min |

**Success Response (`204 No Content`):** Empty body.

---

### 5.3.5 Core Feature Endpoints — Communications

---

#### API029 — Send Email

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/communications/email` |
| **Description** | Sends an email on behalf of the user |
| **Auth required** | Yes |
| **Rate limit** | 10 req/min |

**Request Body:**
```json
{
  "to": "raj@co.in",
  "subject": "Q1 Report Attached",
  "body": "Hi Raj,\n\nPlease find the Q1 report attached.\n\nBest,\nKamal",
  "attachments": ["file_id_01-..."]
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "action_log_id": "act_email_01-...",
    "status": "success",
    "message": "Email sent to raj@co.in"
  },
  "meta": { "request_id": "req_029", "timestamp": "2026-03-24T10:45:00Z" }
}
```

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `400` | `INVALID_RECIPIENT` | Email address is malformed |
| `503` | `EMAIL_SERVICE_UNAVAILABLE` | SMTP server unreachable |

---

#### API030 — Send WhatsApp Message

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/communications/whatsapp` |
| **Description** | Sends a WhatsApp message via the configured API |
| **Auth required** | Yes |
| **Rate limit** | 10 req/min |

**Request Body:**
```json
{
  "to": "+919876543210",
  "message": "Hi Raj, the Q1 report is ready. Shall I send it over?",
  "attachments": []
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "action_log_id": "act_wa_01-...",
    "status": "success",
    "whatsapp_message_id": "wamid.abc123",
    "message": "WhatsApp message sent to +919876543210"
  },
  "meta": { "request_id": "req_030", "timestamp": "2026-03-24T10:46:00Z" }
}
```

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `400` | `INVALID_PHONE_NUMBER` | Number format incorrect |
| `503` | `WHATSAPP_SERVICE_UNAVAILABLE` | WhatsApp API down |

---

### 5.3.6 Core Feature Endpoints — Wake-Up Briefing & Meetings

---

#### API031 — Get Wake-Up Briefing

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/briefing/today` |
| **Description** | Returns today's summarized briefing (tasks, meetings, updates) |
| **Auth required** | Yes |
| **Rate limit** | 10 req/min |

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "date": "2026-03-25",
    "greeting": "Good morning, Kamal!",
    "summary": "You have 2 meetings and 3 tasks today.",
    "meetings": [
      { "title": "Team Standup", "time": "10:00 AM" },
      { "title": "Design Review", "time": "2:00 PM" }
    ],
    "tasks_due": [
      { "title": "Prepare slides", "priority": "high" }
    ],
    "unread_actions": 0
  },
  "meta": { "request_id": "req_031", "timestamp": "2026-03-25T06:00:00Z" }
}
```

---

#### API032 — List Meeting Summaries

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/meetings/summaries` |
| **Description** | Returns AI-generated meeting summaries |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Query Params:** `?page=1&per_page=10`

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "id": "ms_01-...",
      "title": "Team Standup - March 24",
      "summary": "Discussed sprint progress. Backend API 80% complete. Blockers: Google Calendar integration.",
      "action_items": [
        { "description": "Fix Google OAuth redirect", "assignee": "Kamal", "due": "2026-03-26" }
      ],
      "duration_minutes": 25,
      "created_at": "2026-03-24T10:30:00Z"
    }
  ],
  "pagination": { "page": 1, "per_page": 10, "total_items": 1, "total_pages": 1 },
  "meta": { "request_id": "req_032", "timestamp": "2026-03-24T11:00:00Z" }
}
```

---

### 5.4 File Management Endpoints

---

#### API033 — Upload File

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/files/upload` |
| **Description** | Uploads a file to storage and queues it for vector indexing |
| **Auth required** | Yes |
| **Content-Type** | `multipart/form-data` |
| **Rate limit** | 10 req/min |

**Request:** Form data with `file` field (max 50 MB).

**Success Response (`201 Created`):**
```json
{
  "success": true,
  "data": {
    "id": "file_01-...",
    "filename": "Q1_Report.pdf",
    "mime_type": "application/pdf",
    "size_bytes": 2457600,
    "is_indexed": false,
    "created_at": "2026-03-24T11:00:00Z"
  },
  "meta": { "request_id": "req_033", "timestamp": "2026-03-24T11:00:00Z" }
}
```

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `400` | `FILE_TOO_LARGE` | File exceeds 50 MB limit |
| `400` | `UNSUPPORTED_FILE_TYPE` | MIME type not allowed |

---

#### API034 — List Files

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/files` |
| **Description** | Returns user's uploaded files |
| **Auth required** | Yes |
| **Rate limit** | 30 req/min |

**Query Params:** `?search=report&page=1&per_page=20`

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "id": "file_01-...",
      "filename": "Q1_Report.pdf",
      "mime_type": "application/pdf",
      "size_bytes": 2457600,
      "is_indexed": true,
      "created_at": "2026-03-24T11:00:00Z"
    }
  ],
  "pagination": { "page": 1, "per_page": 20, "total_items": 1, "total_pages": 1 },
  "meta": { "request_id": "req_034", "timestamp": "2026-03-24T11:05:00Z" }
}
```

---

#### API035 — Semantic File Search

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/files/search` |
| **Description** | Performs semantic (vector similarity) search across user's indexed files |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Request Body:**
```json
{
  "query": "quarterly revenue projections",
  "limit": 5
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "file_id": "file_01-...",
      "filename": "Q1_Report.pdf",
      "similarity": 0.92,
      "matched_chunk": "...quarterly revenue projected at $2.1M, representing a 15% increase..."
    }
  ],
  "meta": { "request_id": "req_035", "timestamp": "2026-03-24T11:06:00Z" }
}
```

---

#### API036 — Download File

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/files/{file_id}/download` |
| **Description** | Returns a pre-signed URL for file download |
| **Auth required** | Yes |
| **Rate limit** | 30 req/min |

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "download_url": "https://s3.amazonaws.com/antigravity-files/...",
    "expires_in": 3600
  },
  "meta": { "request_id": "req_036", "timestamp": "2026-03-24T11:07:00Z" }
}
```

---

#### API037 — Delete File

| Property | Value |
|----------|-------|
| **Method** | `DELETE` |
| **URL** | `/v1/files/{file_id}` |
| **Description** | Soft-deletes a file and its embeddings |
| **Auth required** | Yes |
| **Rate limit** | 10 req/min |

**Success Response (`204 No Content`):** Empty body.

---

### 5.5 Settings Endpoints

---

#### API038 — Get User Preferences

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/settings/preferences` |
| **Description** | Returns all user preferences and learned behaviors |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    { "key": "preferred_meeting_length", "value": { "minutes": 30 }, "source": "learned", "confidence": 0.85 },
    { "key": "tone", "value": { "style": "professional" }, "source": "manual", "confidence": null }
  ],
  "meta": { "request_id": "req_038", "timestamp": "2026-03-24T11:10:00Z" }
}
```

---

#### API039 — Update User Preference

| Property | Value |
|----------|-------|
| **Method** | `PUT` |
| **URL** | `/v1/settings/preferences/{key}` |
| **Description** | Sets or overrides a specific user preference |
| **Auth required** | Yes |
| **Rate limit** | 15 req/min |

**Path Params:** `key` (e.g., `tone`)

**Request Body:**
```json
{
  "value": { "style": "casual" }
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "key": "tone",
    "value": { "style": "casual" },
    "source": "manual",
    "updated_at": "2026-03-24T11:11:00Z"
  },
  "meta": { "request_id": "req_039", "timestamp": "2026-03-24T11:11:00Z" }
}
```

---

#### API040 — Get Integration Status

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/settings/integrations` |
| **Description** | Returns connection status for all integrations (Google, WhatsApp, Email) |
| **Auth required** | Yes |
| **Rate limit** | 20 req/min |

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "google_calendar": { "connected": true, "email": "kamal@gmail.com" },
    "whatsapp": { "connected": true, "phone": "+919876…" },
    "email_smtp": { "connected": false, "error": "SMTP credentials not configured" }
  },
  "meta": { "request_id": "req_040", "timestamp": "2026-03-24T11:12:00Z" }
}
```

---

### 5.6 Admin Endpoints

---

#### API041 — List All Users (Admin)

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/admin/users` |
| **Description** | Returns all registered users (admin only) |
| **Auth required** | Yes (role: `admin`) |
| **Rate limit** | 10 req/min |

**Query Params:** `?is_active=true&page=1&per_page=50`

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "id": "a1b2c3d4-...",
      "email": "kamal@example.com",
      "full_name": "Kamal Kishor",
      "role": "user",
      "is_active": true,
      "created_at": "2026-03-20T08:00:00Z"
    }
  ],
  "pagination": { "page": 1, "per_page": 50, "total_items": 1, "total_pages": 1 },
  "meta": { "request_id": "req_041", "timestamp": "2026-03-24T11:15:00Z" }
}
```

**Error Responses:**

| Code | Error Code | Condition |
|------|-----------|-----------|
| `403` | `FORBIDDEN` | Non-admin user attempting access |

---

#### API042 — Deactivate User (Admin)

| Property | Value |
|----------|-------|
| **Method** | `PATCH` |
| **URL** | `/v1/admin/users/{user_id}/deactivate` |
| **Description** | Deactivates a user account |
| **Auth required** | Yes (role: `admin`) |
| **Rate limit** | 5 req/min |

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "id": "user_target-...",
    "is_active": false,
    "updated_at": "2026-03-24T11:16:00Z"
  },
  "meta": { "request_id": "req_042", "timestamp": "2026-03-24T11:16:00Z" }
}
```

---

#### API043 — System Health Check

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **URL** | `/v1/admin/health` |
| **Description** | Returns system health status for all services |
| **Auth required** | No (but recommended behind IP whitelist) |
| **Rate limit** | 60 req/min |

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "uptime_seconds": 86400,
    "services": {
      "database": "ok",
      "redis": "ok",
      "livekit": "ok",
      "llm_api": "ok",
      "whatsapp_api": "degraded"
    },
    "version": "1.0.0"
  },
  "meta": { "request_id": "req_043", "timestamp": "2026-03-24T11:17:00Z" }
}
```

---

### 5.7 Webhook Endpoints

---

#### API044 — WhatsApp Incoming Webhook

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/webhooks/whatsapp` |
| **Description** | Receives incoming WhatsApp messages/status updates from Meta API |
| **Auth required** | No (verified via signature) |
| **Rate limit** | 100 req/min |

**Request Headers:** `X-Hub-Signature-256: sha256=<hash>`

**Request Body (from Meta):**
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "changes": [
        {
          "value": {
            "messages": [
              {
                "from": "919876543210",
                "type": "text",
                "text": { "body": "Yes, send me the report." },
                "timestamp": "1711281600"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

**Success Response (`200 OK`):**
```json
{ "status": "received" }
```

---

#### API045 — Google Calendar Webhook

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **URL** | `/v1/webhooks/google-calendar` |
| **Description** | Receives push notifications from Google Calendar API for sync |
| **Auth required** | No (verified via `X-Goog-Channel-Token`) |
| **Rate limit** | 100 req/min |

**Request Headers:** `X-Goog-Channel-Token: <secret_token>`

**Success Response (`200 OK`):** Empty body.

---

## 6.0 Rate Limiting

### Rate limit rules per endpoint group

| Group | Rate Limit | Window |
|-------|-----------|--------|
| Auth (register/login) | 5–10 req | Per minute per IP |
| User Management | 10–30 req | Per minute per user |
| Conversations / Messages | 30–60 req | Per minute per user |
| Calendar / Tasks / Reminders | 15–30 req | Per minute per user |
| File Upload | 10 req | Per minute per user |
| Communications (Email/WA) | 10 req | Per minute per user |
| Admin | 5–10 req | Per minute per user |
| Webhooks | 100 req | Per minute per source IP |

### Rate limit headers returned

```http
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 27
X-RateLimit-Reset: 1711281660
Retry-After: 42
```

### Exceeded limit response (`429`)

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please retry after 42 seconds.",
    "details": {
      "retry_after": 42
    }
  },
  "meta": { "request_id": "req_rate_01", "timestamp": "2026-03-24T12:00:00Z" }
}
```

---

## 7.0 Error Code Reference

| Error Code | HTTP Status | Message | Client Handling |
|-----------|------------|---------|-----------------|
| `VALIDATION_ERROR` | 400 | Field validation failed | Highlight invalid fields |
| `FILE_TOO_LARGE` | 400 | File exceeds size limit | Show max size to user |
| `UNSUPPORTED_FILE_TYPE` | 400 | File type not allowed | Display allowed types |
| `INVALID_RECIPIENT` | 400 | Recipient address invalid | Prompt user to correct |
| `INVALID_PHONE_NUMBER` | 400 | Phone number format incorrect | Show format hint |
| `WEAK_PASSWORD` | 400 | Password doesn't meet requirements | Show password rules |
| `AUTH_TOKEN_EXPIRED` | 401 | Token has expired | Auto-refresh or re-login |
| `INVALID_CREDENTIALS` | 401 | Wrong email or password | Show generic error |
| `INVALID_REFRESH_TOKEN` | 401 | Refresh token invalid | Force re-login |
| `FORBIDDEN` | 403 | Insufficient permissions | Show access denied UI |
| `ACCOUNT_DISABLED` | 403 | Account is deactivated | Show contact admin |
| `CONVERSATION_NOT_FOUND` | 404 | Conversation does not exist | Redirect to conversation list |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found | Show 404 UI |
| `EMAIL_ALREADY_EXISTS` | 409 | Email already registered | Suggest login instead |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Implement backoff, show timer |
| `INTERNAL_ERROR` | 500 | Unexpected server error | Show generic error, log request ID |
| `LLM_SERVICE_UNAVAILABLE` | 503 | AI model service down | Show fallback UI, retry |
| `EMAIL_SERVICE_UNAVAILABLE` | 503 | SMTP service unreachable | Queue for retry, notify user |
| `WHATSAPP_SERVICE_UNAVAILABLE` | 503 | WhatsApp API down | Queue for retry, notify user |

---

## 8.0 Webhook Design

### Webhook event types

| Event | Source | Trigger |
|-------|--------|---------|
| `whatsapp.message.received` | Meta API | User replies via WhatsApp |
| `whatsapp.message.status` | Meta API | Delivery/read receipt |
| `google.calendar.sync` | Google API | Calendar event created/updated/deleted externally |

### Payload format

All incoming webhook payloads are validated, then internally normalized into:

```json
{
  "event_type": "whatsapp.message.received",
  "source": "meta",
  "timestamp": "2026-03-24T12:00:00Z",
  "data": { ... }
}
```

### Retry logic

| Attempt | Delay |
|---------|-------|
| 1st retry | 30 seconds |
| 2nd retry | 2 minutes |
| 3rd retry | 10 minutes |
| Max retries | 3 (then dead-letter queue) |

### Security verification

- **WhatsApp:** Validate `X-Hub-Signature-256` header against app secret with HMAC-SHA256.
- **Google Calendar:** Validate `X-Goog-Channel-Token` matches stored secret per channel subscription.
- All webhook endpoints reject requests failing signature verification with `403 Forbidden`.

---

## 9.0 API Changelog

| Version | Date | Type | Description |
|---------|------|------|-------------|
| v1.0 | 2026-03-24 | Initial | All endpoints documented as baseline |

### Change classification

- **Breaking:** Removing an endpoint, removing a required field from response, changing URL path.
- **Non-breaking:** Adding optional fields to response, adding new endpoints, adding optional query params.
- Breaking changes require major version bump (`v1` → `v2`) with 90-day deprecation.

---

## 10.0 Open Questions

1. **Streaming chat:** Should `API012 — Send Message` support SSE (Server-Sent Events) for streaming LLM token output, or should streaming remain strictly via WebSocket?
2. **File size limits:** Is 50 MB sufficient for meeting recordings, or do we need a separate large-file upload endpoint with resumable upload support?
3. **Multi-user conversations:** Will conversations ever include multiple human participants, requiring a `conversation_members` table and adjusted endpoints?
4. **API key auth:** Should we support API key authentication (in addition to JWT) for programmatic/CI access?

---

## 11.0 Next Steps

1. Implement route stubs in FastAPI using `APIRouter` grouping matching the endpoint groups above.
2. Build Pydantic request/response models matching every JSON schema documented.
3. Add OpenAPI tags and descriptions so Swagger auto-docs mirror this document.
4. Configure rate limiting middleware (e.g., `slowapi` for FastAPI) with per-group rules.
5. Implement webhook signature verification middleware for WhatsApp and Google Calendar endpoints.
