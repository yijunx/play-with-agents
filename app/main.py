from celery import Celery, Task
from celery.worker.request import Request
from logging import getLogger
from app.models.exceptions import Retry
from app.models.agent import Agent
from app.models.metadata import MetaData

from app.handlers.normal_agent import NormalHandler


app = Celery("agents-llm", broker="amqp://rabbitmq:5672")
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
    messages: list[dict] = kwargs.get("messages")
    agent: Agent = Agent(**kwargs.get("agent"))
    metadata: MetaData = MetaData(**kwargs.get("metadata"))

    print(messages)
    print(agent)
    print(metadata)

    h = NormalHandler(messages=messages, agent=agent, metadata=metadata)
    h.handle_conversation()


if __name__ == "__main__":
    app.worker_main(argv=["worker", "--loglevel=info", "--queues", "my-celery-queue"])
