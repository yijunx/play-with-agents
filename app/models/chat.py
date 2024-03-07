from pydantic import BaseModel


class Chat(BaseModel):
    id: int
    user_id: str
    ended: bool
