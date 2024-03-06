# ------------------------------------------------------------------------------------------------------------
# Copyright (c) UCARE.AI Pte Ltd. All rights reserved.
# ------------------------------------------------------------------------------------------------------------
from abc import ABC, abstractclassmethod


class AgentHandler(ABC):
    """the concrete event handler will inherit from here"""

    @abstractclassmethod
    def handle_conversation(self): ...
