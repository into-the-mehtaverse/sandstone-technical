.PHONY: dev dev-backend dev-frontend test

# Start backend and frontend in parallel. Ctrl+C to stop both.
dev:
	(cd apps/backend && $(MAKE) dev) & \
	(cd apps/web && npm run dev) & \
	wait

dev-backend:
	cd apps/backend && $(MAKE) dev

dev-frontend:
	cd apps/web && npm run dev

test:
	cd apps/backend && uv run pytest -v
