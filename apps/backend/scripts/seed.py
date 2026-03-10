"""Seed the document DB with initial content. Run from backend root: uv run python scripts/seed.py"""
import sys
from pathlib import Path

# Ensure app is importable (backend root = cwd when using uv run from apps/backend)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.db.store import DocumentStore
from app.services.documents import DocumentService
from app.services.extraction_utils import extract_text_from_bytes, is_docx_file

# Sandstone_ documents share this party_id; party_name and doc_type set below
SANDSTONE_PARTY_ID = "sandstone-real-estate-llc"
SANDSTONE_PARTY_NAME = "Sandstone_Real_Estate_LLC"
DOC_TYPE_LOAN_AGREEMENT = "loan_agreement"
DOC_TYPE_TEMPLATE = "template"

# Fixed IDs for seeded documents so you can call GET /documents/{id} reliably
SEED_ID_WELCOME = "welcome"
SEED_ID_SECOND_DOC = "second-doc"


def seed_from_inline(store: DocumentStore) -> int:
    """Create a few documents with fixed content and fixed IDs."""
    service = DocumentService(store)
    docs = [
        (SEED_ID_WELCOME, "Welcome", "Hello. This is the first seed document. Edit me."),
        (SEED_ID_SECOND_DOC, "Second doc", "Short text for testing replacements and removals."),
    ]
    for doc_id, title, content in docs:
        service.create_document(title, content=content, id=doc_id)
    return len(docs)


def seed_from_folder(store: DocumentStore, folder: Path) -> int:
    """
    Load .docx files from folder; extract text and create documents.
    - sandstone_* → same party_id, party_name Sandstone_Real_Estate_LLC, doc_type loan_agreement
    - loan agreement template (name contains 'template') → party_id/party_name blank, doc_type template
    - others → no party/type set
    """
    service = DocumentService(store)
    count = 0
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() != ".docx":
            continue
        with path.open("rb") as f:
            data = f.read()
        if not is_docx_file(path.name, None):
            continue
        content = extract_text_from_bytes(data, filename=path.name, content_type=None)
        stem = path.stem
        stem_lower = stem.lower()
        # Use stem as doc id so GET /documents/{stem} works (e.g. sandstone_1, loan_agreement_template)
        doc_id = stem
        if stem_lower.startswith("sandstone_"):
            service.create_document(
                stem,
                content=content,
                id=doc_id,
                party_id=SANDSTONE_PARTY_ID,
                party_name=SANDSTONE_PARTY_NAME,
                doc_type=DOC_TYPE_LOAN_AGREEMENT,
            )
        elif "template" in stem_lower:
            service.create_document(
                stem,
                content=content,
                id=doc_id,
                party_id=None,
                party_name=None,
                doc_type=DOC_TYPE_TEMPLATE,
            )
        else:
            service.create_document(stem, content=content, id=doc_id)
        count += 1
    return count


def main() -> None:
    db_path = settings.get_document_db_path()
    store = DocumentStore(path=db_path)
    seed_docs = Path(__file__).resolve().parent.parent / "seed_docs"
    total = 0
    if seed_docs.is_dir() and any(seed_docs.glob("*.docx")):
        n = seed_from_folder(store, seed_docs)
        total += n
        print(f"Loaded {n} document(s) from seed_docs/")
    total += seed_from_inline(store)
    print(f"Created {total} seed document(s) in {db_path}")
    print("Fixed IDs: GET /documents/welcome, GET /documents/second-doc, and GET /documents/<stem> for seed_docs (e.g. sandstone_1, loan_agreement_template)")


if __name__ == "__main__":
    main()
