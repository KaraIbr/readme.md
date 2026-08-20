# Ventura Energy Platform

Integrated operating platform for renewable energy companies. Manages the full commercial lifecycle — from first contact to project close.

## Architecture

```
ventura-energy-platform/
├── erp/          ERP system (CRM + IAM + Frontend)
├── ai/           AI model testing and evaluation tool
└── docs/         Shared documentation
```

| Component | Description | Stack |
|---|---|---|
| **IAM** | Identity & access management, JWT auth, RBAC | FastAPI + Python 3.14 |
| **CRM** | Contacts, leads, proposals, pipeline, technical visits | FastAPI + Python 3.14 |
| **Frontend** | Web interface with role-based UI | React 19 + TypeScript + Vite |
| **AI** | LLM model comparison tool (GPT, DeepSeek, Grok) | Streamlit + Python 3.14 |

## Services

Each service runs independently and communicates over HTTP.

```bash
# IAM (port 8100)
cd erp && uv run python IAM/main.py

# CRM (port 8000) — depends on IAM for auth
cd erp && uv run python CRM/main.py

# Frontend (port 5173)
cd erp/frontend && npm install && npm run dev

# AI (port 8501)
cd ai && uv run streamlit run app.py
```

## Setup

Prerequisites: Python 3.14+, Node.js 18+, [uv](https://docs.astral.sh/uv/)

```bash
# Clone and install
git clone https://github.com/KaraIbr/readme.md.git
cd readme.md
uv sync

# Database migrations (first time)
cd erp
PYTHONPATH=IAM/src uv run python -m alembic -c IAM/alembic.ini upgrade head
PYTHONPATH=CRM/src uv run python -m alembic upgrade head
```

## Development

```bash
# Lint
uv run ruff check erp ai

# Format
uv run ruff format erp ai

# Tests
uv run pytest erp/CRM/tests
uv run pytest erp/IAM/tests
uv run pytest ai/tests
```

CI runs automatically on every push and pull request via GitHub Actions.
