# Project Structure Document

**File name:** STRUCTURE.md  
**Version:** v1.0  
**Date:** 24 March 2026  

## 1.0 Purpose & Scope
This document outlines the directory architecture for Antigravity. It dictates the organizational principles governing the codebase, ensuring scalable development, straightforward onboarding, and maintainability across frontend, backend, and shared libraries.

## 2.0 Project Overview
- **What Antigravity is:** An AI Operating System featuring Alex, an autonomous, voice-first intelligent assistant capable of semantic search, multi-step actions, and smart communications.
- **Core technical approach:** A decoupled, API-first architecture communicating over REST, WebSockets, and WebRTC to provide a highly interactive real-time experience while delegating heavy compute tasks to asynchronous AI agents.
- **Monorepo vs polyrepo decision:** **Monorepo (e.g., Turborepo/npm workspaces)**. Given the tight integration needed between the AI models, backend services, and frontend UI, a monorepo allows sharing types, API schemas, configurations, and core logic, significantly reducing friction in versioning and cross-team communication.

## 3.0 Folder Structure

```text
antigravity/
├── apps/
│   ├── web/                     # Frontend Next.js/Vite application
│   │   ├── src/
│   │   │   ├── components/      # Reusable UI elements (Button, Waveform, Card)
│   │   │   ├── pages/           # Route definitions (if Next.js pages/app router)
│   │   │   ├── hooks/           # Custom React hooks (useVoice, useAI)
│   │   │   ├── utils/           # Client-side helpers
│   │   │   └── styles/          # Global styles, Tailwind/CSS config
│   │   └── package.json
│   └── api/                     # Backend Python FastAPI application
│       ├── app/
│       │   ├── api/             # Route handlers / controllers
│       │   ├── core/            # Configs, security, auth
│       │   ├── models/          # ORM models (SQLAlchemy/Pydantic)
│       │   ├── services/        # Business logic (AI, Sync, Mail, WhatsApp)
│       │   └── worker/          # Background tasks (Celery/ARQ)
│       ├── requirements.txt
│       └── main.py
├── packages/                    # Shared modules
│   ├── ui-kit/                  # Shared design system components
│   ├── schemas/                 # Shared data schemas (for API validation)
│   └── config/                  # Shared linting/TS configs
├── infra/                       # Infrastructure, Docker, Terraform
│   ├── docker-compose.yml       # Local orchestration
│   └── k8s/                     # Production deployment manifests
├── tests/                       # E2E and cross-service integration tests
└── docs/                        # Project documentation
    ├── ARCHITECTURE.md
    ├── STRUCTURE.md
    ├── UI_UX.md
    └── GOAL.md
```

**Every folder's purpose:**
- `apps/`: Contains standalone deployable applications (Frontend Web & Backend API).
- `packages/`: Internal libraries shared across apps ensuring DRY principles.
- `infra/`: Infrastructure as code and container declarations defining execution environments.
- `tests/`: High-level tests spanning multiple applications (E2E).
- `docs/`: Centralized knowledge base describing system specs.

**Naming conventions:** 
- Kebab-case for folder names (`ui-kit`, `services`, `hooks`).
- PascalCase for React component folders if treating as modules (e.g., `VoiceWaveform/`).

**File naming rules:**
- `camelCase.ts` for utilities and hooks.
- `PascalCase.tsx` for React components.
- `snake_case.py` for Python modules.

## 4.0 Module Breakdown
### 4.1 Frontend modules
- **Communication Module:** Handles LiveKit/WebRTC connections and WebSockets for real-time streaming.
- **Task Module:** Manages local state for calendar, to-dos, and reminders.
- **Search Module:** UI for semantic search, real-time results, and action previews.

### 4.2 Backend modules
- **LLM Engine Module:** Handles intent understanding, multi-step planning, streaming, and multi-agent coordination.
- **Search & Vector Module:** Manages document embeddings, Pinecone/pgvector integration, and semantic query execution.
- **Integration Layer (`services/`):** Connects to WhatsApp, Email (SMTP), and Calendar (Google Auth).
- **WebRTC/LiveKit Module:** Coordinates streaming voice from the UI.

### 4.3 Shared modules
- `packages/config/`: Central styling tokens and environment configurations.
- `packages/ui-kit/`: Agnostic UI components usable across web or internal admin panels.
- `packages/schemas/`: Ensure frontend and backend agree on data structures.

### 4.4 Configuration modules
- Located at project root: `turbo.json`, `package.json` (monorepo root).
- App-specific: `apps/web/next.config.js`, `apps/api/.env`.

### 4.5 Testing modules
- Contained within `__tests__` or alongside files (e.g., `Button.test.tsx` next to `Button.tsx`).

## 5.0 File Naming Conventions
- **Components:** `ChatBubble.tsx`, `ChatBubble.test.tsx`.
- **Pages:** `index.tsx`, `dashboard.tsx` (or `page.tsx` for Next.js app router).
- **Utilities:** `stringFormatters.ts`, `date_utils.py`.
- **Tests:** Suffix with `.test` or `.spec` before the extension.
- **Config files:** `eslint.config.js`, `prettierrc.json` (industry standard).

## 6.0 Import & Export Rules
- **How modules import each other:** Use absolute path aliases defined in `tsconfig.json` (`@/components/...`) or Python `sys.path` relative to `app/`.
- **Circular dependency rules:** Strictly prohibited. CI pipelines will include a circular dependency checker (e.g., `madge`).
- **Index file conventions:** Use `index.ts` or `__init__.py` to act as a public API boundary for a folder. Export only what is necessary to the consuming application.

## 7.0 Configuration Files
- `.env.example`: Root template showing required variables (LiveKit, WhatsApp, Google).
- `apps/api/.env`: Backend specific (DB URLs, LLM APIs).
- `apps/web/.env.local`: Frontend specific (API base URLs).
- `infra/docker-compose.yml`: For local development orchestration.

## 8.0 Testing Structure
- **Unit test location:** Co-located with the implementation code (e.g., `app/services/auth.py` next to `app/services/test_auth.py`).
- **Integration test location:** In an `integration/` folder spanning a service (e.g., `apps/api/integration/`).
- **E2E test location:** In the root `tests/e2e/` folder using Playwright or Cypress.

## 9.0 Build Output Structure
- **What the build produces:** 
  - Frontend: A `.next/` or `dist/` folder containing static and server-rendered bundles optimized for production.
  - Backend: Docker image packaging the Python environment and source code.
- **Deployment ready structure:** Containerized images managed via Kubernetes or pushed to managed services (Vercel/Render).

## 10.0 Open Questions
1. Will we require a separate microservice for heavy background ML tasks (e.g., local Whisper transcription), or will it run within the main FastAPI app/Celery worker?
2. Which specific VectorDB (Pinecone vs Milvus vs pgvector) will dictact our immediate Docker infrastructure needs?

## 11.0 Next Steps
- Initialize the monorepo tooling.
- Scaffold the `apps/api` (FastAPI) and `apps/web` (Next.js/React).
- Setup CI linting rules to enforce naming conventions and structure enforcement.
