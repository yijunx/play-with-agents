from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.sqlalchemy.chat import AgentORM
from app.models.agent import Agent
from app.models.exceptions import CustomException


def create(db: Session, chat_id: str, agent: Agent) -> AgentORM:
    db_item = AgentORM(
        chat_id=chat_id,
        occupation=agent.occupation,
        name=agent.name,
        temper=agent.temper,
        impersonate_who=agent.impersonate_who,
        remaining_replies_count=agent.remaining_replies_count,
    )
    db.add(db_item)
    db.flush()
    return db_item


def get_one(db: Session, agent_id: int) -> AgentORM:
    db_item = db.query(AgentORM).filter(AgentORM.id == agent_id).first()
    if not db_item:
        raise CustomException(http_code=404, message="agent not found")
    return db_item


def get_many(db: Session, chat_id: int) -> list[AgentORM]:
    return db.query(AgentORM).filter(AgentORM.chat_id == chat_id).all()
