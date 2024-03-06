from celery import Celery
from uuid import uuid4

from app.models.message import Message
from app.models.agent import Agent
from app.models.metadata import MetaData


# imaging this file is the todo scanner!!!!,
#  scan the thing every 2s for example!
def start_conversation(
    messages: list[Message], agents: list[Agent], metadata: MetaData
):
    """
    well we will need the meta data like user id, but thats later
    """
    app = Celery("tasks", broker="amqp://rabbitmq:5672")
    task_id = str(uuid4())
    for agent in agents:
        app.send_task(
            name="agents-llm.do_it",
            task_id=task_id,
            kwargs={
                "messages": [m.dict() for m in messages],
                "agent": agent.dict(),
                "metadata": metadata.dict(),
            },
            queue="my-celery-queue",
        )


if __name__ == "__main__":
    start_conversation(
        messages=[Message(role="user", content="How to be happy?")],
        metadata=MetaData(user_id="xxxx", chat_id="yyyy"),
        agents=[
            Agent(who="a professor", temper="mild", impersonnate_who="Richard Feynman"),
            Agent(
                who="an entrepreneur",
                temper="short tempered",
                impersonnate_who="Elon Musk",
            ),
            Agent(
                who="a monk living in the mountains",
                temper="mild",
                impersonnate_who="buddha",
            ),
        ],
    )
