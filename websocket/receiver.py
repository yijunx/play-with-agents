import pika
from websocket.config import configurations as config
from logging import getLogger


logger = getLogger(__name__)


class Receiver:
    """
    This class is used to receive messages from RabbitMQ
    param:
        conn_url: RabbitMQ connection url in the format of "amqp://username:password@host:port/vhost"
        exchange: RabbitMQ exchange.
        routing_key: RabbitMQ routing key. user_id is used as routing key
    """

    def __init__(
        self,
        routing_key,
        conn_url=config.RMQ_CONN_URL,
        exchange=config.MQ_EXCHANGE,
    ):
        self.conn_url = conn_url
        self.exchange = exchange
        self.routing_key = routing_key

        logger.info(
            f"Connecting to RabbitMQ at{self.conn_url},{self.exchange},{self.routing_key}"
        )
        self.connection = pika.BlockingConnection(
            pika.connection.URLParameters(self.conn_url)
        )
        logger.info(f"Connected to RabbitMQ")

        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue="", exclusive=True, auto_delete=True)
        self.channel.exchange_declare(exchange=self.exchange, exchange_type="direct")
        self.queue_name = result.method.queue
        self.channel.queue_bind(
            exchange=self.exchange, queue=self.queue_name, routing_key=self.routing_key
        )

        self.my_daemon = None

    def start(self, callback):
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=callback, auto_ack=True
        )
        try:
            self.channel.start_consuming()
        except Exception as e:
            logger.info(e)
            self.terminate()

    def terminate(self):
        self.channel.stop_consuming()
        self.channel.queue_unbind(
            exchange=self.exchange, queue=self.queue_name, routing_key=self.routing_key
        )
        self.channel.queue_delete(queue=self.queue_name)
        try:
            self.connection.close()
            logger.info(f"Session ended. Queue for {self.routing_key} is cleared")
        except Exception as e:
            logger.error(f"Connection close error: {e}")


if __name__ == "__main__":
    import json
    r = Receiver(routing_key="user-id")
    def callback(ch, method, properties, body):
        print(body.decode("utf-8"))
        # try json..
    r.start(callback=callback)