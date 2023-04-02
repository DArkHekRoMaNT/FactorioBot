import enum
from dataclasses import dataclass


class ChatServiceMessageType(enum.StrEnum):
    AUTH = "AUTH"
    RESPONSE = "RESPONSE"
    PING = "PING"
    PONG = "PONG"
    CHAT = "CHAT"


@dataclass
class ChatServiceMessage:
    type: ChatServiceMessageType
    nonce: str
    error: str
    data: {}

    @staticmethod
    def from_dict(obj: dict) -> 'ChatServiceMessage':
        _type = ChatServiceMessageType(obj.get('type'))
        _nonce = str(obj.get('nonce', ''))
        _error = str(obj.get('error', None))
        _data = dict(obj.get('data', {}))

        return ChatServiceMessage(_type, _nonce, _error, _data)
