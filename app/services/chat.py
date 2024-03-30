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
import random


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


def user_start_chat(user: User, message_create: MessageCreate) -> MessageForFrontend:
    with get_db() as db:
        # create the repo
        db_chat = ChatRepo.create(db=db, user_id=user.id)
        chat = Chat.from_orm(db_chat)

        db_message = MessageRepo.create_message_from_user(
            db=db, chat_id=db_chat.id, message_create=message_create, user=user
        )
        message_for_frontend = MessageForFrontend.from_orm(db_message)
        messages_for_openai = [MessageForOpenai.from_orm(db_message)]

        # we also needs to randomly choose 1 to answer for the first time
        # later we need to find agents to create but now lets just hard code
        lucky_number = random.randint(1, len(AGENTS))
        lucky_agent = None
        rounds = 1
        for agent in AGENTS:
            db_agent = AgentRepo.create(db=db, chat_id=db_chat.id, agent=agent)
            if rounds == lucky_number:
                db_agent.remaining_replies_count -= 1
                lucky_agent = Agent.from_orm(db_agent)
            rounds += 1

        # the lucky agent gets the job
        job = Job(
            messages=messages_for_openai,
            agent=lucky_agent,
            user_id=user.id,
            chat_id=chat.id,
        )
        TodoRepo.create(db=db, job=job)
    return message_for_frontend


def user_post_chat(
    user: User, chat_id: int, message_create: MessageCreate
) -> MessageForFrontend:
    with get_db() as db:
        db_chat = ChatRepo.get_one(db=db, chat_id=chat_id)

        # check if still can chat
        if db_chat.ended:
            raise CustomException(http_code=400, message="This chat is closed")
        if db_chat.user_id != user.id:
            raise CustomException(http_code=403, message="well it is your chat..")
        # get current messages
        current_messages = MessageRepo.get_many(db=db, chat_id=chat_id)
        messages_for_openai = [MessageForOpenai.from_orm(x) for x in current_messages]

        # create this message
        db_message = MessageRepo.create_message_from_user(
            db=db, chat_id=chat_id, message_create=message_create, user=user
        )
        message_for_frontend = MessageForFrontend.from_orm(db_message)

        # adds to messages for openai for the job
        messages_for_openai.append(MessageForOpenai.from_orm(db_message))

        # remove all the current todo
        TodoRepo.delete_many(db=db, chat_id=chat_id)

        # charge the db agent
        db_agents = AgentRepo.get_many(db=db, chat_id=chat_id)
        lucky_number = random.randint(1, len(AGENTS))
        lucky_agent = None
        rounds = 1
        for db_agent in db_agents:
            db_agent.remaining_replies_count = (
                configurations.MAX_MESSAGES_FROM_AGENTS_FOR_ONE_TRIGGER
            )
            if rounds == lucky_number:
                db_agent.remaining_replies_count -= 1
                lucky_agent = Agent.from_orm(db_agent)
            rounds += 1

        job = Job(
            messages=messages_for_openai,
            agent=lucky_agent,
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

        db_agents = AgentRepo.get_many(db=db, chat_id=chat.id, can_still_talk=True)
        agents = [
            Agent.from_orm(x)
            for x in db_agents
            if x.id != message_create_from_agent.agent_id
        ]
        if len(agents) == 0:
            TodoRepo.delete_one(db=db, task_id=task_id)
            return

        # choose a agent which has most remaining response count..
        lucky_agent = sorted(
            agents, key=lambda x: x.remaining_replies_count, reverse=True
        )[0]
        # lucky_agent = random.choice(agents)
        for db_agent in db_agents:
            if db_agent.id != lucky_agent.id:
                continue
            # it is all lucky agent...
            db_agent.remaining_replies_count -= 1
            job = Job(
                messages=messages_for_openai,
                agent=lucky_agent,
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
