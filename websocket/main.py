# # # gunicorn -b 0.0.0.0:5000 --workers 4 --threads 100 app.main:app

from flask_sock import Sock
from websocket.receiver import Receiver
from flask import Flask, Request
from flask import request
from logging import getLogger
from pydantic import BaseModel
import re
import jwt


logger = getLogger(__name__)

app = Flask(__name__)
sock = Sock(app)


class User(BaseModel):
    name: str
    id: str


def get_actor_from_request(request: Request) -> User:
    authorization = request.args.get["token"]
    m = re.match(r"bearer (.+)", authorization, re.IGNORECASE)
    token = m.group(1)
    payload = jwt.decode(token, options={"verify_signature": False})
    try:
        actor = User(**payload)
    except Exception:
        logger.warning("failed to create actor from internal token")
    return actor


@app.route("/internal/liveness", methods=["GET"])
def liveness():
    return {"hello": "i am alive"}


@sock.route("/apis/chat")
def connect(ws):
    try:
        actor = get_actor_from_request(request)
        logger.info(f"authenticated user: {actor.name}")
        # delete below line
        ws.send({"message": f"Welcome"})
    except Exception as e:
        logger.error(f"authenticate error {e}")
        ws.send({"message": e})
        return

    def callback(ch, method, properties, body):
        ws.send(body.decode("utf-8"))

    try:
        recv = Receiver(routing_key=actor.id)
    except Exception as e:
        logger.error(f"receiver error {e}")
        ws.send({"error": e})
        return
    logger.info("start receiving")
    recv.start(callback)


if __name__ == "__main__":
    sock.run(app, host="localhost", port=8000, debug=True)
