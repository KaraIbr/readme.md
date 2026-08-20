# Component Diagram

CRM domain structure and layer dependencies.

```mermaid
graph TB
    subgraph "API Layer"
        Router["router.py<br/>FastAPI APIRouter"]
        Deps["dependencies.py<br/>CurrentUser, get_db_session"]
    end

    subgraph "Domain Layer"
        Service["service.py<br/>Business logic"]
        Repository["repository.py<br/>SQLAlchemy queries"]
        Schemas["schemas.py<br/>Pydantic DTOs"]
        Models["models.py<br/>SQLModel entities"]
    end

    subgraph "External Dependencies"
        Permissions["permissions/service.py<br/>Authorization"]
        Pipeline["pipeline/service.py<br/>Stage transitions"]
        OtherDomains["Other domain services<br/>Cross-domain calls"]
    end

    subgraph "Core"
        Config["core/config.py<br/>BaseSettings"]
        DB["core/database.py<br/>AsyncSession"]
        Security["core/security.py<br/>JWT, bcrypt"]
    end

    Router -->|"calls"| Service
    Router -->|"validates"| Schemas
    Router -->|"auth"| Deps
    Service -->|"queries"| Repository
    Service -->|"validates"| Schemas
    Service -->|"checks"| Permissions
    Service -->|"transitions"| Pipeline
    Service -->|"cross-domain"| OtherDomains
    Repository -->|"reads/writes"| Models
    Models -->|"ORM"| DB

    Deps --> Security
    Router -.->|"never directly"| Repository
    Router -.->|"never directly"| Models
    Repository -.->|"never calls"| Service

    style Router fill:#e1f5fe
    style Service fill:#f3e5f5
    style Repository fill:#e8f5e9
    style Models fill:#fff3e0
    style Schemas fill:#fce4ec
    style Permissions fill:#f5f5f5
    style Pipeline fill:#f5f5f5
```

## Layer Dependency Rule

```
router.py  -->  service.py  -->  repository.py  -->  models.py
    |               ^
    v               |
 schemas.py    (may call other domain services)
```

- `router.py` only knows `service.py` and `schemas.py`. Never queries the DB directly.
- `service.py` orchestrates business logic, calls `repository.py`, may call other domain services.
- `repository.py` is the only layer that writes SQLModel/SQLAlchemy queries.
- `models.py` only imports from `sqlmodel` and Python builtins. No app-level imports.

## Domain Map

```mermaid
graph LR
    subgraph "CRM Domains"
        Users["users/<br/>IAM references"]
        Permissions["permissions/<br/>Access control"]
        Contacts["contacts/<br/>People & orgs"]
        Leads["leads/<br/>Sales opportunities"]
        Proposals["proposals/<br/>Offer variants"]
        TechnicalVisits["technical_visits/<br/>On-site inspections"]
        Tasks["tasks/<br/>Work items"]
        Pipeline["pipeline/<br/>Stage transitions"]
    end

    subgraph "Infrastructure"
        Agent["agent/<br/>AI assistant"]
        Core["core/<br/>Config, DB, security"]
        API["api/v1/<br/>Route aggregation"]
    end

    Contacts --> Users
    Leads --> Contacts
    Leads --> Permissions
    Proposals --> Leads
    Proposals --> Permissions
    TechnicalVisits --> Leads
    TechnicalVisits --> Proposals
    Tasks --> Contacts
    Tasks --> Leads
    Pipeline -.-> Leads
    Pipeline -.-> Proposals
    Agent --> Leads
    Agent --> Proposals
    Agent --> Contacts
    API --> Contacts
    API --> Leads
    API --> Proposals
    API --> TechnicalVisits
    API --> Tasks
    API --> Pipeline
    API --> Permissions
```
