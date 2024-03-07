from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.sqlalchemy.todo import TodoORM, FinishedTodoORM

from app.models.exceptions import CustomException
from app.models.todo import Job
from datetime import datetime, timezone
from uuid import uuid4


def create(db: Session, job: Job, scheduled_at: datetime) -> TodoORM:
    task_id = str(uuid4())
    job.task_id = task_id
    db_item = TodoORM(
        id=task_id,
        created_at=datetime.now(timezone.utc),
        job=job.dict(),
        scheduled_at=scheduled_at
    )
    db.add(db_item)
    db.flush()
    return db_item


def get_one(db: Session, task_id: str) -> TodoORM:
    db_item = db.query(TodoORM).filter(TodoORM.id==task_id).first()
    if not db_item:
        raise CustomException(http_code=404, message="chat not found")
    return db_item


def get_many(db: Session) -> list[TodoORM]:
    return db.query(TodoORM).all()


def delete_one(db: Session, task_id: str) -> None:
    db.query(TodoORM).filter(TodoORM.id==task_id).delete()


