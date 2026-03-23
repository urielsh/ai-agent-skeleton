# AI Agent Skeleton

A full-stack template for building AI-powered analysis agents. Users submit input through guided chat, the system collects structured data via LLM, runs a deterministic engine, and returns scored results.

**INPUT &rarr; LLM + ENGINE &rarr; OUTPUT**

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Uvicorn |
| Frontend | React 18, TypeScript, Vite, Zustand, TanStack Query |
| Database | PostgreSQL 16 + Redis 7 (cache) |
| LLM | Anthropic Claude or OpenAI GPT (configurable) |
| Infra | Docker Compose, GitHub Actions CI |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/urisha/ai-agent-skeleton.git
cd ai-agent-skeleton

# 2. Configure
cp config/dev.env.template .env
# Edit .env — set LLM_PROVIDER and matching API key

# 3. Run
docker compose up

# 4. Open
# Frontend: http://localhost:5173
# API: http://localhost:8000/api/health
```

## Project Structure

```
src/
├── backend/app/
│   ├── main.py              # FastAPI app factory
│   ├── config.py            # Pydantic Settings (env-driven)
│   ├── middleware.py         # Rate limiter
│   ├── db/connection.py     # Async PostgreSQL
│   ├── models/
│   │   ├── database.py      # 3 SQLAlchemy tables
│   │   └── schemas.py       # Pydantic DTOs
│   ├── api/                 # REST endpoints
│   │   ├── health.py        # GET /api/health
│   │   ├── sessions.py      # POST/GET/DELETE /api/sessions
│   │   ├── chat.py          # POST /api/sessions/{id}/chat
│   │   └── compute.py       # POST /api/sessions/{id}/compute
│   ├── services/
│   │   ├── llm_router.py    # Anthropic/OpenAI abstraction
│   │   ├── session_manager.py # Redis + DB state management
│   │   └── orchestrator.py  # LLM chat orchestration
│   └── engine/
│       └── blackbox.py      # Sample deterministic engine
│
└── frontend/src/
    ├── App.tsx               # Routes: Landing + Session
    ├── api/                  # HTTP client + React Query hooks
    ├── stores/               # Zustand state
    └── components/           # Layout, ChatPanel, ResultsPanel
```

## Sample Blackbox Engine

The included engine is a placeholder that scores argument strength (1-10). It demonstrates the compute pipeline pattern:

**5 Input Fields:**
- `claim` (string, required) — The argument text
- `confidence_level` (enum: low/medium/high, required)
- `supporting_reasons` (list of strings, required)
- `domain` (string, optional)
- `time_horizon` (string, optional)

**Output:** Score (1-10), label (Weak/Moderate/Strong), summary, breakdown

### Replacing the Blackbox

1. Edit `src/backend/app/engine/blackbox.py` — replace `compute()` with your logic
2. Update the input fields in `src/backend/app/services/session_manager.py` (`REQUIRED_FIELDS`, `ALL_FIELDS`)
3. Update `src/backend/app/models/schemas.py` (`EngineInput`, `EngineOutput`)
4. Update the orchestrator prompt in `src/backend/app/prompts/orchestrator_v1.0.txt`
5. Update frontend types in `src/frontend/src/api/types.ts`

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check (DB + Redis) |
| `POST` | `/api/sessions` | Create session |
| `GET` | `/api/sessions/{id}` | Get session |
| `DELETE` | `/api/sessions/{id}` | End session |
| `POST` | `/api/sessions/{id}/chat` | Send message |
| `POST` | `/api/sessions/{id}/compute` | Run engine |

## Commands

```bash
# Backend tests
cd src/backend && python3 -m pytest -v

# Frontend tests
cd src/frontend && npx vitest run

# Backend standalone
cd src/backend && uvicorn app.main:app --reload --port 8000

# Frontend standalone
cd src/frontend && npm run dev
```

## License

MIT
