import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any


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
