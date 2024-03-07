from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.sqlalchemy.chat import MessageORM
from app.models.message import RoleEnum, MessageCreate, AgentMessageCreate
from app.models.user import User



def create_message_from_user(db: Session, chat_id: str, message_create: MessageCreate, user: User) -> MessageORM:
    db_item = MessageORM(
        chat_id=chat_id,
        role=RoleEnum.user,
        # content
        content=message_create.actual_content,
        actual_content=message_create.actual_content,
        # metadata
        created_at=datetime.now(timezone.utc),
        created_by=user.id,
        created_by_name=user.name,
    )
    db.add(db_item)
    db.flush()
    return db_item


def create_message_from_agent(db: Session, message_create_from_agent: AgentMessageCreate) -> MessageORM:
    db_item = MessageORM(
        chat_id=message_create_from_agent.chat_id,
        role=RoleEnum.assistant,
        # content
        content=message_create_from_agent.content,
        actual_content=message_create_from_agent.actual_content,
        # metadata
        created_at=datetime.now(timezone.utc),
        created_by=message_create_from_agent.agent_id,
        created_by_name=message_create_from_agent.agent_name,
    )
    db.add(db_item)
    db.flush()
    return db_item


def get_many(db: Session, chat_id: int) -> list[MessageORM]:
    return db.query(MessageORM).filter(MessageORM.chat_id==chat_id).order_by(MessageORM.created_at).all()
