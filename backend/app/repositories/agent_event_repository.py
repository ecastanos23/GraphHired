"""Repository for agent trace events."""
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.entities import AgentEvent


class AgentEventRepository:
    """Persist and query agentic trace events."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        agent_name: str,
        action: str,
        reason: str,
        candidate_id: Optional[int] = None,
        application_id: Optional[int] = None,
        input_summary: Optional[str] = None,
        output_summary: Optional[str] = None,
        commit: bool = True,
    ) -> AgentEvent:
        event = AgentEvent(
            candidate_id=candidate_id,
            application_id=application_id,
            agent_name=agent_name,
            action=action,
            reason=reason,
            input_summary=input_summary,
            output_summary=output_summary,
        )
        self.db.add(event)
        if commit:
            self.db.commit()
            self.db.refresh(event)
        return event

    def get_for_candidate(self, candidate_id: int, limit: int = 100) -> List[AgentEvent]:
        return (
            self.db.query(AgentEvent)
            .filter(AgentEvent.candidate_id == candidate_id)
            .order_by(AgentEvent.created_at.desc(), AgentEvent.id.desc())
            .limit(limit)
            .all()
        )
