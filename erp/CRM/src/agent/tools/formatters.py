"""Domain object formatters for agent tools."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from domains.contacts.models import Contact
from domains.leads.models import Lead
from domains.pipeline.models import StageTransition
from domains.pipeline.schemas import PipelineSummary
from domains.proposals.models import Proposal


def contact_record(contact: Contact) -> dict[str, Any]:
    """Return a compact JSON-safe contact record."""

    return {
        "record_type": "contact",
        "id": contact.id,
        "display_name": contact.name,
        "type": contact.type,
        "promoter_id": contact.promoter_id,
        "email": contact.email,
        "phone": contact.phone,
        "city": contact.city,
        "state": contact.state,
        "industry": contact.industry,
        "owner_id": contact.owner_id,
        "created_at": contact.created_at,
        "updated_at": contact.updated_at,
    }


def lead_record(lead: Lead, *, contact: Contact | None = None) -> dict[str, Any]:
    """Return a compact JSON-safe lead record."""

    return {
        "record_type": "lead",
        "id": lead.id,
        "display_name": lead.title,
        "contact_id": lead.contact_id,
        "contact_name": contact.name if contact else None,
        "interest_type": lead.interest_type,
        "qualification_score": lead.qualification_score,
        "current_stage": lead.current_stage,
        "outcome": lead.outcome,
        "owner_id": lead.owner_id,
        "notes": lead.notes,
        "technical_visit_requirement": lead.technical_visit_requirement,
        "created_at": lead.created_at,
        "closed_at": lead.closed_at,
    }


def proposal_record(
    proposal: Proposal,
    *,
    lead: Lead | None = None,
    contact: Contact | None = None,
) -> dict[str, Any]:
    """Return a compact JSON-safe proposal record."""

    pv_system = proposal.pv_system
    bess_system = proposal.bess_system
    return {
        "record_type": "proposal",
        "id": proposal.id,
        "display_name": proposal.name,
        "lead_id": proposal.lead_id,
        "lead_title": lead.title if lead else None,
        "contact_id": lead.contact_id if lead else None,
        "contact_name": contact.name if contact else None,
        "version": proposal.version,
        "installation_address": proposal.installation_address,
        "tariff": proposal.tariff,
        "contracted_demand": proposal.contracted_demand,
        "system_type": proposal.system_type,
        "total_price": proposal.total_price,
        "annual_savings": proposal.annual_savings,
        "currency": proposal.currency,
        "estimated_cost": proposal.estimated_cost,
        "expected_profit": proposal.expected_profit,
        "submitted_at": proposal.submitted_at,
        "valid_until": proposal.valid_until,
        "pv_system": (
            {
                "panel_count": pv_system.panel_count,
                "panel_model": pv_system.panel_model,
                "panel_power": pv_system.panel_power,
                "inverter_model": pv_system.inverter_model,
                "inverter_count": pv_system.inverter_count,
                "inverter_power": pv_system.inverter_power,
                "type_of_surface": pv_system.type_of_surface,
                "total_power_ac": pv_system.total_power_ac,
                "system_size_kw": pv_system.system_size_kw,
                "oversizing_kw": pv_system.oversizing_kw,
                "estimated_annual_kwh": pv_system.estimated_annual_kwh,
                "estimated_savings_kw": pv_system.estimated_savings_kw,
                "connection_mode": pv_system.connection_mode,
                "cost_watt": pv_system.cost_watt,
                "price_watt": pv_system.price_watt,
            }
            if pv_system
            else None
        ),
        "bess_system": (
            {
                "battery_model": bess_system.battery_model,
                "battery_count": bess_system.battery_count,
                "battery_power_kw": bess_system.battery_power_kw,
                "battery_storage_kwh": bess_system.battery_storage_kwh,
                "bess_primary_use": bess_system.bess_primary_use,
                "technical_notes": bess_system.technical_notes,
                "cost_kwh": bess_system.cost_kwh,
                "price_kwh": bess_system.price_kwh,
            }
            if bess_system
            else None
        ),
        "is_complete": proposal.is_complete,
        "current_stage": proposal.current_stage,
        "loss_reason": proposal.loss_reason,
        "proposed_at": proposal.proposed_at,
        "created_by": proposal.created_by,
        "created_at": proposal.created_at,
        "missing_fields": proposal.missing_required_fields,
    }


def pipeline_summary_record(summary: PipelineSummary) -> dict[str, Any]:
    """Return a compact JSON-safe pipeline summary record."""

    return {
        "record_type": "pipeline_summary",
        "entity_type": summary.entity_type,
        "entity_id": summary.entity_id,
        "current_stage": summary.current_stage,
        "transition_count": summary.transition_count,
        "last_transition_at": summary.last_transition_at,
    }


def transition_record(transition: StageTransition) -> dict[str, Any]:
    """Return a compact JSON-safe transition record."""

    return {
        "record_type": "stage_transition",
        "id": transition.id,
        "entity_type": transition.entity_type,
        "entity_id": transition.entity_id,
        "from_stage": transition.from_stage,
        "to_stage": transition.to_stage,
        "transitioned_by": transition.transitioned_by,
        "transitioned_at": transition.transitioned_at,
        "reason": transition.reason,
        "notes": transition.notes,
    }


def proposal_metrics(proposal: Proposal) -> dict[str, Any]:
    """Compute deterministic metrics from one proposal."""

    cents = Decimal("0.01")
    precise = Decimal("0.0001")
    missing_fields: list[str] = []
    pv_system = proposal.pv_system
    bess_system = proposal.bess_system

    metrics: dict[str, Any] = {
        "record_type": "proposal_metrics",
        "proposal_id": proposal.id,
        "proposal_name": proposal.name,
        "total_price": proposal.total_price,
        "currency": proposal.currency,
        "system_size_kw": pv_system.system_size_kw if pv_system else None,
        "estimated_annual_kwh": (pv_system.estimated_annual_kwh if pv_system else None),
        "cost_watt": pv_system.cost_watt if pv_system else None,
        "price_watt": pv_system.price_watt if pv_system else None,
        "annual_savings": proposal.annual_savings,
        "estimated_cost": proposal.estimated_cost,
        "expected_profit": proposal.expected_profit,
        "battery_storage_kwh": bess_system.battery_storage_kwh if bess_system else None,
        "cost_kwh": bess_system.cost_kwh if bess_system else None,
        "price_kwh": bess_system.price_kwh if bess_system else None,
        "missing_fields": missing_fields,
    }

    if proposal.total_price is None:
        missing_fields.append("total_price")
        return metrics

    total_price = Decimal(proposal.total_price)
    if pv_system is None or pv_system.system_size_kw is None:
        missing_fields.append("pv_system.system_size_kw")
    else:
        system_size_kw = Decimal(str(pv_system.system_size_kw))
        metrics["price_per_kw_formula"] = f"{total_price} / {system_size_kw} kW"
        metrics["price_per_kw"] = (total_price / system_size_kw).quantize(
            cents,
            rounding=ROUND_HALF_UP,
        )

    if pv_system is None or pv_system.estimated_annual_kwh is None:
        missing_fields.append("pv_system.estimated_annual_kwh")
    else:
        annual_kwh = Decimal(str(pv_system.estimated_annual_kwh))
        metrics["price_per_estimated_annual_kwh_formula"] = f"{total_price} / {annual_kwh} kWh"
        metrics["price_per_estimated_annual_kwh"] = (total_price / annual_kwh).quantize(
            precise,
            rounding=ROUND_HALF_UP,
        )

    if proposal.estimated_cost is None:
        missing_fields.extend(["estimated_cost", "gross_margin_percent"])
    else:
        estimated_cost = Decimal(proposal.estimated_cost)
        gross_margin = total_price - estimated_cost
        metrics["gross_margin"] = gross_margin.quantize(
            cents,
            rounding=ROUND_HALF_UP,
        )
        metrics["gross_margin_percent"] = (gross_margin / total_price * 100).quantize(
            precise,
            rounding=ROUND_HALF_UP,
        )

    return metrics
