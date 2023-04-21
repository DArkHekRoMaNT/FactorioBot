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
from ._chat_message import TrovoChatMessage, TrovoChatMessageType
from ._chat_socket_message import TrovoChatSocketMessage

_log = logging.getLogger(__name__)


class TrovoChat(ChatBot):
    chat_url = 'wss://open-chat.trovo.live/chat'
    request_queue = []
    active = False
    start_time = 0
    last_pong_time = 0
    heartbeat_gap = 30

    def __init__(self, client_id: str, client_secret: str, redirect_url: str, channel_id: str):
        self.api = TrovoApi(client_id, client_secret, redirect_url)
        self.channel_id = channel_id

    async def run(self):
        async for ws in websockets.connect(self.chat_url):
            self.load()
            if not self.api.auth():
                _log.critical('Auth error')
                return
            self.save()

            self.request_queue.clear()
            self.active = True
            self.start_time = int(time())
            self.last_pong_time = 0
            self.heartbeat_gap = 30

            tasks = [
                asyncio.create_task(self._ping_pong_loop()),
                asyncio.create_task(self._response_loop(ws)),
                asyncio.create_task(self._request_loop(ws))
            ]
            try:
                await asyncio.gather(*tasks)
            except Exception as e:
                _log.error(f'Chat loop crashed: {e}')
                _log.debug(traceback.format_exc())
                for task in tasks:
                    task.cancel()

            if not self.active:
                break

            await asyncio.sleep(5)

    async def _ping_pong_loop(self):
        _log.info(f'Ping-pong loop started')
        while self.active:
            await asyncio.sleep(self.heartbeat_gap)
            self.request_queue.append({
                'type': 'PING',
                'nonce': self.get_new_nonce()
            })

    async def _response_loop(self, ws):
        _log.info(f'Response loop started')
        while self.active:
            data = await ws.recv()
            _log.debug(f'Response: {data}')
            raw_msg = TrovoChatSocketMessage.from_dict(json.loads(data))
            self._process_message(raw_msg)

    async def _request_loop(self, ws):
        _log.info(f'Request loop started')
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
            await ws.send(data)

    def _process_message(self, raw_msg: TrovoChatSocketMessage):
        match raw_msg.type:
            case "RESPONSE":
                self.send_message('Awakening')

            case "PONG":
                self.last_pong_time = time()
                self.heartbeat_gap = raw_msg.data.get('gap', 30)

            case "CHAT":
                for raw_chat_msg in raw_msg.data.get('chats', []):
                    msg = TrovoChatMessage.from_dict(raw_chat_msg)
                    if msg.send_time >= self.start_time:
                        user = db.find_user(msg.nick_name, trovo_id=msg.sender_id)
                        self._check_donation(msg, user)
                        trigger_commands(ChatMessage(
                            text=msg.content,
                            sender=user,
                            roles=msg.roles
                        ), self)
                    else:
                        _log.debug(f'Old message "{msg.content}" ignored')

    def _check_donation(self, msg: TrovoChatMessage, user: UserData):
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
