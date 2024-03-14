import pika
from openai import AzureOpenAI
from app.utils.config import configurations
from logging import getLogger
from app.models.message import MessageForOpenai, AgentMessageCreate, MessageForFrontend
import json
from uuid import uuid4
from app.models.agent import Agent
from datetime import datetime, timezone

logger = getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def label_chunk_message(chunk_message: str, message_id: str, keep_listening: True) -> str:
    return json.dumps(
        {"id": message_id, "content": chunk_message, "keep_listening": keep_listening}
    )


def reply_with_stream(user_id: str, messages: list[MessageForOpenai], chat_id: str, agent: Agent) -> tuple[str, str]:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    channel.exchange_declare(exchange=configurations.MQ_EXCHANGE, exchange_type="direct")

    client = AzureOpenAI(
        api_key=configurations.OPENAI_API_KEY,
        api_version=configurations.OPENAI_API_VERSION,
        azure_endpoint=configurations.AZURE_OPENAI_ENDPOINT,
    )

    deployment_name = configurations.OPENAI_ENGINE

    # Send a completion call to generate an answer
    # start_time = time.time()
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[m.dict() for m in messages],
        stream=True,
    )
    # response = client.completions.create(model=deployment_name, prompt=start_phrase, max_tokens=10) #, stream=True)
    collected_chunks = []
    collected_messages = []
    full_answer = ""

    # send a starting message for frontend to get ready!!!
    message_id = str(uuid4())

    empty_message = MessageForFrontend(
        id=message_id,
        created_by=agent.id,
        created_by_name=agent.name,
        created_at=datetime.now(timezone.utc),
        actual_content="",
        chat_id=chat_id
    )
    channel.basic_publish(
        exchange="direct_logs",
        routing_key=user_id,
        body = json.dumps(empty_message.dict(), cls=CustomJSONEncoder)
    )

    for chunk in response:
        # chunk_time = time.time() - start_time  # calculate the time delay of the chunk
        collected_chunks.append(chunk)  # save the event response
        chunk_message = chunk.choices[0].delta.content  # extract the message
        collected_messages.append(chunk_message)  # save the message

        if chunk_message:
            channel.basic_publish(
                exchange="direct_logs", routing_key=user_id, body=label_chunk_message(
                    chunk_message=chunk_message, message_id=message_id
                )
            )
            full_answer += chunk_message

    channel.basic_publish(
        exchange="direct_logs", routing_key=user_id, body=label_chunk_message(
            chunk_message="", message_id=message_id, keep_listening=False
        )
    )
    channel.close()
    connection.close()
    return full_answer, message_id
