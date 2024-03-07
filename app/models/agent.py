from pydantic import BaseModel


class Agent(BaseModel):
    id: int | None
    name: str | None
    occupation: str
    temper: str | None
    impersonate_who: str | None
    remaining_replies_count: int

    class Config:
        orm_mode = True
