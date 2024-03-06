from app.handlers.base import AgentHandler
from app.models.agent import Agent
from app.models.metadata import MetaData
from app.models.message import Message, RoleEnum

import app.services.answer_question as QuestionAnswerService
from app.utils.prompt import get_system_message_from_agent


class NormalHandler(AgentHandler):
    def __init__(self, messages: list[dict], agent: Agent, metadata: MetaData) -> None:
        self.agent = agent
        self.messages = messages
        self.messages.append(
            Message(
                role=RoleEnum.system,
                content=get_system_message_from_agent(a=self.agent),
            )
        )
        self.metadata = metadata

    def handle_conversation(self):

        # add system message

        full_reply = QuestionAnswerService.reply_with_stream(
            messages=self.messages, user_id=self.metadata.user_id
        )
        print("full reply:")
        print(full_reply)

        # same full reply to db

        # need to save like something below
        # so that it is like a forum!!
        # {“role”:“user”,“content”:“%USERNAME said %COMMAND%”}]}
        # {“role”:“user”,“content”:“John Doe said hows it going fam”}]}
