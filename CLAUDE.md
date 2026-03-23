# CLAUDE.md — AI Agent Skeleton

## What This Project Is

A full-stack template for building AI-powered analysis agents. Users submit input through guided chat, the system collects structured data via LLM, runs a deterministic engine, and returns scored results.

**INPUT -> LLM + ENGINE -> OUTPUT**

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Uvicorn |
| Frontend | React 18, TypeScript, Vite, Zustand, TanStack Query |
| Database | PostgreSQL 16 + Redis 7 (cache) |
| LLM | Anthropic Claude or OpenAI GPT (configurable) |
| Infra | Docker Compose, GitHub Actions CI |

## Project Structure

```
src/backend/app/
  api/            # REST endpoints: health, sessions, chat, compute
  services/       # LLM router, session manager, orchestrator
  engine/         # Deterministic blackbox engine
  models/         # SQLAlchemy models (3 tables) + Pydantic schemas
  prompts/        # Versioned prompt templates
  db/             # Async DB connection
src/frontend/src/
  components/     # Layout, ChatPanel, ResultsPanel, pages, shared
  api/            # HTTP client, React Query hooks, TypeScript types
  stores/         # Zustand (session + UI state)
```

## Commands

```bash
# Full stack (4 Docker containers)
docker compose up

# Backend tests
cd src/backend && python3 -m pytest -v

# Frontend tests
cd src/frontend && npx vitest run

# Backend standalone
cd src/backend && uvicorn app.main:app --reload --port 8000

# Frontend standalone
cd src/frontend && npm run dev

# Lint
cd src/backend && ruff check app/ tests/
cd src/frontend && npx tsc --noEmit
```

## Architecture Decisions

1. **Session-centric API**: All state hangs off session ID. No auth.
2. **Dual-write drafts**: Redis (fast reads) + PostgreSQL (durability)
3. **Content-hash compute cache**: SHA-256 of engine input, avoids duplicate computation
4. **Multi-provider LLM**: `LLM_PROVIDER` selects Anthropic or OpenAI at runtime
5. **SQLite-compatible models**: `JSONVariant` type renders JSONB on PostgreSQL, JSON on SQLite

## Configuration

All via env vars in `config/dev.env.template`:

| Variable | Required | Default |
|----------|----------|---------|
| `LLM_PROVIDER` | Yes | `anthropic` |
| `ANTHROPIC_API_KEY` | When provider=anthropic | — |
| `OPENAI_API_KEY` | When provider=openai | — |
| `DATABASE_URL` | No | `postgresql+asyncpg://appdev:appdev@db:5432/appdev` |
| `REDIS_URL` | No | `redis://redis:6379/0` |

## Replacing the Blackbox Engine

1. Edit `src/backend/app/engine/blackbox.py` — replace `compute()` with your logic
2. Update input fields in `src/backend/app/services/session_manager.py` (`REQUIRED_FIELDS`, `ALL_FIELDS`)
3. Update `src/backend/app/models/schemas.py` (`EngineInput`, `EngineOutput`)
4. Update the orchestrator prompt in `src/backend/app/prompts/orchestrator_v1.0.txt`
5. Update frontend types in `src/frontend/src/api/types.ts`

## Style and Conventions

- **Backend**: Python, async/await, type hints, ruff linting
- **Frontend**: TypeScript strict mode, `@/` path alias
- **Database**: UUID primary keys, JSONB for complex data, snake_case
- **API**: Session-centric REST, 422 for validation errors
