from pydantic import BaseSettings


class Settings(BaseSettings):
    RMQ_CONN_URL: str = "amqp://rabbitmq:5672"
    MQ_EXCHANGE: str = "chat_exchange"


configurations = Settings()


if __name__ == "__main__":
    print(configurations)
