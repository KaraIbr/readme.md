# Architecture

## System Overview

Ventura Energy Platform is a service-oriented system composed of four independent services that communicate over HTTP.

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                             │
│                   React 19 + TypeScript                     │
│                      (port 5173)                            │
└──────────────┬──────────────────────────┬───────────────────┘
               │ REST API                 │ REST API
       ┌───────▼───────┐          ┌───────▼───────┐
       │     CRM        │◄────────►│     IAM       │
       │   FastAPI      │  auth    │   FastAPI     │
       │  (port 8000)   │  check   │  (port 8100)  │
       └───────┬────────┘          └───────────────┘
               │
               │ Azure OpenAI API
       ┌───────▼────────┐
       │   AI Service   │
       │   Streamlit    │
       │  (port 8501)   │
       └────────────────┘
```

## Service Communication

| From | To | Protocol | Purpose |
|---|---|---|---|
| Frontend | CRM | REST/JSON | CRUD operations, pipeline, proposals |
| Frontend | IAM | REST/JSON | Login, token refresh, user info |
| CRM | IAM | REST/JSON | Token validation, permission checks |
| AI | Azure OpenAI | HTTPS | LLM inference (GPT, DeepSeek, Grok) |

## Data Flow

```
Contact → Lead → Proposal → Technical Visit → Won / Lost
   │         │         │            │
   │         │         │            └── On-site inspection and documentation
   │         │         └── Technical and commercial offer variants
   │         └── Bounded sales opportunity with stage tracking
   └── Permanent customer record
```

## IAM Service

Handles identity and access management. All other services delegate authentication to IAM.

- JWT token issuance and validation
- Role-based access control (Admin, Manager, Sales, Technical)
- User CRUD and permission management

## CRM Service

Core business logic for the sales lifecycle.

- Contacts and companies
- Leads with pipeline stage tracking
- Proposals with PV/BESS technical specifications
- Technical visits with scheduling and attachments
- AI assistant for natural language queries on sales data

## AI Service

Standalone tool for testing and comparing LLM models hosted on Azure.

- Supports GPT-5.6, DeepSeek V4 Pro, Grok 4.3
- Configurable reasoning levels per model
- PDF and image attachment processing
- Results comparison across models
