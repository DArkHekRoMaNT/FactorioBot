import asyncio
import json
import logging
import traceback

import socketio

import db
from models import ChatBot, PointsType
from .alert_message import AlertMessage

_log = logging.getLogger(__name__)


class DonationAlerts:
    sio = socketio.AsyncClient()

    def __init__(self, token: str, announce_bot: ChatBot = None):
        self.token = token
        self.announce_bot = announce_bot

    async def run(self):
        @self.sio.on('connect')
        async def on_connect():
            await self.sio.emit('add-user', {'token': self.token, 'type': 'alert_widget'})

        @self.sio.on('donation')
        async def on_message(data):
            data = json.loads(data)
            msg = AlertMessage.from_dict(data)
            _log.info(msg)

            if msg.is_test_alert:
                _log.debug(f'Test alert, skipped')
                return

            try:
                match int(msg.alert_type):
                    case 1:
                        p_type = PointsType.Elixir
                        amount = int(msg.amount_main)
                    case 19:
                        p_type = PointsType.Mana
                        amount = int(float(msg.amount))
                    case _:
                        return

                user = db.find_user(msg.username)
                db.add_points(user, amount, p_type, bot=self.announce_bot)

            except Exception as e:
                _log.error(f'Can\'t add donation points {e}')
                _log.debug(traceback.format_exc(e))

        while True:
            if self.sio.connected:
                await asyncio.sleep(30)
                continue

            await self.sio.connect('wss://socket.donationalerts.ru:443', transports='websocket')
            _log.info('Socket connected')
