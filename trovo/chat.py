import asyncio
import json
import logging
import random
import string
from time import time

import websockets

import db
from .api import TrovoApi
from .commands import commands
from .models import ChatMessage, ChatServiceMessage, ChatServiceMessageType, User, ChatMessageType

_log = logging.getLogger(__name__)


class TrovoChat:
    chat_url = 'wss://open-chat.trovo.live/chat'
    request_queue = []
    heartbeat_gap = 30
    ws = None
    active = False
    users = {}
    start_time = 0
    last_pong_time = 0

    def __init__(self, client_id: str, client_secret: str, channel_id: str):
        self.api = TrovoApi(client_id, client_secret)
        self.channel_id = channel_id

    async def run(self):
        self.load()
        if not self.api.auth():
            _log.critical('Auth error')
            return
        self.save()

        self.active = True
        self.start_time = int(time())
        self.ws = await websockets.connect(self.chat_url)
        tasks = [
            asyncio.create_task(self._ping_pong_loop()),
            asyncio.create_task(self._response_loop()),
            asyncio.create_task(self._request_loop())
        ]
        await asyncio.gather(*tasks)

    async def _ping_pong_loop(self):
        _log.info('Ping-pong loop started')
        while self.active:
            await asyncio.sleep(self.heartbeat_gap)
            self.request_queue.append({
                'type': 'PING',
                'nonce': self.get_new_nonce()
            })

    async def _response_loop(self):
        _log.info('Response loop started')
        while self.active:
            try:
                data = await self.ws.recv()
                _log.debug(f'Response: {data}')
                raw_msg = ChatServiceMessage.from_dict(json.loads(data))
                match raw_msg.type:
                    case ChatServiceMessageType.AUTH:
                        self.send_message('Awakening')
                    case ChatServiceMessageType.PONG:
                        self.last_pong_time = time()
                        self.heartbeat_gap = raw_msg.data.get('gap', 30)
                    case ChatServiceMessageType.CHAT:
                        for raw_chat_msg in raw_msg.data.get('chats', []):
                            msg = ChatMessage.from_dict(raw_chat_msg)
                            if msg.send_time >= self.start_time:
                                self.trigger_commands(msg)
                                self.check_donation(msg)
                            else:
                                _log.debug(f'Old message "{msg.content}" ignored')
            except websockets.ConnectionClosedError as e:
                _log.error(f'Response loop connection error, stopped: {e}')
                self.active = False
            except Exception as e:
                _log.error(f'Response loop iteration error "{e.__name__()}": {e}')

    async def _request_loop(self):
        _log.info('Request loop started')
        while self.active:
            if self.last_pong_time + self.heartbeat_gap * 2 < time():
                self.request_queue.append({
                    'type': 'AUTH',
                    'nonce': self.get_new_nonce(),
                    'data': {
                        'token': self.api.get_channel_chat_token(self.channel_id)
                    }
                })
                self.last_pong_time = time()

            if len(self.request_queue) == 0:
                await asyncio.sleep(0.1)
                continue

            msg = self.request_queue.pop(0)
            data = json.dumps(msg)
            _log.debug(f'Request: {data}')
            await self.ws.send(data)

    def trigger_commands(self, msg: ChatMessage):
        for command in commands:
            try:
                command(msg, self)
            except Exception as e:
                _log.warning(f'Trigger command {command.name} by {msg.nick_name} is failed: {e}')

    def check_donation(self, msg: ChatMessage):
        if msg.type == ChatMessageType.SPELLS:
            content = json.loads(msg.content)
            value = content.get('gift_value')
            num = content.get('num')
            user = self.get_user(msg.sender_id, msg.nick_name)
            if content.get('value_type') == 'Mana':
                self.add_mana(user, num * value)
            elif content.get('value_type') == 'Elixir':
                self.add_elixir(user, num * value)

        elif msg.type == ChatMessageType.SUBSCRIPTION_MESSAGE:
            self.add_elixir(self.get_user(msg.sender_id, msg.nick_name), 500)

    def get_user(self, user_id: int, user_name: str) -> User:
        if user_id in self.users:
            user = self.users[user_id]
        else:
            user = User(user_id, user_name)
            self.users[user_id] = user
        return user

    def find_user(self, user_name: str) -> User:
        for user in self.users.values():
            if user.name == user_name:
                return user

        info = self.api.get_users([user_name])
        return self.get_user(int(info['users'][0]['user_id']), user_name)

    def add_mana(self, user: User, number: int):
        user.elixir += number
        self.send_message(f'Add {number} mp to {user.name}')
        _log.info(f'Added {number} elixir points to {user.name}. Total: {user.elixir}')
        self.save()

    def add_elixir(self, user: User, number: int):
        user.mana += number
        self.send_message(f'Add {number} ep to {user.name}')
        _log.info(f'Added {number} mana points to {user.name}. Total: {user.mana}')
        self.save()

    def load(self):
        data = db.load('trovo')
        self.api.access_token = data.get('access_token', self.api.access_token)
        self.api.refresh_token = data.get('refresh_token', self.api.refresh_token)
        self.users = dict((user['id'], User.from_dict(user)) for user in data.get('users', self.users.values()))

    def save(self):
        db.save('trovo', {
            'access_token': self.api.access_token,
            'refresh_token': self.api.refresh_token,
            'users': [user.__dict__() for user in self.users.values()]
        })

    def send_message(self, msg: str):
        return self.api.send_message(msg, self.channel_id)

    @staticmethod
    def get_new_nonce() -> str:
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(10))
