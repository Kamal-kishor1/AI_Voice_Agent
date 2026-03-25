# General System Architecture Document

**File name:** ARCHITECTURE.md  
**Version:** v1.0  
**Date:** 24 March 2026  

## 1.0 Purpose & Scope
This document outlines the high-level technical architecture of Antigravity and its core AI, Alex. It defines the systems, data flows, persistence layers, and communication protocols necessary to achieve a real-time, context-aware AI Operating System capable of autonomous tasks and seamless multimedia interactions.

## 2.0 Architecture Overview
**Architecture style chosen and why:**  
A **Service-Oriented Architecture (SOA)** with an asynchronous event-driven background layer. 
*Why:* The system mixes high-throughput low-latency requirements (voice streaming, chat) with heavy, asynchronous tasks (transcribing meetings, semantic indexing, sending emails). A rigid monolith would block user-facing processes easily; SOA allows the inference/agent engine to scale independently from the basic CRUD APIs.

**High level system diagram:**
```text
  [ Client (Web/Mobile) ]
      |         |
 (WebRTC)   (REST / WebSocket)
      |         |
   [ Media  ] [   API Gateway / Load Balancer   ]
   [ Server ]           |
    (LiveKit)    [ Core FastAPI App ]
                        |
      +-----------------+-----------------+
      |                 |                 |
 [ Vector DB ]   [ Postgres DB ]   [ Message Broker ]
 (Context)      (State/Memory)      (Redis/RabbitMQ)
                                          |
                                   [ Worker Nodes ]
                                 (Agents/Background Jobs)
```

**Key architectural decisions:**
- WebRTC for voice streaming to minimize latency.
- Python FastAPI for the backend to leverage the extensive AI/ML ecosystem natively.
- Redis/RabbitMQ for caching and message brokerage to decouple heavy jobs.

## 3.0 System Components

### 3.1 Frontend Layer
- **Framework and why:** Next.js + React. Excellent for complex state management, scalable ecosystem, and enables SSR for initial fast loads if SEO/performance dictates.
- **State management approach:** Zustand (lightweight, unopinionated) or React Context for global state (User, Auth, AI State).
- **Rendering strategy:** CSR (Client-Side Rendering) for the main application given its highly interactive, app-like nature (dashboards, real-time chat), mixing with SSR where appropriate for initial auth loads.

### 3.2 Backend Layer
- **Server framework:** FastAPI (Python). Highly performant, async by default, native Pydantic validation perfectly suited for LLM schemas.
- **Business logic layer:** Encapsulated in a `services` directory. This isolates core AI logic (Intent extraction, Tool calling, RAG) from external web routing.
- **Service layer design:** 
  - *LLM Engine:* Manages prompts, token limits, multi-agent orchestration.
  - *Integrations:* Connects to Google Calendar, WhatsApp APIs, Mail servers.

### 3.3 Database Layer
- **Database type and why:** PostgreSQL for relational data (users, schedules, access control) and a Vector DB (pgvector or Pinecone) for semantic search.
- **Data access patterns:** Repositories abstracting SQL queries.
- **ORM/query builder choice:** SQLAlchemy for Python, enabling robust data modeling and async queries.

### 3.4 Cache Layer
- **Caching strategy:** Cache session data, frequent system configurations, and repeated simple LLM instructions.
- **What gets cached:** User preferences, API credentials, routing tokens.
- **Cache invalidation rules:** TTL (Time to live) based on data volatility.

### 3.5 Queue/Worker Layer
- **Background job processing:** Celery or ARQ.
- **Queue technology:** Redis or RabbitMQ.
- **Worker design:** Specialized autonomous workers (e.g., "Transcription Worker", "Email Dispatch Worker") consuming from specific queues to ensure heavy tasks don't block web threads. Multi-step execution is orchestrated here.

## 4.0 Communication Patterns
### 4.1 Client to server communication
- REST for standard data retrieval (fetching tasks, settings).
- WebSockets for bi-directional chat, real-time UI updates, and streaming LLM token dumps.
- WebRTC (via LiveKit/custom implementation) for raw audio streaming (Wake word detection -> STT).

