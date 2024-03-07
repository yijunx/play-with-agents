from app.utils.db import get_db
from app.models.user import User
import app.repositories.chat as ChatRepo
import app.repositories.agent as AgentRepo
import app.repositories.message as MessageRepo
import app.repositories.todo as TodoRepo

from app.models.todo import Job, Todo
from app.models.chat import Chat
from app.models.agent import Agent
from app.models.message import (
    MessageCreate,
    AgentMessageCreate,
    MessageForOpenai,
    MessageForFrontend,
)
from app.utils.config import configurations
from app.models.exceptions import CustomException


AGENTS = [
    Agent(
        name="Prof. Boffin",
        occupation="a professor",
        temper="mild",
        impersonate_who="Richard Feynman",
        remaining_replies_count=configurations.MAX_MESSAGES_FROM_AGENTS_FOR_ONE_TRIGGER,
    ),
    Agent(
        name="George Michael",
        occupation="an entrepreneur",
        temper="short tempered",
        impersonate_who="Elon Musk",
        remaining_replies_count=configurations.MAX_MESSAGES_FROM_AGENTS_FOR_ONE_TRIGGER,
    ),
    Agent(
        name="Hui Neng",
        occupation="a monk living in the mountains",
        temper="mild",
        impersonate_who="buddha",
        remaining_replies_count=configurations.MAX_MESSAGES_FROM_AGENTS_FOR_ONE_TRIGGER,
    ),
]


def user_start_chat(user: User, message_create: MessageCreate) -> Chat:
    with get_db() as db:
        # create the repo
        db_chat = ChatRepo.create(db=db, user_id=user.id)
        chat = Chat.from_orm(db_chat)
        # create the agents
        # later we need to find agents to create but now lets just hard code

        # create the first message
        db_message = MessageRepo.create_message_from_user(
            db=db, chat_id=db_chat.id, message_create=message_create, user=user
        )
        # message_for_frontend = MessageForFrontend.from_orm(db_message)
        messages_for_openai = [MessageForOpenai.from_orm(db_message)]

        # each agent now has a job!
        for agent in AGENTS:
            db_agent = AgentRepo.create(db=db, chat_id=db_chat.id, agent=agent)
            job = Job(
                messages=messages_for_openai,
                agent=Agent.from_orm(db_agent),
                user_id=user.id,
                chat_id=chat.id,
            )
            TodoRepo.create(db=db, job=job)
    return chat


def user_post_chat(
    user: User, chat_id: int, message_create: MessageCreate
) -> MessageForFrontend:
    with get_db() as db:
        db_chat = ChatRepo.get_one(db=db, chat_id=chat_id)

        if db_chat.ended:
            raise CustomException(http_code=400, message="This chat is closed")
        if db_chat.user_id != user.id:
            raise CustomException(http_code=403, message="well it is your chat..")

        current_messages = MessageRepo.get_many(db=db, chat_id=chat_id)

        messages_for_openai = [MessageForOpenai.from_orm(x) for x in current_messages]
        db_message = MessageRepo.create_message_from_user(
            db=db, chat_id=chat_id, message_create=message_create, user=user
        )
        message_for_frontend = MessageForFrontend.from_orm(db_message)
        messages_for_openai.append(MessageForOpenai.from_orm(db_message))
        db_agents = AgentRepo.get_many(db=db, chat_id=chat_id)

        # charge the dbagent
        for db_agent in db_agents:
            db_agent.remaining_replies_count = (
                configurations.MAX_MESSAGES_FROM_AGENTS_FOR_ONE_TRIGGER
            )
            agent = Agent.from_orm(db_agent)
            job = Job(
                messages=messages_for_openai,
                agent=agent,
                user_id=user.id,
                chat_id=chat_id,
            )
            TodoRepo.create(db=db, job=job)
    return message_for_frontend


def agent_post_chat(message_create_from_agent: AgentMessageCreate, task_id: str):
    with get_db() as db:
        db_chat = ChatRepo.get_one(db=db, chat_id=message_create_from_agent.chat_id)
        if db_chat.ended:
            raise CustomException(http_code=400, message="This chat is closed")
        chat = Chat.from_orm(db_chat)

        current_messages = MessageRepo.get_many(db=db, chat_id=chat.id)
        messages_for_openai = [MessageForOpenai.from_orm(x) for x in current_messages]
        db_message = MessageRepo.create_message_from_agent(
            db=db, message_create_from_agent=message_create_from_agent
        )
        messages_for_openai.append(MessageForOpenai.from_orm(db_message))
        db_agents = AgentRepo.get_many(db=db, chat_id=chat.id)

        this_agent = AgentRepo.get_one(
            db=db, agent_id=message_create_from_agent.agent_id
        )
        this_agent.remaining_replies_count -= 1

        for db_agent in db_agents:
            agent = Agent.from_orm(db_agent)
            if (
                agent.remaining_replies_count > 0
                and agent.id != message_create_from_agent.agent_id
            ):
                job = Job(
                    messages=messages_for_openai,
                    agent=agent,
                    user_id=chat.user_id,
                    chat_id=message_create_from_agent.chat_id,
                )
                TodoRepo.create(db=db, job=job)

        TodoRepo.delete_one(db=db, task_id=task_id)


def user_close_chat(user: User, chat_id: int):
    with get_db() as db:
        db_chat = ChatRepo.get_one(db=db, chat_id=chat_id)
        if db_chat.user_id != user.id:
            raise CustomException(http_code=403, message="well it is your chat..")
        ChatRepo.close_one(db=db, chat_id=chat_id)
        TodoRepo.delete_for_a_chat(db=db, chat_id=chat_id)


def user_get_messages(chat_id: int) -> list[MessageForFrontend]:
    with get_db() as db:
        db_messages = MessageRepo.get_many(db=db, chat_id=chat_id)
        messages = [MessageForFrontend.from_orm(x) for x in db_messages]
    return messages


def user_get_internal_messages(chat_id: int) -> list[MessageForOpenai]:
    with get_db() as db:
        db_messages = MessageRepo.get_many(db=db, chat_id=chat_id)
        messages = [MessageForOpenai.from_orm(x) for x in db_messages]
    return messages
