from pydantic import BaseModel
from datetime import datetime
from app.models.message import MessageForOpenai
from app.models.agent import Agent


class Job(BaseModel):
    messages: list[MessageForOpenai]
    agent: Agent
    user_id: str
    chat_id: str


class Todo(BaseModel):
    id: int
    created_at: datetime
    scheduled_at: datetime
    job: Job
    finished_at: datetime = None
    


