"""Pipeline tools for the runtime CRM assistant."""

from agent.tools.formatters import pipeline_summary_record, transition_record
from agent.tools.serialization import to_json
from domains.pipeline import service as pipeline_service
from domains.pipeline.models import PipelineEntityType
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession


class PipelineSummaryInput(BaseModel):
    """Input for getting one pipeline summary."""

    entity_type: PipelineEntityType
    entity_id: int = Field(gt=0)


class ListStageTransitionsInput(BaseModel):
    """Input for listing stage transitions."""

    entity_type: PipelineEntityType | None = None
    entity_id: int | None = Field(default=None, gt=0)
    limit: int = Field(default=20, ge=1, le=50)


def make_pipeline_tool_functions(session: AsyncSession, user_id: int):
    """Create async pipeline tool callables bound to request context."""

    async def get_pipeline_summary(
        entity_type: PipelineEntityType,
        entity_id: int,
    ) -> str:
        """Get current stage and transition count for a lead or proposal."""

        summary = await pipeline_service.summarize_entity(
            session,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        return to_json(
            {
                "tool": "get_pipeline_summary",
                "record": pipeline_summary_record(summary),
            }
        )

    async def list_stage_transitions(
        entity_type: PipelineEntityType | None = None,
        entity_id: int | None = None,
        limit: int = 20,
    ) -> str:
        """List stage transitions visible to the authenticated user."""

        transitions = await pipeline_service.list_transitions(
            session,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
        )
        return to_json(
            {
                "tool": "list_stage_transitions",
                "count": len(transitions),
                "records": [transition_record(transition) for transition in transitions],
            }
        )

    return get_pipeline_summary, list_stage_transitions
