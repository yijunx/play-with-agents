from app.models.agent import Agent


def get_system_message_from_agent(a: Agent) -> str:
    res = f"You are {a.name}, a {a.occupation}"
    if a.impersonate_who:
        res += f"talking like {a.impersonate_who}"
    res += ". Please continue the conversation and reply in one or two sentences. You may raise questions."

    return res
