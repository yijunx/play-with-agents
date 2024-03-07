# used for celery worker
import pika
from openai import AzureOpenAI
from app.utils.config import configurations
from logging import getLogger
import time
from app.models.message import MessageForOpenai

logger = getLogger(__name__)


def reply_with_stream(user_id: str, messages: list[MessageForOpenai]) -> str:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    channel.exchange_declare(exchange="direct_logs", exchange_type="direct")

    client = AzureOpenAI(
        api_key=configurations.OPENAI_API_KEY,
        api_version=configurations.OPENAI_API_VERSION,
        azure_endpoint=configurations.AZURE_OPENAI_ENDPOINT,
    )

    deployment_name = configurations.OPENAI_ENGINE

    # Send a completion call to generate an answer
    start_time = time.time()
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[m.dict() for m in messages],
        stream=True,
    )
    # response = client.completions.create(model=deployment_name, prompt=start_phrase, max_tokens=10) #, stream=True)
    collected_chunks = []
    collected_messages = []
    full_answer = ""

    for chunk in response:
        chunk_time = time.time() - start_time  # calculate the time delay of the chunk
        collected_chunks.append(chunk)  # save the event response
        chunk_message = chunk.choices[0].delta.content  # extract the message
        collected_messages.append(chunk_message)  # save the message
        # print(
        #     f"Message received {chunk_time:.2f} seconds after request: {chunk_message}"
        # )
        if chunk_message:
            channel.basic_publish(
                exchange="direct_logs", routing_key=user_id, body=chunk_message
            )
            full_answer += chunk_message

    # print(full_answer)
    # channel.close()
    # connection.close()
    return full_answer
