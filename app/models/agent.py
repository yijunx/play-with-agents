from pydantic import BaseModel


class Agent(BaseModel):
    name: str | None
    occupation: str
    temper: str | None
    impersonate_who: str | None
