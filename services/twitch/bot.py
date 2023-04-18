import asyncio
import logging
import os

from dotenv import load_dotenv
from twitchAPI import UserAuthenticator, Chat
from twitchAPI.chat import EventData, ChatMessage, ChatSub
from twitchAPI.helper import first
from twitchAPI.oauth import refresh_access_token
from twitchAPI.object import TwitchUser
from twitchAPI.twitch import Twitch
from twitchAPI.types import AuthScope, InvalidRefreshTokenException, ChatEvent

import commands
import db
import models
from logger import setup_logger
from models import ChatBot

_log = logging.getLogger(__name__)


class TwitchBot(ChatBot):
    twitch: Twitch
    chat: Chat
    access_token: str = None
    refresh_token: str = None
    user: TwitchUser
    auth_data_path = 'auth/twitch'
    scope = [
        AuthScope.CHAT_READ,
        AuthScope.CHAT_EDIT,
        AuthScope.CHANNEL_MANAGE_SCHEDULE,
        AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
        AuthScope.MODERATOR_MANAGE_BANNED_USERS,
        AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES,
        AuthScope.MODERATOR_READ_FOLLOWERS
    ]
    message_queue = []

    def __init__(self, client_id: str, client_secret: str, redirect_url: str, channel_name: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.channel_name = channel_name

    async def run(self):
        async def on_ready(ready_event: EventData):
            _log.info("Twitch chat ready")
            await ready_event.chat.join_room(self.channel_name)
            await ready_event.chat.send_message(self.channel_name, 'Awakening')

        async def on_message(msg: ChatMessage):
            user = db.find_user(msg.user.name, twitch_id=int(msg.user.id))
            message = models.ChatMessage(
                text=msg.text,
                sender=user,
                roles=msg.user.badges.keys()
            )
            commands.trigger_commands(message, self)
            _log.debug(f'Message received: {msg.text}')

        async def on_sub(sub: ChatSub):
            _log.info(f'New subscription [{sub.sub_plan}]: {sub.sub_message}')

        self.twitch = await Twitch(self.client_id, self.client_secret)
        self.load()
        await self.auth()
        self.save()
        self.user = await first(self.twitch.get_users(logins=[self.channel_name]))
        await self.twitch.set_user_authentication(self.access_token, self.scope, self.refresh_token)

        self.chat = await Chat(self.twitch)
        self.chat.register_event(ChatEvent.READY, on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, on_message)
        self.chat.register_event(ChatEvent.SUB, on_sub)
        self.chat.start()

        self.message_queue.clear()

        while True:
            if not self.chat.is_connected:
                self.chat.stop()
                self.chat.start()

            if len(self.message_queue) > 0:
                msg = self.message_queue.pop(0)
                await self.chat.send_message(self.channel_name, msg)
            else:
                await asyncio.sleep(0.1)

    async def auth(self):
        try:
            self.access_token, self.refresh_token = await refresh_access_token(
                self.refresh_token, self.client_id, self.client_secret)
        except InvalidRefreshTokenException:
            auth = UserAuthenticator(self.twitch, self.scope, url=self.redirect_url)
            auth.port = int(self.redirect_url.split(':')[2])
            self.access_token, self.refresh_token = await auth.authenticate()

    def save(self):
        db.save(self.auth_data_path, {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        })

    def load(self):
        data = db.load(self.auth_data_path)
        self.access_token = data.get('access_token', self.access_token)
        self.refresh_token = data.get('refresh_token', self.refresh_token)

    def send_message(self, msg: str):
        self.message_queue.append(msg)
