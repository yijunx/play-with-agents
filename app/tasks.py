from celery import Celery, Task
from celery.worker.request import Request
from logging import getLogger
from app.models.exceptions import Retry

from app.handlers.normal_agent import NormalHandler
from app.utils.config import configurations
from app.models.todo import Job


app = Celery(configurations.CELERY_TASK_NAME, broker=configurations.CELERY_BROKER)
logger = getLogger(__name__)


class MyRequest(Request):
    "A minimal custom request to log failures and hard time limits."

    def on_timeout(self, soft, timeout):
        super(MyRequest, self).on_timeout(soft, timeout)
        if not soft:
            hard_time_msg = f"A hard timeout was enforced for task {self.task.name}"
            logger.warning(hard_time_msg)
            info = self.info()["kwargs"]

    def on_failure(self, exc_info, send_failed_event=True, return_ok=False):
        """triggered when get killed, to handle the signal 9
        or raised custom errors"""
        super().on_failure(
            exc_info, send_failed_event=send_failed_event, return_ok=return_ok
        )
        info = self.info()["kwargs"]
        logger.warning(f"##### task {info} ###### \n failed with exc info {exc_info}")


class MyTask(Task):
    Request = MyRequest


@app.task(
    base=MyTask,
    autoretry_for=(Retry,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def do_it(**kwargs):
    # this mockserivce has 50% changce to return 500
    # what kind of the job is sent here
    job = Job(**kwargs)

    print(job)

    h = NormalHandler(job=job)
    h.handle_conversation()


if __name__ == "__main__":
    app.worker_main(
        argv=[
            "worker",
            f"--autoscale={configurations.CELERY_WORKER_MAX},{1}",
            "--loglevel=info",
            "--queues",
            configurations.CELERY_QUEUE,
        ]
    )
