# Entity Relationship Diagram

Full database ER diagram for the shared VERP database (ventura.db).

> Render this file in any Mermaid-compatible viewer (GitHub, VS Code, etc.).

```mermaid
erDiagram
    IAM_USER {
        int id PK
        varchar email UK
        varchar full_name
        varchar hashed_password
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    IAM_SERVICE_ACCESS {
        int id PK
        int user_id FK
        varchar service_key
        boolean is_active
        int granted_by FK
        datetime created_at
        datetime updated_at
    }

    IAM_USER_PERMISSION_OVERRIDE {
        int id PK
        int user_id FK
        varchar permission
        varchar effect
        int changed_by FK
        datetime created_at
        datetime updated_at
    }

    CRM_USER_ACCESS {
        int user_id PK FK
        varchar role
        boolean is_active
        int changed_by FK
        datetime created_at
        datetime updated_at
    }

    CRM_USER_PERMISSION_OVERRIDE {
        int id PK
        int user_id FK
        varchar permission
        varchar effect
        int changed_by FK
        datetime created_at
        datetime updated_at
    }

    PROMOTER {
        int id PK
        varchar name
        varchar phone
        int owner_id FK
        datetime created_at
        datetime updated_at
    }

    CONTACT {
        int id PK
        varchar type
        varchar name
        varchar address_line
        varchar city
        varchar state
        varchar postal_code
        int promoter_id FK
        int owner_id FK
        datetime created_at
        datetime updated_at
    }

    INDIVIDUAL_CONTACT_PROFILE {
        int id PK
        int contact_id FK
        varchar email
        varchar phone
    }

    COMPANY_CONTACT_PROFILE {
        int id PK
        int contact_id FK
        varchar industry
    }

    COMPANY_CONTACT_PERSON {
        int id PK
        int company_contact_id FK
        varchar name
        varchar phone
        varchar email
        varchar position
        datetime created_at
        datetime updated_at
    }

    LEAD {
        int id PK
        int contact_id FK
        varchar title
        varchar interest_type
        int qualification_score
        varchar current_stage
        varchar outcome
        int owner_id FK
        varchar notes
        varchar technical_visit_requirement
        datetime created_at
        datetime closed_at
    }

    LEAD_ASSIGNMENT {
        int id PK
        int lead_id FK
        int user_id FK
        int assigned_by FK
        boolean is_active
        datetime assigned_at
        datetime unassigned_at
    }

    LEAD_DOCUMENT {
        int id PK
        int lead_id FK
        varchar title
        varchar original_filename
        varchar content_type
        varchar stored_path
        int size_bytes
        int uploaded_by FK
        datetime uploaded_at
    }

    LEAD_ELECTRICITY_BILL {
        int id PK
        int lead_id FK
        varchar title
        varchar original_filename
        varchar content_type
        varchar stored_path
        int size_bytes
        int uploaded_by FK
        datetime uploaded_at
    }

    LEAD_INTERACTION {
        int id PK
        int lead_id FK
        varchar interaction_type
        varchar title
        varchar notes
        datetime interaction_date
        int created_by FK
        datetime created_at
        datetime updated_at
    }

    PROPOSAL {
        int id PK
        int lead_id FK
        varchar name
        varchar version
        varchar installation_address_line
        varchar installation_city
        varchar installation_state
        varchar installation_postal_code
        varchar tariff
        float contracted_demand
        varchar system_type
        decimal total_price
        decimal annual_savings
        varchar currency
        decimal estimated_cost
        decimal expected_profit
        datetime submitted_at
        date valid_until
        varchar current_stage
        varchar loss_reason
        datetime proposed_at
        int created_by FK
        datetime created_at
    }

    PROPOSAL_PV_SYSTEM {
        int id PK
        int proposal_id FK
        int panel_count
        varchar panel_model
        float panel_power
        varchar inverter_model
        int inverter_count
        float inverter_power
        varchar type_of_surface
        float total_power_ac
        float system_size_kw
        float oversizing_kw
        float estimated_annual_kwh
        float estimated_savings_kw
        varchar connection_mode
        decimal cost_watt
        decimal price_watt
    }

    PROPOSAL_BESS_SYSTEM {
        int id PK
        int proposal_id FK
        varchar battery_model
        int battery_count
        float battery_power_kw
        float battery_storage_kwh
        varchar bess_primary_use
        varchar technical_notes
        decimal cost_kwh
        decimal price_kwh
    }

    PROPOSAL_COMMERCIAL_DOCUMENT {
        int id PK
        int proposal_id FK
        varchar title
        varchar original_filename
        varchar content_type
        varchar stored_path
        int size_bytes
        int uploaded_by FK
        datetime uploaded_at
    }

    PROPOSAL_DOCUMENT {
        int id PK
        int proposal_id FK
        varchar title
        varchar classification
        varchar original_filename
        varchar content_type
        varchar stored_path
        int size_bytes
        int uploaded_by FK
        datetime uploaded_at
    }

    PROPOSAL_ASSIGNMENT {
        int id PK
        int proposal_id FK
        int user_id FK
        int assigned_by FK
        boolean is_active
        datetime assigned_at
        datetime unassigned_at
    }

    TECHNICAL_VISIT {
        int id PK
        int lead_id FK
        varchar status
        datetime scheduled_at
        varchar receiver_name
        varchar receiver_phone
        varchar notes
        int created_by FK
        datetime created_at
        datetime updated_at
        datetime completed_at
        datetime cancelled_at
        varchar cancellation_reason
    }

    TECHNICAL_VISIT_ASSIGNEE {
        int id PK
        int visit_id FK
        varchar name
        int user_id FK
        datetime created_at
    }

    TECHNICAL_VISIT_ATTACHMENT {
        int id PK
        int visit_id FK
        varchar title
        varchar file_kind
        varchar original_filename
        varchar content_type
        varchar stored_path
        int size_bytes
        int uploaded_by FK
        datetime uploaded_at
    }

    PROPOSAL_TECHNICAL_VISIT {
        int id PK
        int proposal_id FK
        int technical_visit_id FK
        varchar relationship_type
        varchar notes
        int linked_by FK
        datetime linked_at
    }

    TASK {
        int id PK
        varchar title
        varchar description
        varchar status
        varchar priority
        datetime due_date
        datetime completed_at
        int contact_id FK
        int lead_id FK
        int assigned_to FK
        int created_by FK
        datetime created_at
        datetime updated_at
    }

    STAGE_TRANSITION {
        int id PK
        varchar entity_type
        int entity_id
        varchar from_stage
        varchar to_stage
        int transitioned_by FK
        datetime transitioned_at
        varchar reason
        varchar notes
    }

    IAM_USER ||--o{ IAM_SERVICE_ACCESS : "grants access"
    IAM_USER ||--o{ IAM_USER_PERMISSION_OVERRIDE : "has IAM overrides"
    IAM_USER ||--o{ CRM_USER_ACCESS : "has CRM role"
    IAM_USER ||--o{ CRM_USER_PERMISSION_OVERRIDE : "has CRM overrides"
    IAM_USER ||--o{ PROMOTER : "owns"
    IAM_USER ||--o{ CONTACT : "owns"
    IAM_USER ||--o{ LEAD : "owns or follows up"
    IAM_USER ||--o{ PROPOSAL : "creates"
    IAM_USER ||--o{ TASK : "creates"
    IAM_USER ||--o{ TASK : "assigned to"

    PROMOTER ||--o{ CONTACT : "promotes"
    CONTACT ||--o| INDIVIDUAL_CONTACT_PROFILE : "individual profile"
    CONTACT ||--o| COMPANY_CONTACT_PROFILE : "company profile"
    CONTACT ||--o{ COMPANY_CONTACT_PERSON : "company people"
    CONTACT ||--o{ LEAD : "generates"
    CONTACT ||--o{ TASK : "linked to"

    LEAD ||--o{ LEAD_ASSIGNMENT : "sales assignments"
    LEAD ||--o{ LEAD_DOCUMENT : "documents"
    LEAD ||--o{ LEAD_ELECTRICITY_BILL : "electricity bills"
    LEAD ||--o{ LEAD_INTERACTION : "interactions"
    LEAD ||--o{ PROPOSAL : "proposal variants"
    LEAD ||--o{ TECHNICAL_VISIT : "technical visits"
    LEAD ||--o{ TASK : "linked to"

    PROPOSAL ||--o| PROPOSAL_PV_SYSTEM : "PV details"
    PROPOSAL ||--o| PROPOSAL_BESS_SYSTEM : "BESS details"
    PROPOSAL ||--o{ PROPOSAL_DOCUMENT : "internal documents"
    PROPOSAL ||--o{ PROPOSAL_COMMERCIAL_DOCUMENT : "commercial PDFs"
    PROPOSAL ||--o{ PROPOSAL_ASSIGNMENT : "technical assignments"
    PROPOSAL ||--o{ PROPOSAL_TECHNICAL_VISIT : "visit evidence"

    TECHNICAL_VISIT ||--o{ TECHNICAL_VISIT_ASSIGNEE : "assignees"
    TECHNICAL_VISIT ||--o{ TECHNICAL_VISIT_ATTACHMENT : "attachments"
    TECHNICAL_VISIT ||--o{ PROPOSAL_TECHNICAL_VISIT : "proposal links"
```
