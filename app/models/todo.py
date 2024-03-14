from pydantic import BaseModel
from datetime import datetime
from app.models.message import MessageForOpenai
from app.models.agent import Agent


class Job(BaseModel):
    messages: list[MessageForOpenai]
    agent: Agent
    user_id: str
    chat_id: str
    task_id: str | None


class Todo(BaseModel):
    id: str
    created_at: datetime
    scheduled_at: datetime
    job: Job
    chat_id: str

    class Config:
        orm_mode = True
