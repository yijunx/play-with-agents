from celery import Celery
from uuid import uuid4

from app.models.message import MessageForOpenai, MessageCreate
from app.models.agent import Agent
import app.services.todo as TodoService
from app.models.user import User
import uuid


def trigger_todo():
    """
    well we will need the meta data like user id, but thats later
    """
    TodoService.get_all_todos_and_trigger()


if __name__ == "__main__":
    trigger_todo()
