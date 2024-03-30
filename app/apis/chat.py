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
        logger.warning("no athorization header")
        raise CustomException(http_code=401, message="auth failed")
    m = re.match(r"bearer (.+)", authorization, re.IGNORECASE)
    if m is None:
        logger.warning("invalid authorization type")
        raise CustomException(http_code=401, message="auth failed")
    token = m.group(1)
    payload = jwt.decode(token, options={"verify_signature": False})
    print(payload)
    try:
        actor = User(
            name=payload["name"],
            id=payload["sub"]
        )
    except Exception:
        logger.warning("failed to create actor from internal token")
        raise CustomException(http_code=401, message="auth failed")
    return actor


@bp.route("/multi-agent-chat/chats", methods=["POST"])
@validate()
def start_chat(body: MessageCreate):
    try:
        user = get_actor_from_request(request=request)
        r = ChatService.user_start_chat(user=user, message_create=body)
        return r.dict()
    except CustomException as e:
        return {"message": e.message}, e.http_code


@bp.route("/multi-agent-chat/chats/<chat_id>", methods=["POST"])
@validate()
def continue_chat(body: MessageCreate, chat_id: str):
    try:
        user = get_actor_from_request(request=request)
        r = ChatService.user_post_chat(user=user, chat_id=chat_id, message_create=body)
        return r.dict()
    except CustomException as e:
        return {"message": e.message}, e.http_code


@bp.route("/multi-agent-chat/chats/<chat_id>/messages", methods=["GET"])
def get_chat_messages(chat_id: str):
    try:
        r = ChatService.user_get_messages(chat_id=chat_id)
        print(f"we have {len(r)} messages..")
        return [x.dict() for x in r]
    except CustomException as e:
        return {"message": e.message}, e.http_code


@bp.route("/multi-agent-chat/chats/<chat_id>/internal-messages", methods=["GET"])
def get_chat_interal_messages(chat_id: str):
    try:
        r = ChatService.user_get_internal_messages(chat_id=chat_id)
        print(f"we have {len(r)} messages..")
        return [x.dict() for x in r]
    except CustomException as e:
        return {"message": e.message}, e.http_code


@bp.route("/multi-agent-chat/chats/<chat_id>", methods=["DELETE"])
def close_chat(chat_id: str):
    try:
        user = get_actor_from_request(request=request)
        _ = ChatService.user_close_chat(user=user, chat_id=chat_id)
        return "closed"
    except CustomException as e:
        return {"message": e.message}, e.http_code
