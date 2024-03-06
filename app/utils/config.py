from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    AZURE_OPENAI_ENDPOINT: str
    OPENAI_API_VERSION: str
    OPENAI_API_KEY: str
    OPENAI_ENGINE: str


class ProductionConfig(Settings):
    # it means that, every entry for Settings must
    # come from environment variables
    pass


class DevelopmentConfig(Settings):
    class Config:
        env_file = "./dev.env"


def find_which_config():
    if os.getenv("ENV"):  # there is DOMAIN name provided
        config = ProductionConfig()
    else:
        config = DevelopmentConfig()

    def func() -> Settings:
        return config

    return func()


configurations = find_which_config()
