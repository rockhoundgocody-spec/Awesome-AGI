# AGENTS.md — Base44 Dev Environment

## Repository Type

This is a **content-only** repository ("Awesome AGI Resources" — a curated link list). There is no application code, no `package.json`, no Dockerfile, no build system. The only meaningful content is `README.md` and the `imgs/` directory.

## Why It "Failed to Start"

Commit `4d4f094c66` (the branch HEAD) only adds a line to `README.md`. There was never a runnable application, so nothing listened on port 3000 — the preview stayed on the loading screen.

## Dev Setup (Added by Base44)

A minimal Python server (`server.py`) renders `README.md` to styled HTML on every request, so edits to the README are reflected immediately (just refresh the preview). Images in `imgs/` are served as static files.

- **Stack:** `python:3.12-slim` + `markdown` library, via `docker-compose.base44.yml`
- **Port:** 3000 (mapped from container)
- **Live reload:** README is re-read on each request — no watcher needed; refresh the preview to see changes
- **Healthcheck:** `GET /` must return 200

## Useful Commands

```bash
# Start the preview
docker compose -f docker-compose.base44.yml up -d --build

# Check status
docker compose -f docker-compose.base44.yml ps

# View logs
docker compose -f docker-compose.base44.yml logs -f web

# Stop
docker compose -f docker-compose.base44.yml down
```

## Secrets

None required. This is a static content site with no external dependencies.
