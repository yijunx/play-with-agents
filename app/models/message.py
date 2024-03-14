from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class RoleEnum(str, Enum):
    user = "user"
    system = "user"
    assistant = "assistant"


# response = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#     {"role": "user", "content": "Where was it played?"}
#   ]
# )


class MessageCreate(BaseModel):
    actual_content: str


class AgentMessageCreate(BaseModel):
    id: str
    agent_name: str
    agent_id: int
    actual_content: str
    content: str
    chat_id: str


class MessageForOpenai(BaseModel):
    role: RoleEnum
    content: str

    class Config:
        orm_mode = True


class MessageForFrontend(BaseModel):
    id: str
    created_by: str
    created_by_name: str
    created_at: datetime
    actual_content: str
    chat_id: str

    class Config:
        orm_mode = True
