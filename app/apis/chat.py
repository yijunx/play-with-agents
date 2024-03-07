# -------------------------------------------------------------------------------------------------------------
# Copyright (c) UCARE.AI Pte Ltd. All rights reserved.
# -------------------------------------------------------------------------------------------------------------
from logging import getLogger

from flask import Blueprint, request
from werkzeug import Request
from flask_pydantic import validate
import app.services.chat as ChatService
from app.models.message import MessageCreate
import jwt
from app.models.exceptions import CustomException
import re
from app.models.user import User

logger = getLogger(__name__)

bp = Blueprint("chat_bp", __name__)


def get_actor_from_request(request: Request) -> User:
    try:
        authorization = request.headers["authorization"]
    except KeyError:
        logger.warning("no athorization header provided from internal request")
        raise
    m = re.match(r"bearer (.+)", authorization, re.IGNORECASE)
    if m is None:
        logger.warning("invalid authorization type")
        raise
    token = m.group(1)
    payload = jwt.decode(token, options={"verify_signature": False})
    try:
        actor = User(**payload)
    except Exception:
        logger.warning("failed to create actor from internal token")
        raise
    return actor


@bp.route("/multi-agent-chat/chat", methods=["POST"])
@validate()
def start_chat(body: MessageCreate):
    try:
        user = get_actor_from_request(request=request)
        r = ChatService.user_start_chat(user=user, message_create=body)
        return r.dict()
    except CustomException as e:
        return {"message": e.message}, e.http_code


@bp.route("/multi-agent-chat/chat/<int:chat_id>", methods=["POST"])
@validate()
def continue_chat(body: MessageCreate, chat_id:int):
    try:
        user = get_actor_from_request(request=request)
        r = ChatService.user_post_chat(user=user, chat_id=chat_id,message_create=body)
        return r.dict()
    except CustomException as e:
        return {"message": e.message}, e.http_code


@bp.route("/multi-agent-chat/chat/<int:chat_id>", methods=["DELETE"])
def close_chat(chat_id:int):
    try:
        user = get_actor_from_request(request=request)
        _ = ChatService.user_close_chat(user=user, chat_id=chat_id)
    except CustomException as e:
        return {"message": e.message}, e.http_code
    

