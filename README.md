## Sandstone Loan Doc Template Builder

Welcome to Sandstone Real Estate LLC's in-house document management and legal template editing app (FastAPI + Next.js). Pick a pre-loaded template, edit it, save changes, and search across docs with optional filters by counter party (borrower, buyer, etc.) so you always get the right context.

Inspired by a workflow from in-house legal at a real estate investment firm: every new deal started from templates (loan agreements, leases, etc.) and was built up using precedent from prior deals with the same counter party.

**Run:** `make dev` at the repo root to start backend and frontend. You'll find frontend at Port 3000. The repo is pre-seeded with a template and two loan agreements for Sandstone Real Estate LLC.
**Tests:** `make test` at the repo root

**Layout:** Monorepo — `apps/backend` (API), `apps/web` (Next.js). DB is SQLite under `apps/backend/app/db/`.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/documents` | List document summaries. Query: `party_id`, `party_name`, `doc_type` (optional). |
| GET | `/documents/search` | Search all (or subset). Query: `q` (required), `limit`, `offset`, `document_ids`. |
| GET | `/documents/{doc_id}/search` | Search within one document. Query: `q`, `limit`, `offset`. |
| POST | `/documents/from-template` | Create a new doc from a template. Body: `template_id`, `title`. |
| GET | `/documents/{doc_id}` | Get full document. Optional `If-None-Match` for 304. |
| PATCH | `/documents/{doc_id}` | Update content/title (range-based changes). Requires `If-Match: version`. |
| DELETE | `/documents/{doc_id}` | Delete document. Returns 204. |

Interactive API docs: `http://localhost:8000/docs` when the backend is running.

### API design notes

1. **RESTful endpoints** — The app is built around the `document` resource; endpoints are CRUD and query operations, not action-based.

2. **Modular design**: Routes are thin HTTP layers, all business logic live in services, db layer is independent, deps are managed via singletons in core, centralized config

3. **Database** — SQLite for simplicity on a local prototype. Blob storage or Postgres could be swapped in given the modular design; document content lives in the SQLite `documents` table.

4. **Concurrency** — Version-based: if the doc version is out of sync on PATCH, the backend returns 412. Automerge was out of scope.

5. **Document updates** — Position/range-based patching only (for time); bulk replace is supported; find-and-replace is not implemented.

6. **Memory management** -  Ideally for large documents, we'd be streaming from blob storage and processing in chunks within a bounded memory window. Given the docs are loaded in memory on SQLlite, there is no such mechanism. We do, however, conduct query search by loading one doc into memory at a time for the sake of demonstration.

7. **Benchmarking** — Search performance tests run over 10, 100, and 1000 documents (10MB each). At 1000 docs the linear scan is slow (see the failed test); an inverted index would scale better (not implemented due to time).

8. **Inverted index tradeoffs** — Would require a key-value term → doc-id structure and intersection for multi-word queries; the index would have to be updated on create/update or it becomes stale. Adding the index would introduce state and maintenance overhead in exchange for much faster repeated search.

9. **Minimal frontend**: The frontend is intentionally minimal given the scope of the assignment. In a more robust project, I'd recommend using Zustand for application state, React Query for server state, Zod for typing.

10. **Feature ideas**: Frontend includes bug report button and UI for an LLM driven semantic query on previous docs with a specific counterparty. These are meant to be purely conceptual and are not wired into any backend endpoint.

11. **Document Upload Flow**: The repo intentionally excludes user driven document upload given lack of blob storage. The production flow would be, user sends request with document metadata, backend responds with signedUrl, frontend uploads directly to blob storage.


###
