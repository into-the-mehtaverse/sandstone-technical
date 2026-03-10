"""
Performance benchmarks: large-document PATCH and search.
Creates a ~10MB document in the test and asserts correctness and optional time bounds.
"""
import time

import pytest

from app.db.store import DocumentStore
from app.models.api import DocumentChange, ReplaceRange
from app.services.documents import DocumentService
from app.services.search import SearchService

# 10MB document for performance benchmarks
LARGE_DOC_SIZE = 10 * 1024 * 1024
# Max seconds for PATCH / search on 10MB (generous for CI)
MAX_PATCH_SECONDS = 1.0
MAX_SEARCH_SECONDS = 1.0
# Max seconds for search across N documents (10MB each)
MAX_SEARCH_N_DOCS_SECONDS = {10: 1.0, 100: 1.0, 1000: 1.0}


@pytest.fixture
def store() -> DocumentStore:
    return DocumentStore(path=":memory:")


@pytest.fixture
def document_service(store: DocumentStore) -> DocumentService:
    return DocumentService(store)


@pytest.fixture
def search_service(store: DocumentStore) -> SearchService:
    return SearchService(store)


def _large_content_with_needle(size: int = LARGE_DOC_SIZE, needle: str = "unique_needle_here") -> str:
    """Build content of given size with needle at the middle."""
    half = (size - len(needle)) // 2
    return "a" * half + needle + "a" * (size - half - len(needle))


def test_patch_large_document(document_service: DocumentService) -> None:
    """PATCH a single replace on a ~10MB document; assert correctness and reasonable time."""
    content = _large_content_with_needle()
    doc = document_service.create_document("Large", content=content)
    # Replace the needle in the middle with new text
    needle = "unique_needle_here"
    start = (LARGE_DOC_SIZE - len(needle)) // 2
    end = start + len(needle)
    change = DocumentChange(
        operation="replace",
        range=ReplaceRange(start=start, end=end),
        text="replaced",
    )

    t0 = time.perf_counter()
    updated = document_service.update_document_content(doc.id, doc.version, [change])
    elapsed = time.perf_counter() - t0

    assert len(updated.content) == LARGE_DOC_SIZE - len(needle) + len("replaced")
    assert updated.content[start : start + len("replaced")] == "replaced"
    assert elapsed < MAX_PATCH_SECONDS, f"PATCH took {elapsed:.2f}s (max {MAX_PATCH_SECONDS}s)"


def test_search_large_document(search_service: SearchService, store: DocumentStore) -> None:
    """Search for a phrase in a ~10MB document; assert one match and reasonable time."""
    needle = "unique_needle_here"
    content = _large_content_with_needle(needle=needle)
    doc = store.create_document("Large", content=content)

    t0 = time.perf_counter()
    page, total = search_service.search(needle, document_ids=[doc.id])
    elapsed = time.perf_counter() - t0

    assert total == 1
    assert page[0].document_id == doc.id
    assert needle in page[0].snippet
    assert elapsed < MAX_SEARCH_SECONDS, f"Search took {elapsed:.2f}s (max {MAX_SEARCH_SECONDS}s)"


@pytest.mark.parametrize("num_docs", [10, 100, 1000])
def test_search_across_many_large_documents(
    search_service: SearchService,
    store: DocumentStore,
    num_docs: int,
) -> None:
    """Benchmark search across 10, 100, or 1000 documents of 10MB each; assert correctness and time."""
    needle = "search_needle"
    content = _large_content_with_needle(needle=needle)
    for i in range(num_docs):
        store.create_document(f"Doc_{i}", content=content)

    t0 = time.perf_counter()
    page, total = search_service.search(needle)
    elapsed = time.perf_counter() - t0

    max_sec = MAX_SEARCH_N_DOCS_SECONDS[num_docs]
    assert total == num_docs, f"Expected {num_docs} hits, got {total}"
    assert len(page) == min(num_docs, 10), "Default limit is 10"
    assert elapsed < max_sec, f"Search across {num_docs} docs took {elapsed:.2f}s (max {max_sec}s)"
