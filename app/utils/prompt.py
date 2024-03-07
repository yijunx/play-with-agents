from app.models.agent import Agent


def get_system_message_from_agent(a: Agent) -> str:
    res = f"You are a {a.occupation}. "
    if a.impersonate_who:
        res += f"please reply like {a.impersonate_who} may say. But do not mention {a.impersonate_who}."
    # res += f"with a {a.temper} temper."

    return res
