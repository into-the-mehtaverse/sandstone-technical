"""Tests for SearchService (linear scan, streaming one doc at a time)."""
import pytest

from app.db.store import DocumentStore
from app.services.search import SearchMatch, SearchService


@pytest.fixture
def store() -> DocumentStore:
    return DocumentStore(path=":memory:")


@pytest.fixture
def service(store: DocumentStore) -> SearchService:
    return SearchService(store)


def test_empty_query_returns_no_hits(service: SearchService, store: DocumentStore) -> None:
    store.create_document("Doc", content="hello world")
    page, total = service.search("")
    assert page == []
    assert total == 0


def test_phrase_match_case_insensitive(service: SearchService, store: DocumentStore) -> None:
    store.create_document("Doc", content="Hello World")
    page, total = service.search("world")
    assert total == 1
    assert page[0].document_id is not None
    assert page[0].title == "Doc"
    assert "world" in page[0].snippet.lower()
    assert page[0].start_index == 6
    assert page[0].end_index == 11


def test_multiple_matches_in_one_doc(service: SearchService, store: DocumentStore) -> None:
    doc = store.create_document("Doc", content="foo bar foo baz foo")
    page, total = service.search("foo")
    assert total == 3
    assert all(m.document_id == doc.id for m in page)
    assert [m.start_index for m in page] == [0, 8, 16]


def test_search_all_docs_vs_filtered_by_id(service: SearchService, store: DocumentStore) -> None:
    d1 = store.create_document("One", content="only in one")
    d2 = store.create_document("Two", content="only in two")
    page_all, total_all = service.search("only")
    assert total_all == 2
    ids_all = {m.document_id for m in page_all}
    assert ids_all == {d1.id, d2.id}

    page_filtered, total_filtered = service.search("only", document_ids=[d1.id])
    assert total_filtered == 1
    assert page_filtered[0].document_id == d1.id


def test_pagination_limit_offset(service: SearchService, store: DocumentStore) -> None:
    doc = store.create_document("Doc", content="x " * 10)  # "x" at 0,2,4,...
    page1, total = service.search("x", limit=3, offset=0)
    assert total == 10
    assert len(page1) == 3
    page2, _ = service.search("x", limit=3, offset=3)
    assert len(page2) == 3
    assert page1[0].start_index != page2[0].start_index


def test_snippet_window(service: SearchService, store: DocumentStore) -> None:
    store.create_document("Doc", content="a" * 30 + "needle" + "b" * 30)
    page, total = service.search("needle", snippet_window=5)
    assert total == 1
    assert "needle" in page[0].snippet
    assert len(page[0].snippet) <= 5 + 6 + 5  # window + needle + window


def test_nonexistent_doc_id_skipped(service: SearchService, store: DocumentStore) -> None:
    d = store.create_document("Doc", content="hello")
    page, total = service.search("hello", document_ids=[d.id, "nonexistent-id"])
    assert total == 1
    assert page[0].document_id == d.id
