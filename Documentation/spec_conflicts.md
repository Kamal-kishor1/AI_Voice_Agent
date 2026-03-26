# Spec Conflicts

This file records source-of-truth conflicts discovered while implementing phase 1 so they can be resolved before later phases depend on them.

## 1. `audit_logs` exists in security docs but not database schema

- `SECURITY.md` repeatedly references an `audit_logs` table for service-role activity and user-visible audit history.
- `DATABASE.md` does not define `audit_logs`.
- Phase-1 code follows `DATABASE.md` because `TASK.md` says the database schema is authoritative.

## 2. File embedding dimension is inconsistent

- `DATABASE.md` defines `file_embeddings.embedding` as `VECTOR(1536)` and describes OpenAI `text-embedding-3-small`.
- `TECH_STACK.md` and later task phases describe the free-first embedding model as `all-MiniLM-L6-v2`, which is 384-dimensional.
- The phase-1 schema uses 1536 to remain consistent with `DATABASE.md`.

## 3. File embedding cardinality is inconsistent

- `DATABASE.md` marks `file_embeddings.file_id` as `UNIQUE`.
- Phase 5 in `TASK.md` describes chunking each file into multiple segments, which would require multiple embedding rows per file.
- The phase-1 schema keeps the `UNIQUE` constraint because the schema document is authoritative.

## 4. User preferences naming is inconsistent

- `DATABASE.md` defines a `user_preferences` table.
- `SECURITY.md` refers to a `preferences` table in the data-handling section.
- The implementation uses `user_preferences` to match the schema.

## 5. Health endpoint naming differs between docs

- Phase 1 in `TASK.md` requires `GET /health`.
- `API_ENDPOINTS.md` defines `GET /v1/admin/health`.
- The implementation exposes both: `/health` for the phase-1 acceptance path and `/v1/admin/health` for the API catalog shape.

## 6. Local compose service count differs from the task text

- `TASK.md` mentions four compose services in one place while also requiring a working database-backed health check.
- The local stack includes PostgreSQL, Redis, API, worker, and beat so the phase-1 environment is self-contained and reproducible.
