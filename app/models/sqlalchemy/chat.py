from app.models.sqlalchemy.base import Base
from sqlalchemy import Boolean, DateTime, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime


class AgentORM(Base):
    __tablename__ = "agents_table"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    chat_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    occupation: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    temper: Mapped[str] = mapped_column(String, nullable=True)
    impersonate_who: Mapped[str] = mapped_column(String, nullable=True)
    remaining_replies_count: Mapped[int] = mapped_column(Integer, nullable=False)


class ChatORM(Base):
    __tablename__ = "chats_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)

    # for whom this conversation is for
    user_id: Mapped[str] = mapped_column(String, nullable=False)

    # and ended by default is False
    ended: Mapped[bool] = mapped_column(Boolean, server_default="false")


class MessageORM(Base):
    __tablename__ = "messages_table"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    # for which chat is for
    chat_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # then we have the agents, without relation first
    role: Mapped[str] = mapped_column(String, nullable=False)
    # this content is for openai
    content: Mapped[str] = mapped_column(String, nullable=False)

    actual_content: Mapped[str] = mapped_column(String, nullable=False)

    # metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_by_name: Mapped[str] = mapped_column(String, nullable=False)
