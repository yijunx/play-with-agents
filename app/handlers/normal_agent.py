from app.handlers.base import AgentHandler
from app.models.agent import Agent
from app.models.todo import Job
from app.models.message import MessageForOpenai, RoleEnum


import app.services.answer_question as QuestionAnswerService
from app.utils.prompt import get_system_message_from_agent


class NormalHandler(AgentHandler):
    def __init__(self, job: Job) -> None:
        self.agent = job.agent
        self.messages = job.messages
        self.messages.append(
            MessageForOpenai(
                role=RoleEnum.system,
                content=get_system_message_from_agent(a=self.agent),
            )
        )
        self.user_id = job.user_id
        self.chat_id = job.chat_id

    def handle_conversation(self):

        # add system message

        full_reply = QuestionAnswerService.reply_with_stream(
            messages=self.messages, user_id=self.user_id
        )
        print(f"full reply from {self.agent.occupation}:")
        print(full_reply)

        # same full reply to db

        # need to save like something below
        # so that it is like a forum!!
        # {“role”:“user”,“content”:“%USERNAME said %COMMAND%”}]}
        # {“role”:“user”,“content”:“John Doe said hows it going fam”}]}
