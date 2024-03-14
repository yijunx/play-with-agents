from pydantic import BaseModel


class Chat(BaseModel):
    id: str
    user_id: str
    ended: bool

    class Config:
        orm_mode = True