### 4.2 Service to service communication
- Internal gRPC or Fast HTTP endpoints for synchronously checking data between microservices (if separated).
- Pub/Sub via Redis for asynchronous state changes.

### 4.3 Real-time communication
- WebSocket heartbeat ensures connection health; disconnection triggers UI offline state instantly.

### 4.4 Event driven patterns
- "Upload File" -> Triggers S3 Save Event -> Pushed to Worker Queue -> Index Worker Vectors the document -> Updates DB -> Notifies User via WebSocket.

## 5.0 Data Flow
**Voice Interaction Request Lifecycle:**
1. User speaks -> Browser captures audio chunks.
2. WebRTC streams audio to Media Server (LiveKit).
3. Backend receives stream, pipes to STT (Speech-to-Text) module.
4. STT outputs text to LLM Intent Engine.
5. Intent Engine determines action (e.g., "Schedule meeting with John").
6. System checks Calendar API & verifies permissions.
7. System formulates text response + executes action via Background Worker.
8. Text response sent to TTS (Text-to-Speech) module.
9. Audio streamed back to client via WebRTC.
10. Database asynchronously logs transaction for personalization learning.

## 6.0 Scalability Design
- **Horizontal scaling approach:** Stateless FastAPI instances scaled via Kubernetes HPA based on CPU/RAM usage.
- **Vertical scaling limits:** Will be hit primarily on GPU nodes (if hosting local LLMs/TTS). Must shard or load balance across multiple GPU instances.
- **Load balancing strategy:** NGINX or AWS ALB directing traffic; sticky sessions required for WebSockets.
- **Database scaling plan:** Read replicas for Postgres; distributed sharding for Vector DB as context size grows.

## 7.0 Resilience & Reliability
- **Failure handling:** Graceful degradation. If Voice Synthesis fails, fallback to Text-only UI.
- **Retry strategies:** Exponential backoff for 3rd party API limits (WhatsApp, Calendar).
- **Circuit breaker patterns:** Halts requests to an external API (like LLM provider) if it times out continuously, preventing resource exhaustion.
- **Fallback mechanisms:** Core logic caching locally.

## 8.0 Performance Architecture
- **Performance targets:** <500ms TTFB (Time to First Byte) for AI voice responses.
- **Optimization strategies:** LLM Token streaming heavily utilized so UI starts updating immediately. 
- **Bottleneck prevention:** Strict rate limiting; background queue utilization for any task taking > 200ms.

## 9.0 Deployment Architecture
- **Environments:** Dev (Local), Staging (Preview), Prod.
- **CI/CD pipeline design:** GitHub Actions running lint, test, build array -> Docker Push -> Helm sync / ArgoCD.
- **Infrastructure as code approach:** Terraform for managing AWS/GCP resources.
- **Container strategy:** Universal Dockerized environments.

## 10.0 Architectural Decision Records (ADR)
| Decision | Reason | Alternatives rejected |
|----------|--------|-----------------------|
| Python Backend (FastAPI) | Superior AI/ML ecosystem, Fast prototyping | Node.js (poor ML lib support), Go (longer dev time) |
| WebRTC for Voice | Lowest latency for streaming duplex audio | WebSocket binary streaming (higher latency, overhead) |
| Redis Task Queue | Handles high throughput messaging perfectly | Kafka (Over-engineered for initial phase) |

## 11.0 Open Questions
1. Do we host our own open-source LLM models (Llama 3, Mistral), or rely entirely on external managed APIs (OpenAI/Anthropic) initially?
2. What are the strict data privacy & compliance limits for the Vector DB regarding user uploaded files?

## 12.0 Next Steps
- Finalize cloud provider (AWS vs GCP) based on AI service availability.
- Setup core repository with foundational docker-compose infrastructure.
- Implement a skeleton ping-pong WebRTC + WebSocket application as proof of concept.
