from dataclasses import dataclass


@dataclass
class Account:
    name: str
    avatar_url: str


@dataclass
class TrovoAccount(Account):
    access_token: str = None
    refresh_token: str = None
