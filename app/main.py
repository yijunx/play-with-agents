from celery import Celery, Task
from celery.worker.request import Request
from logging import getLogger


app = Celery("tasks3", broker="amqp://rabbitmq:5672")
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
        """triggered when get killed, to handle the signal 9"""
        super().on_failure(
            exc_info, send_failed_event=send_failed_event, return_ok=return_ok
        )
        info = self.info()["kwargs"]
        logger.warning(f"##### task {info} ###### \n failed with exc info {exc_info}")


class MyTask(Task):
    Request = MyRequest  # you can use a FQN 'my.package:MyRequest'



class RelatedServiceReturn500(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class CannotEstablishConn(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


@app.task(
    base=MyTask, 
    autoretry_for=(RelatedServiceReturn500,), 
    retry_backoff=True, 
    retry_kwargs={'max_retries': 5}
)
def do_it(**kwargs):
    # this mockserivce has 50% changce to return 500
    ...

if __name__ == "__main__":
    app.worker_main(argv=["worker", "--loglevel=info", "--queues", "my-celery-queue2"])
