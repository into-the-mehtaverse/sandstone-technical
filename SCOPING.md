## ENDPOINTS

GET /documents
    - Request: NA
    - Response: 200 - array of doc summaries (no full content)
    - Notes: list only, no search. omit content to keep payload small.

GET /documents/{id}
    - Request: NA
    - Response: 200 - full document
    - Notes: Header should be etag. Return 304 If-None-Match matches current etag. This is the source of truth for content and etag before PATCH. Client should store etag for If-Match on save.

POST /documents
    - Request: metadata only
    - Response: 201 -documentId + uploadUrl (presigned)
    - Notes: Client uploads file to uploadUrl (eg. PUT), then can call GET /documents/{id} (and optionally poll until processing/indexing is done if we get there).

PATCH /documents/{id}
    - Request:
    - Response: full new document text, new eTag
    - Header: If-Match: "<etag>", 412 if missing or doesn't match.
    - Notes: Apply changes in array order; targets relative to document state at start of request. Use a single name for “new text” in PATCH (e.g. replacement everywhere, or text in the change object).

and then search related

GET /documents/search?
    - Request: Query params: q (required), limit=10, offset=0. Optional: documentIds=id1,id2 to restrict to specific docs.
    - Response: { "matches": [ { "documentId", "snippet", "startIndex", "endIndex" } ], "total": 42 }. also include titles.
    - Notes: Notes: Uses in-memory inverted index; snippet is the matching excerpt (e.g. fixed character window around the hit). Paginate via limit/offset and optionally return total.

GET /documents/{id}/search?
    - Request:
    - Response: 200 — same shape as global search but all documentId are this id, e.g. { "matches": [ { "documentId", "snippet", "startIndex", "endIndex" } ], "total": 5 }.
    - Notes: Search restricted to one document; same index, filtered by documentId.


## DATA MODELS:

Document:
- id
- title or filename
- content (full text)
- createdAt
- updatedAt
- etag (cache of hash)

#### OPTIONAL / FUTURE DATA MODELS:

Revision:
- id
- documentId (FK)
- version (integer, 1-based)
- content or patch
- createdAt

Chunk:
- id
- documentId (FK)
- content (snippet text)
- startIndex, endIndex (or position)
- embedding


## APPROACHES:

 - REPLACE (target, bulk operations):
    - Occurrence based and range based
    - One PATCH = one array of changes, apply in array order
    - Positions and occurences are relative to the document state at the start of the request (so later changes don't invalidate old ones)


 - MEMORY MANAGEMENT:
    - Start with in-memory, single pass, then transition to:

        - Bounded memory window / streaming
        1. Read in chunks
        2. Copy to output
        3. When you hit replace region, emit replacement instead of chunk, then continue

 - SEARCH:
    * USING INVERTED INDEX
    1. Build the index in one pass per document (O(n) to total to index)
    2. Each search will be O(query length + result size)
    3. Look up terms in map then intersect the lists

    This removes need for re-scanning full text per query (near-linear meaning index size once then fast look ups)

 - CONCURRENCY:
   -etag represents current version of the document content
   -require client to send If-Match: <etag from last GET>
   -before doing any replace logic, compare:
        - If If-Match does not equal current etag, do not run replace at all and return 412 Precondition Failed instead
        - If they match, proceed with above described REPLACE approach, then:
            - Save the new content
            - Recompute and store a new etag on the document


 - ERROR HANDLING:
    - 4xx for client errors
    - 5xx for server errors
    - Shared, consistent error shape


## TECH STACK
- Backend: FastAPI
- Frontend: React / Vite
- DB: SQLite with very light SQL

## Other notes

- Assume explict saves, not auto-update on keystroke
- If etag doesn't match, then we'll reject server side and the changes will remain client side but they'll need to refresh the document and re-apply (automerge is out of scope, we can mention Websockets for Real time and auto-merge for conflict resolition in write up)
- never overwrite the editor with the refetched document without an explicit user action (and ideally a warning). Maybe can copy client side, have a redline side by side so they can reapply or something.
**DELIVERABLE** - include unit tests based on interview.md and make sure all this passes.
