from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.sqlalchemy.todo import TodoORM

from app.models.exceptions import CustomException
from app.models.todo import Job
from datetime import datetime, timezone
from uuid import uuid4


def create(db: Session, job: Job, scheduled_at: datetime = None) -> TodoORM:
    task_id = str(uuid4())
    job.task_id = task_id
    now = datetime.now(timezone.utc)
    if scheduled_at is None:
        scheduled_at = now
    db_item = TodoORM(
        id=task_id,
        created_at=now,
        job=job.dict(),
        chat_id=job.chat_id,
        scheduled_at=scheduled_at,
    )
    db.add(db_item)
    db.flush()
    return db_item


def get_one(db: Session, task_id: str) -> TodoORM:
    db_item = db.query(TodoORM).filter(TodoORM.id == task_id).first()
    if not db_item:
        raise CustomException(http_code=404, message="task not found")
    return db_item


def get_many(db: Session) -> list[TodoORM]:
    return db.query(TodoORM).all()


def get_need_run(db: Session) -> list[TodoORM]:
    return (
        db.query(TodoORM)
        .filter(TodoORM.scheduled_at < datetime.now(timezone.utc))
        .all()
    )


def delete_one(db: Session, task_id: str) -> None:
    db.query(TodoORM).filter(TodoORM.id == task_id).delete()


def delete_for_a_chat(db: Session, chat_id: str) -> None:
    db.query(TodoORM).filter(TodoORM.chat_id == chat_id).delete()
