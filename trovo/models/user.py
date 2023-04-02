from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    mana = 0
    elixir = 0

    @staticmethod
    def from_dict(obj: dict) -> 'User':
        _id = int(obj.get('id'))
        _name = str(obj.get('name'))
        _mana = int(obj.get('mana', 0))
        _elixir = int(obj.get('elixir', 0))
        user = User(_id, _name)
        user.mana = _mana
        user.elixir = _elixir
        return user

    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name,
            'mana': self.mana,
            'elixir': self.elixir
        }
