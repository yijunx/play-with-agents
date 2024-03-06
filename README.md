# play-with-agents
play with llm agents

# to setup

* Copy the `config/dev.env.template` to `config/dev.env`, and key in your credentials.
* reopen in devcontainer
* start the poetry shell by `poetry shell`
* to start the agents `python app/main.py`
* to ask sample questions, please edit `trigger_celery.py` at the parts under `if __name__ == "__main__"` then run `python trigger_celery.py`
