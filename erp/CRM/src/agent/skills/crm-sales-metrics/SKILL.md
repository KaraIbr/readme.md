---
name: "crm-sales-metrics"
description: "Compute deterministic CRM sales metrics such as price per kW, totals, budgets, and margin availability."
---

# CRM Sales Metrics

Use this skill for numeric questions about prices, costs, budgets, margins, power, energy, totals, or unit economics.

1. Use tools or deterministic Python calculations for arithmetic.
2. Do not do model arithmetic in the final answer.
3. Report calculated values exactly as returned by metric tools.
4. Do not show an equation unless the tool returned that exact formula field.
5. If a margin or cost is requested but the returned proposal data is missing `estimated_cost`, `expected_profit`, or another required value, state the missing field.
6. For proposal metrics, report the source proposal ID and relevant inputs.
7. For PV unit economics, use values from `pv_system`; for BESS-only proposals, state when a PV-only metric such as price per PV kW is not available.
8. Keep units explicit: kW, kWh, currency amount, or percent.
