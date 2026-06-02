
.PHONY: check dev

dev:
	uv run uvicorn app.main:app --reload

check:
	env UV_CACHE_DIR=/private/tmp/uv-cache uv run python -m compileall app
