# Sequence Diagram: Task CRUD

Task creation, listing, status transitions, and deletion.

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant Router as tasks/router.py
    participant Service as tasks/service.py
    participant Perms as permissions/service.py
    participant Repo as tasks/repository.py
    participant DB as Database

    Note over User,DB: === Create Task ===
    User->>FE: Fill task form
    FE->>Router: POST /api/v1/tasks/
    Router->>Perms: require_permission("crm.tasks.create")
    Perms-->>Router: OK
    Router->>Service: create_task(payload, created_by)
    Service->>Repo: insert_task(task_data)
    Repo->>DB: INSERT INTO task
    DB-->>Repo: Task
    Repo-->>Service: Task
    Service-->>Router: Task
    Router-->>FE: 201 Created

    Note over User,DB: === List Tasks (creator + assigned) ===
    User->>FE: Open task list
    FE->>Router: GET /api/v1/tasks/
    Router->>Perms: require_permission("crm.tasks.read")
    Router->>Service: list_tasks(owner_id, status?, priority?)
    Service->>Repo: select_tasks WHERE created_by = owner<br/>OR assigned_to = owner
    Repo->>DB: SELECT FROM task
    DB-->>Repo: [Task, Task, ...]
    Repo-->>Service: [Task]
    Service-->>Router: [TaskRead]
    Router-->>FE: 200 OK

    Note over User,DB: === Status Transition: TODO → IN_PROGRESS ===
    User->>FE: Click "Start Task"
    FE->>Router: POST /api/v1/tasks/1/status
    Router->>Perms: require_permission("crm.tasks.update")
    Router->>Service: update_task_status(1, "IN_PROGRESS", owner_id)
    Service->>Repo: get_task(1, owner_id)
    Repo->>DB: SELECT FROM task WHERE id = 1<br/>AND (created_by = owner OR assigned_to = owner)
    Service->>Service: validate_status_transition(TODO → IN_PROGRESS)
    Service->>Repo: update_task_status("IN_PROGRESS")
    Repo->>DB: UPDATE task SET status = 'IN_PROGRESS'
    Service-->>Router: Updated Task
    Router-->>FE: 200 OK

    Note over User,DB: === Status Transition: IN_PROGRESS → DONE ===
    User->>FE: Click "Complete Task"
    FE->>Router: POST /api/v1/tasks/1/status
    Router->>Service: update_task_status(1, "DONE", owner_id)
    Service->>Service: validate_status_transition(IN_PROGRESS → DONE)
    Service->>Service: Set completed_at = now()
    Service->>Repo: update_task_status("DONE", completed_at)
    Repo->>DB: UPDATE task SET status = 'DONE',<br/>completed_at = datetime('now')
    Service-->>Router: Updated Task
    Router-->>FE: 200 OK
    FE-->>User: Task completed

    Note over User,DB: === Delete Task ===
    User->>FE: Confirm delete
    FE->>Router: DELETE /api/v1/tasks/1
    Router->>Perms: require_permission("crm.tasks.delete")
    Router->>Service: delete_task(1, owner_id)
    Service->>Repo: delete_task(1, owner_id)
    Repo->>DB: DELETE FROM task WHERE id = 1<br/>AND created_by = owner
    Service-->>Router: OK
    Router-->>FE: 204 No Content
```

## Access Rules

- **List**: tasks where `created_by = current_user` OR `assigned_to = current_user`
- **Read**: same as list — creator or assignee can view
- **Update**: creator only (title, description, priority, due_date, assigned_to)
- **Status change**: creator only
- **Delete**: creator only

## Status Machine

```
TODO ──→ IN_PROGRESS ──→ DONE
   └──→ CANCELLED (any time before DONE)
```

- DONE and CANCELLED are terminal (no further transitions)
- `completed_at` is set automatically on DONE
