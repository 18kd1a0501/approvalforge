# ApprovalForge

A production-grade, configurable multi-stage approval workflow API built with FastAPI.

## Why ApprovalForge?

Most approval systems hardcode their workflow stages in code. ApprovalForge stores workflow definitions in the database — any team can define their own approval chain (stages, approvers, order) without a code change or redeployment.

## Live Demo

Base URL: `https://approvalforge.onrender.com`  
Interactive Docs: `https://approvalforge.onrender.com/docs`

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (async) |
| ORM | SQLAlchemy 2.0 async + Alembic |
| Database | PostgreSQL (Neon) |
| Auth | JWT via python-jose |
| Testing | pytest-asyncio, SQLite in-memory |
| CI | GitHub Actions |
| Deploy | Render |

## Architecture

User → FastAPI Router → Service Layer (approval_engine.py) → PostgreSQL

↓

WorkflowDefinition (DB)

WorkflowStage (DB) — dynamic, data-driven

ApprovalRequest (DB)

ApprovalAction (DB)

## Core Concept: Data-Driven Workflow Engine

Workflow stages are rows in the database, not Python enums or hardcoded logic.

```json
{
  "name": "Budget Approval",
  "stages": [
    {"name": "Manager Review", "order": 1, "approver_id": "..."},
    {"name": "Finance Review", "order": 2, "approver_id": "..."},
    {"name": "CFO Sign-off",   "order": 3, "approver_id": "..."}
  ]
}
```

Adding a 4th stage = one INSERT. No deployment needed.

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login, get JWT |
| POST | `/workflows/` | Define a workflow |
| GET | `/workflows/` | List workflows |
| POST | `/requests/` | Submit approval request |
| POST | `/requests/{id}/action` | Approve or reject |
| GET | `/requests/` | List your requests |
| GET | `/health` | Health check |

## State Machine

PENDING → [stage 1 approved] → [stage 2 approved] → ... → APPROVED

PENDING → [any stage rejected] → REJECTED

## Local Setup

```bash
git clone https://github.com/18kd1a0501/approvalforge
cd approvalforge
pip install -r requirements.txt
cp .env.example .env  # fill in DATABASE_URL and SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

## Running Tests

```bash
pytest tests/ -v
```

18 tests covering auth, workflow definitions, and approval engine edge cases.