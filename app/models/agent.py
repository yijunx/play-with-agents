from pydantic import BaseModel


class Agent(BaseModel):
    who: str
    temper: str
    impersonnate_who: str | None
