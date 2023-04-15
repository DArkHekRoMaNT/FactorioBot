import asyncio
import json
import logging
import random
import string
import traceback
from time import time

import websockets

import db
from commands import trigger_commands
from models import ChatBot, PointsType, ChatMessage, UserData
from .api import TrovoApi
from .models import TrovoChatMessage, TrovoChatSocketMessage, TrovoChatMessageType

_log = logging.getLogger(__name__)


class TrovoChat(ChatBot):
    chat_url = 'wss://open-chat.trovo.live/chat'
    request_queue = []
    heartbeat_gap = 30
    ws = None
    active = False
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

    @staticmethod
    def loop(name: str):
        def decorator(func):
            async def wrapper(self):
                try:
                    _log.info(f'{name} loop started')
                    while self.active:
                        await func(self)

                except Exception as e:
                    _log.error(f'{name} loop crashed: {e}')
                    _log.debug(traceback.format_exc())
                    self.active = False

            return wrapper
        return decorator

    @loop('Ping-pong')
    async def _ping_pong_loop(self):
        await asyncio.sleep(self.heartbeat_gap)
        self.request_queue.append({
            'type': 'PING',
            'nonce': self.get_new_nonce()
        })

    @loop('Response')
    async def _response_loop(self):
        try:
            data = await self.ws.recv()
            _log.debug(f'Response: {data}')
            raw_msg = TrovoChatSocketMessage.from_dict(json.loads(data))

            match raw_msg.type:
                case "AUTH":
                    self.send_message('Awakening')

                case "PONG":
                    self.last_pong_time = time()
                    self.heartbeat_gap = raw_msg.data.get('gap', 30)

                case "CHAT":
                    for raw_chat_msg in raw_msg.data.get('chats', []):
                        msg = TrovoChatMessage.from_dict(raw_chat_msg)
                        if msg.send_time >= self.start_time:
                            user = db.find_user(msg.nick_name, trovo_id=msg.sender_id)
                            self.check_donation(msg, user)
                            trigger_commands(ChatMessage(
                                text=msg.content,
                                sender=user,
                                roles=msg.roles
                            ), self)
                        else:
                            _log.debug(f'Old message "{msg.content}" ignored')

        except websockets.ConnectionClosedError as e:
            _log.error(f'Response loop connection error, stopped: {e}')
            _log.debug(traceback.format_exc())
            self.active = False

    @loop('Request')
    async def _request_loop(self):
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
            return

        msg = self.request_queue.pop(0)
        data = json.dumps(msg)
        _log.debug(f'Request: {data}')
        await self.ws.send(data)

    def check_donation(self, msg: TrovoChatMessage, user: UserData):
        if msg.type == TrovoChatMessageType.SPELLS:
            content = json.loads(msg.content)
            value = content.get('gift_value')
            num = content.get('num')
            if content.get('value_type') == 'Mana':
                db.add_points(user, num * value, PointsType.Mana, bot=self)
            elif content.get('value_type') == 'Elixir':
                db.add_points(user, num * value, PointsType.Elixir, bot=self)

        elif msg.type == TrovoChatMessageType.SUBSCRIPTION_MESSAGE:
            db.add_points(user, 500, PointsType.Elixir, bot=self)

    def load(self):
        auth = db.load('auth/trovo')
        self.api.access_token = auth.get('access_token', self.api.access_token)
        self.api.refresh_token = auth.get('refresh_token', self.api.refresh_token)

    def save(self):
        db.save('auth/trovo', {
            'access_token': self.api.access_token,
            'refresh_token': self.api.refresh_token
        })

    def send_message(self, msg: str):
        return self.api.send_message(msg, self.channel_id)

    @staticmethod
    def get_new_nonce() -> str:
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(10))
