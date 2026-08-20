# VERP — Ventura Energy Software

An integrated operating platform for companies that sell and install renewable energy systems (photovoltaic and battery storage).

---

## What It Does

VERP manages the **full commercial lifecycle** of renewable energy projects — from the first contact with a potential customer to closing the deal.

### Core Capabilities

| Area | What It Handles |
|---|---|
| **Contacts** | Customers, companies, promoters, and contact profiles |
| **Leads** | Sales opportunities tracking from inquiry to close |
| **Proposals** | Technical and commercial offers with PV/BESS specifications |
| **Technical Visits** | On-site inspections, assignees, and evidence attachments |
| **Pipeline** | Stage transitions with full audit history |
| **AI Assistant** | Natural-language queries about sales data and pipeline status |
| **Access Control** | Role-based permissions (Admin, Manager, Sales, Technical) |

### Business Flow

```
Contact → Lead → Proposal → Technical Visit → Won / Lost
   │         │         │            │
   │         │         │            └── On-site inspection & documentation
   │         │         └── Technical & commercial offer variants
   │         └── Bounded sales opportunity with stage tracking
   └── Permanent customer record
```


## Architecture

VERP is a **service-oriented platform** (not a monolith). Each service runs independently but shares identity and data.

```
VERP/
├── IAM/        → Identity & Access Management (users, auth, permissions)
├── CRM/        → Customer Relationship Management (sales lifecycle)
├── frontend/   → React web application
└── _docs/      → Platform documentation
```

| Service | Purpose | Technology |
|---|---|---|
| **IAM** | User accounts, authentication, JWT tokens, service access | FastAPI + Python |
| **CRM** | Contacts, leads, proposals, pipeline, AI agent | FastAPI + Python |
| **Frontend** | Web interface with role-based UI | React + TypeScript |


## Key Features

### Sales Pipeline Management
- Track leads through stages: **New → Qualifying → Proposal Phase → Closed**
- Every stage transition is recorded with timestamps and user attribution
- Automatic pipeline updates when proposals are won or lost

### Proposal Management
- Create multiple offer variants per lead
- Track PV (solar) and BESS (battery) technical specifications
- Generate commercial PDFs
- Link proposals to technical visits

### Role-Based Access Control
- **Admin**: Full system access
- **Manager**: Team oversight and approvals
- **Sales**: Lead and proposal management
- **Technical**: Technical visit execution

### AI-Powered Assistant
- Ask questions about your sales data in natural language
- Query pipeline status, proposal details, and contact information
- Built on Azure OpenAI with domain-specific tools


## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.14+, FastAPI, SQLModel (SQLAlchemy 2.x) |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Auth | JWT tokens, bcrypt password hashing |
| AI | Azure OpenAI GPT-5.4, LangGraph, LangChain |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Quality | Ruff (lint), MyPy (types), Pytest (tests) |



## Getting Started

### Prerequisites
- Python 3.14+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Backend Setup

```bash
# Install dependencies
uv sync

# Set up database (run IAM migrations first, then CRM)
PYTHONPATH=IAM/src uv run python -m alembic -c IAM/alembic.ini upgrade head
PYTHONPATH=CRM/src uv run python -m alembic upgrade head

# Start IAM service (port 8100)
uv run python IAM/main.py

# Start CRM service (port 8000)
uv run python CRM/main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### First Login

On a fresh database, the first user is created automatically with admin privileges. Use the bootstrap credentials shown in the startup logs.

---

## Documentation

| Document | Location | Audience |
|---|---|---|
| Platform overview | `_docs/vision_scope.md` | Everyone |
| CRM service details | `_docs/crm.md` | Developers |
| IAM service details | `_docs/iam.md` | Developers |
| Database schema | `_docs/venturadb.md` | Developers |
| API reference | `CRM/docs/rest-json-bodies.md` | Frontend developers |
| Architecture diagrams | `docs/` | Technical leads |

---

## License

Private software — Ventura Energy.
