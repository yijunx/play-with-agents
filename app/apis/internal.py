# -------------------------------------------------------------------------------------------------------------
# Copyright (c) UCARE.AI Pte Ltd. All rights reserved.
# -------------------------------------------------------------------------------------------------------------
from logging import getLogger

from flask import Blueprint
from flask_pydantic import validate
import app.services.todo as TodoService
import app.services.chat as ChatService
from app.models.message import AgentMessageCreate

logger = getLogger(__name__)

bp = Blueprint("internal_bp", __name__)


@bp.route("/internal/liveness", methods=["GET"])
def scan_todo():
    """yes, this is the liveness probe also!!"""
    TodoService.get_all_todos_and_trigger()
    return {"hello": "i am alive"}


@bp.route("/internal/agent-chat-task/tasks/<task_id>", methods=["POST"])
@validate()
def agent_post_chat(task_id: str, body: AgentMessageCreate):
    ChatService.agent_post_chat(message_create_from_agent=body, task_id=task_id)
    return {"hello": "i am alive"}
