"""
Linear-scan search over document content. Returns hits with snippet (fixed window).
"""
from dataclasses import dataclass

from app.db.store import DocumentStore



## this is what each search hit will look like
@dataclass
class SearchMatch:
    """A single search hit: document id, title, snippet, and character range."""

    document_id: str
    title: str
    snippet: str
    start_index: int
    end_index: int


## linear scan: all occurrences of query in content (case-insensitive). Returns list of (start, end).
## O(n) time complexity, n is the length of the content
def _find_matches_in_content(content: str, query: str) -> list[tuple[int, int]]:
    """Linear scan: all occurrences of query in content (case-insensitive). Returns list of (start, end)."""

    ## if the query is empty, return an empty list
    if not query or not query.strip():
        return []
    ## strip the query and convert to lowercase (normalize)
    q = query.strip()
    content_lower = content.lower()
    q_lower = q.lower()
    length = len(q_lower)
    if length == 0: ## if the query is empty, return an empty list
        return []
    result: list[tuple[int, int]] = [] ## initialize an empty list to store the results
    start = 0   ## start at the beginning of the content and keep track of the position we are looking at
    while True: ## keep looking for the query in the content until we reach the end
        pos = content_lower.find(q_lower, start)
        if pos == -1:
            break
        result.append((pos, pos + length))
        start = pos + 1
    return result


def _snippet(content: str, start: int, end: int, window: int = 40) -> str:
    """Fixed character window around [start, end]. Clamped to content bounds."""
    low = max(0, start - window)
    high = min(len(content), end + window)
    return content[low:high]


class SearchService:
    """Search over document content. Uses store for doc access; linear scan for matching."""

    def __init__(self, store: DocumentStore) -> None:
        self._store = store

    def search(
        self,
        q: str,
        limit: int = 10,
        offset: int = 0,
        document_ids: list[str] | None = None,
        snippet_window: int = 40,
    ) -> tuple[list[SearchMatch], int]:
        """
        Search documents for query string (phrase, case-insensitive).
        document_ids=None -> search all docs; otherwise restrict to those ids.
        Returns (matches for this page, total hit count). Pagination via limit/offset.
        Streams one document at a time (no full corpus in memory).
        """
        all_hits: list[SearchMatch] = []

        if document_ids is not None:
            id_list = document_ids
        else:
            # Summaries only (no content); we fetch full doc one at a time below.
            id_list = [s.id for s in self._store.list_document_summaries()]

        for doc_id in id_list:
            doc = self._store.get_document(doc_id)
            if doc is None:
                continue
            for start, end in _find_matches_in_content(doc.content, q):
                snippet = _snippet(doc.content, start, end, window=snippet_window)
                all_hits.append(
                    SearchMatch(
                        document_id=doc.id,
                        title=doc.title,
                        snippet=snippet,
                        start_index=start,
                        end_index=end,
                    )
                )
            # only one document processed at a time
            # for linear scan, we shouldn't be doing whole doc searches, it should be streamed one chunk at a time


        total = len(all_hits)
        page = all_hits[offset : offset + limit]
        return (page, total)
