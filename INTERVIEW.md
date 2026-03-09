# Legal Tech - Full Stack Interview Assessment (CONFIDENTIAL)

**Overview**

*This interview consists of three  phases designed to evaluate your full‑stack development, infrastructure design, and problem‑solving skills.*

1. **Part I: Take‑Home App Build** (limit to 3-4 hours at home)

    Build core features including open‑ended text editing/redlining and search

2. **Part II: Infra Thinking & Assessment Take-Home** (~1 hour at home)

    Outline how you’d production-ize and scale the app from Part  I (or a similar app).

---

## What We’re Evaluating

- **Part I:** Code quality, API design, modularity, basic LLM integration, test coverage
- **Part II:** Architecture vision, ability to think about operational trade‑offs
- **Part III:** Real‑time coding fluency, communication, design rationale, adaptability/quick thinking

---

## Part I: Take‑Home App Build (limit to 3-4 hrs)

**Goal:** Deliver an open-ended app with document editing capabilities and search functionality. Think of this as a simple document management service where users can make text changes and search across document content. You may use whatever tech stack you prefer. Note - this prompt is **purposefully open-ended**. Please use your own creativity to determine what to create within the scope of a "redlining service" and "search functionality". We are mostly going to be evaluating how you think about designing and the quality of your code.

### Requirements (baseline)

- **Change Requests:** send JSON specifying text to replace and new text for a single document and receive the updated document text in the response.
- **Search Functionality:** query one or more documents for relevant text snippets and receive matching contexts.
- **Tests & Docs:**
    - Unit tests for core change and search logic, including large‑file tests or performance benchmarks.
    - Sample requests (curl or Postman collection).
    - `README.md` with setup, usage examples, performance considerations, and any chosen API design rationale.

*You’re free to design the API structure and create test data as you see fit.* Example endpoints:

```
# Document changes
PATCH /documents/{id}
{
  "changes": [
    {
      "operation": "replace",
      "target": { "text": "old text", "occurrence": 1 },
      "replacement": "new text"
    }
  ]
}

# Or position-based
PATCH /documents/{id}
{
  "changes": [
    {
      "operation": "replace",
      "range": { "start": 100, "end": 108 },
      "text": "new text"
    }
  ]
}

# Search
GET /documents/search?q=contract&limit=10&offset=0
# or search specific documents
GET /documents/{id}/search?q=contract
```

### Requirements (optional)

- **Error Handling:** Return appropriate 4xx for client errors (e.g. invalid payload, missing document); return 5xx for server errors with a JSON body `{ error: string, code: number }`.
- **Bulk Operations:** support replacing multiple terms in one request (e.g., array of changes).
- **Performance Constraints:** assume documents can be large (e.g., 10MB+); design search and replace to run in near-linear time and document your approach to indexing or streaming.
- **Concurrency Control:** add simple versioning or ETag support to detect and prevent conflicting updates; handle cases where replacement text appears multiple times in a document (e.g., specify occurrence number, character ranges, or contextual matching).
- **Search Indexing:** outline or implement an in-memory inverted index for faster repeated searches, and discuss trade‑offs
- **API Design Refinement:** Separate read and write operations cleanly, consider RESTful patterns vs. action-based endpoints, and justify your API structure choices.

> Time Estimate: ~3-4  hours. A simple front‑end is **fine**—focus primarily on API and core features.
>

---

## Part II: Infra Thinking & Assessment (limit to 1hr)

**Goal:** Outline how to turn your prototype into a robust, production‑grade service.

### Deliverables (1 page Markdown or PDF with text or diagrams on the following topics, or others you think would be appropriate)

- **Architecture & Infra**: compute, storage, caching, etc.
- **CI/CD & Deployment**: pipelines, rollout strategies
- **Security & Compliance**: auth (SSO/OAuth2), encryption, audit logs, GDPR/SOC2 compliance
- **Scalability & Resilience**: auto‑scaling, failover, batching, etc.
- **Monitoring & Observability**: metrics, logs, tracing, alerts
- **Operations & Cost**: cost controls, multi‑region, right‑sizing

> We expect concise thinking or diagrams—demonstrate trade‑offs and priorities. Do not just write a long essay!
>

---
