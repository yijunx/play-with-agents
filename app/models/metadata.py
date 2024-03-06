from pydantic import BaseModel


class MetaData(BaseModel):
    user_id: str
    chat_id: str
