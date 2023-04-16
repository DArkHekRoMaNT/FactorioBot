import json
import logging
from asyncio import sleep

import requests
from donationalerts import DonationAlertsAPI, Scopes, DEFAULT_URL, Centrifugo
from donationalerts.asyncio_api import Alert

import db
from utils import request_oauth_login_by_user

_log = logging.getLogger(__name__)


class DonationAlertsService:
    auth_data_path = 'auth/donation_alerts'
    data_path = 'donation_alerts'
    access_token: str = None
    refresh_token: str = None
    active = False
    centrifugo: Centrifugo = None

    def __init__(self, client_id: str, client_secret: str, redirect_url: str):
        self.api = DonationAlertsAPI(client_id, client_secret, redirect_url, Scopes.ALL_SCOPES)

    def auth(self) -> bool:
        if not self.access_token and not self.refresh_token:
            _log.info('First auth. Open browser')
            code = request_oauth_login_by_user(self.api.login())
            json_request = self.api.get_access_token(code, full_json=True)
            self.access_token = json_request.access_token
            self.refresh_token = json_request.refresh_token
            return self.is_token_valid()

        if self.is_token_valid():
            return True
        elif self.refresh_token:
            _log.info('Refresh token')
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.api.client_id,
                'client_secret': self.api.client_secret,
                'scope': self.api.scope
            }
            response = requests.post(f"{DEFAULT_URL}token", data=payload)
            obj = json.loads(response.text)
            self.access_token = obj.get('access_token')
            self.refresh_token = obj.get('refresh_token')
            return self.is_token_valid()
        else:
            return False

    def is_token_valid(self) -> bool:
        _log.info('Check is access token valid')
        try:
            self.api.user(self.access_token)
            return True
        except KeyError:
            _log.info('Invalid token')
            return False

    async def run(self):
        self.load()
        if not self.auth():
            _log.critical('Auth error')
            return
        self.save()

    def save(self):
        db.save(self.auth_data_path, {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        })

    def load(self):
        data = db.load(self.auth_data_path)
        self.access_token = data.get('access_token')
        self.refresh_token = data.get('refresh_token')
