from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    AZURE_OPENAI_ENDPOINT: str
    OPENAI_API_VERSION: str
    OPENAI_API_KEY: str
    OPENAI_ENGINE: str

    CELERY_BROKER: str
    CELERY_WORKER_MAX: int
    CELERY_QUEUE: str
    CELERY_TASK_NAME: str

    MQ_EXCHANGE: str = "chat_exchange"
    # RMQ_CONN_URL: str = "amqp://rabbitmq:5672"

    MAX_MESSAGES_FROM_AGENTS_FOR_ONE_TRIGGER: int
    DATABASE_URI: str

    AGENT_INTERNAL_POST_URL: str


class ProductionConfig(Settings):
    # it means that, every entry for Settings must
    # come from environment variables
    pass


class DevelopmentConfig(Settings):
    class Config:
        env_file = "config/dev.env"


def find_which_config():
    if os.getenv("ENV"):  # there is DOMAIN name provided
        config = ProductionConfig()
    else:
        config = DevelopmentConfig()

    def func() -> Settings:
        return config

    return func()


configurations = find_which_config()

if __name__ == "__main__":
    print(configurations)
