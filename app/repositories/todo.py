from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.sqlalchemy.todo import TodoORM, FinishedTodoORM

from app.models.exceptions import CustomException


def create(db: Session, ) -> TodoORM:
    db_item = ChatORM(
        user_id=user_id
    )
    db.add(db_item)
    db.flush()
    return db_item


def get_one(db: Session, chat_id: int) -> ChatORM:
    db_item = db.query(ChatORM).filter(ChatORM.id==chat_id).first()
    if not db_item:
        raise CustomException(http_code=404, message="chat not found")
    return db_item

def get_many(db: Session, chat_id: int) -> ChatORM:
    db_item = db.query(ChatORM).filter(ChatORM.id==chat_id).first()
    if not db_item:
        raise CustomException(http_code=404, message="chat not found")
    return db_item

