# Production infra outline

One-page outline for taking the prototype (FastAPI + Next.js + SQLite) to a robust, production-grade service. Trade-offs called out where relevant.

---

## Architecture & infra

- **API:** Run FastAPI in containers (e.g. AWS, GCP Cloud Run, Digital Ocean). Avoid serverless for the API so we keep connection pooling to the DB and predictable latency for search; cold starts would hurt UX.
- **Frontend:** Next.js on Vercel. Trade-off is vendor lock-in for minimal ops headaches and Vercel tooling. Static assets on CDN.
- **Data:** Move from SQLite to **Postgres** for documents metadata and version history; store **document body/content in object storage** (S3, GCS) keyed by doc id. Reduces DB size and allows streaming large docs later.
- **Search:** Replace in-memory linear scan with a searched dedicated DB like **Elasticsearch/OpenSearch**. *Trade-off: in-memory scan / Postgres FTS = less ops; Elasticsearch = better search and scale, more to run.*
- **Caching:** Redis (or managed equivalent) for session/tokens and optional response cache for hot document reads. Skip caching search results initially until we know what the access pattern is (query variety is high).

```
[Users] → [CDN / Vercel] (Next.js)
              ↓
         [API (ECS/Cloud Run)]
              ├→ [Postgres] (metadata)
              ├→ [OpenSearch/Elasticsearch] (search index)
              ├→ [Object storage] (doc content)
              └→ [Redis] (sessions, optional cache)
```

---

## CI/CD & deployment

- **Pipeline:** GitHub Actions: on push to main — run backend tests, frontend lint/build; build API; push to registry. Only affected packages should be updated to avoid unnecessary redeployment.
- **Deploy:** API: rolling deploy to ECS/Cloud Run with health checks on `/health`. Frontend: Vercel auto-deploy or deploy static assets to CDN. DB migrations as a separate step (e.g. run before new API rollout).

---

## Security & compliance

- **Auth:** OAuth2 (e.g. Auth0) for user sign-in; issue JWTs for API calls. Enables SSO and enterprise later without redesign.
- **Transport & secrets:** TLS everywhere (frontend and API). Secrets pulled from a secret manager; no secrets in repo or env files in prod.
- **Data:** Encrypt at rest (DB and object storage; default on most clouds). RLS for multi-tenant on DB.
- **Audit & compliance:** Log document access and mutations (who, when, doc id) to a dedicated audit log, will be important for SOC 2 / enterprise.

---

## Scalability & resilience

- **API scaling:** Horizontal: run API replicas behind a load balancer. Scale on CPU or request rate (something like 70% CPU or a RPS threshold). Single replica is fine for early prod; add autoscaling when load grows.
- **Large docs:** Stream from object storage in chunks instead of loading full doc into memory. Apply range-based PATCH against a streamed view / temp buffer so we have a bounded memory window.

---

## Monitoring & observability

- **Metrics:** Use Datadog or a similar platform to track request count, latency (p50/p95/p99), error rate by route and status.
- **Logs:** Structured JSON logs from API and ship to a central log store. Datadog can also handle this.
- **Tracing:** Not as critical immediately, but will be included with Datadog and becomes important if we have questions re: performance.
- **Alerts:** Alert on error rate spike, latency degradation, and dependency failure (DB, storage, auth).

---

## Operations & cost

- **Cost controls:** Right-size API instances (start with 1–2 small nodes; scale up only on data). Set up billing alerts and periodic reviews.
- **Multi-region:** Stay single-region initially. Add a second region only when we have latency / availability needs; document content in object storage can be replicated later for DR.
- **Migrations & ops:** Use an ORM and make sure migrations are clearly organized, versioned, and rollback-able. I'd recommend a managed Postgres and Redis to minimize ops.
