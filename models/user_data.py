from dataclasses import dataclass


@dataclass
class UserData:
    name: str
    mana: int
    elixir: int
    trovo_id: int
    twitch_id: int

    @staticmethod
    def from_dict(obj: dict) -> 'UserData':
        _name = str(obj.get('name'))
        _mana = int(obj.get('mana', 0))
        _elixir = int(obj.get('elixir', 0))
        _trovo_id = int(obj.get('trovo_id', -1))
        _twitch_id = int(obj.get('twitch_id', -1))
        return UserData(_name, _mana, _elixir, _trovo_id, _twitch_id)

    def __dict__(self):
        return {
            'name': self.name,
            'mana': self.mana,
            'elixir': self.elixir,
            'trovo_id': self.trovo_id,
            'twitch_id': self.twitch_id
        }
