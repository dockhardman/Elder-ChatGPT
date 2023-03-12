from typing import Text, TypedDict


class Message(TypedDict):
    role: Text  # user, assistant
    content: Text
