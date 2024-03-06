# play-with-agents
play with llm agents

# to setup

* Copy the `config/dev.env.template` to `config/dev.env`, and key in your credentials.
* reopen in devcontainer
* start the poetry shell by `poetry shell`
* to start the agents `python app/main.py`
* to ask question to agents:
    * edit `trigger_celery.py` at the parts under `if __name__ == "__main__"` 
    * then open another terminal, run `poetry shell`, then run `python trigger_celery.py`. When this script is run, all agents will hear what you ask at the same time, then answer in the log of the terminal of `python app/main.py`.
