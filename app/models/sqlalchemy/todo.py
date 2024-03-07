from app.models.sqlalchemy.base import Base
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    String,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime


class TodoORM(Base):
    __tablename__ = "todos_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    chat_id: Mapped[int] = mapped_column(int, nullable=False)
    job: Mapped[dict] = mapped_column(JSON, nullable=False)


# class FinishedTodoORM(Base):
#     __tablename__ = "finished_todos_table"
#     id: Mapped[str] = mapped_column(String, primary_key=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
#     scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
#     job: Mapped[dict] = mapped_column(JSON, nullable=False)
#     finished_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


# by right we need to have a finished todo table
# ones a todo is finsihed it will neeeds to come to finished todo table
