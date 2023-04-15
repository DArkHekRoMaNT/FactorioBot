from dataclasses import dataclass


@dataclass
class TrovoChatSocketMessage:
    type: str
    nonce: str
    error: str
    data: {}

    @staticmethod
    def from_dict(obj: dict) -> 'TrovoChatSocketMessage':
        _type = str(obj.get('type'))
        _nonce = str(obj.get('nonce', ''))
        _error = str(obj.get('error', None))
        _data = dict(obj.get('data', {}))

        return TrovoChatSocketMessage(_type, _nonce, _error, _data)
