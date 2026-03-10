PYTHON = uv run python
UVICORN = uv run uvicorn

DB_PATH = app/db/documents.db

.PHONY: dev seed clean-db

dev: clean-db seed
	$(UVICORN) app.app:app --reload

seed:
	$(PYTHON) scripts/seed.py

clean-db:
	rm -f $(DB_PATH)

