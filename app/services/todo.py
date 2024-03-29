from datetime import datetime, timezone, timedelta
from celery import Celery
from app.utils.db import get_db
import app.repositories.todo as TodoRepo
from app.models.todo import Todo, Job
from app.utils.config import configurations as conf

celery = Celery(conf.CELERY_TASK_NAME, broker=conf.CELERY_BROKER)


def get_all_todos_and_trigger():

    with get_db() as db:
        db_todos = TodoRepo.get_need_run(db=db)
        for db_todo in db_todos:
            todo = Todo.from_orm(db_todo)

            if todo.scheduled:
                if todo.scheduled_at < (datetime.now(timezone.utc) - timedelta(seconds=10)).replace(tzinfo=None):
                    # if scheduled 10s ago, still not processed
                    # we can mark it failed
                    todo.scheduled = False
                    todo.scheduled_at = datetime.now(timezone.utc)
            else:
                db_todo.scheduled = True
                celery.send_task(
                    name=f"{conf.CELERY_TASK_NAME}.do_it",
                    kwargs=todo.job.dict(),
                    queue=conf.CELERY_QUEUE,
                )


def finished_a_task(task_id: str):
    with get_db() as db:
        TodoRepo.delete_one(db=db, task_id=task_id)
