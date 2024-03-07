from celery import Celery
from uuid import uuid4

from app.models.message import MessageCreate
import app.services.chat as ChatService
from app.models.user import User
import uuid


def start_conversation():
    """
    well we will need the meta data like user id, but thats later
    """
    user = User(name="Charcole Llang", id=str(uuid.uuid4()))
    ChatService.user_start_chat(
        user=user,
        message_create=MessageCreate(
            actual_content="I feel depressed. My day jobs are too tiring, should I apply for a new job?"
        ),
    )


if __name__ == "__main__":
    start_conversation()
