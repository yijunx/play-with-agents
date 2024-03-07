from app.models.agent import Agent


def get_system_message_from_agent(a: Agent) -> str:
    res = f"You are {a.name}, a {a.occupation}. "
    if a.impersonate_who:
        res += f"please continue the conversation like {a.impersonate_who} may say. But do not mention {a.impersonate_who}."
    res += "Keep the reply in one paragraph and take ideas from others in the chat."

    return res
