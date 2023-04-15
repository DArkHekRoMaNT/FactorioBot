from dataclasses import dataclass

from .user_data import UserData


@dataclass
class ChatMessage:
    text: str
    sender: UserData
    roles: list[str]

    @staticmethod
    def from_dict(obj: dict) -> 'ChatMessage':
        _text = str(obj.get('text'))
        _sender = UserData.from_dict(obj.get('sender'))
        _roles = list(obj.get('roles', []))
        return ChatMessage(_text, _sender, _roles)

    def __dict__(self):
        return {
            'text': self.text,
            'sender': self.sender,
            'roles': self.roles
        }
