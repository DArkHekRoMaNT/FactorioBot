import asyncio
import json
import logging
import traceback
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import socketio

import db
from models import ChatBot, PointsType

_log = logging.getLogger(__name__)


@dataclass
class AlertMessage:
    id: int
    alert_type: str
    is_shown: str
    additional_data: dict
    billing_system: str
    billing_system_type: str
    username: str
    amount: str
    amount_formatted: str
    amount_main: int
    currency: str
    message: str
    header: str
    date_created: Any
    emotes: str
    ap_id: str
    is_test_alert: bool
    message_type: str
    preset_id: int
    objects: dict

    @staticmethod
    def from_dict(obj) -> 'AlertMessage':
        return AlertMessage(
            id=obj.get('id'),
            alert_type=obj.get('alert_type'),
            is_shown=obj.get('is_shown'),
            additional_data=json.loads(obj.get('additional_data', '')),
            billing_system=obj.get('billing_system'),
            billing_system_type=obj.get('billing_system_type'),
            username=obj.get('username'),
            amount=obj.get('amount'),
            amount_formatted=obj.get('amount_formatted'),
            amount_main=obj.get('amount_main'),
            currency=obj.get('currency'),
            message=obj.get('message'),
            header=obj.get('header'),
            date_created=datetime.strptime(obj.get('date_created', ''), '%Y-%m-%d %H:%M:%S'),
            emotes=obj.get('emotes'),
            ap_id=obj.get('ap_id'),
            is_test_alert=obj.get('_is_test_alert'),
            message_type=obj.get('message_type'),
            preset_id=obj.get('preset_id'),
            objects=obj
        )


sio = socketio.AsyncClient()


async def run(token: str, bot: ChatBot):
    @sio.on('connect')
    async def on_connect():
        await sio.emit('add-user', {'token': token, 'type': 'alert_widget'})

    @sio.on('donation')
    async def on_message(data):
        data = json.loads(data)
        msg = AlertMessage.from_dict(data)
        _log.info(msg)

        if msg.is_test_alert:
            return

        try:
            user = db.find_user(msg.username)
            db.add_points(user, msg.amount_main, PointsType.Elixir, bot=bot)
        except Exception as e:
            _log.error(f'Can\'t add donation points {e}')
            _log.debug(traceback.format_exc(e))

    while True:
        if sio.connected:
            await asyncio.sleep(30)
            continue

        await sio.connect('wss://socket.donationalerts.ru:443', transports='websocket')
        _log.info('Socket connected')
