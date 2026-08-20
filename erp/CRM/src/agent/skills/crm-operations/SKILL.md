---
name: "crm-operations"
description: "Handle CRM write-intent safely by requiring explicit confirmation before changes."
---

# CRM Operations

Use this skill when the user asks to create, update, move, close, mark, or otherwise mutate CRM data.

1. Identify the target record and intended change.
2. Ask for confirmation before executing any write.
3. Do not call write tools unless the user has explicitly confirmed the exact change.
4. If write tools are unavailable for the requested action, explain that the action is not supported by the agent yet.
5. Preserve owner scoping and domain service invariants.
