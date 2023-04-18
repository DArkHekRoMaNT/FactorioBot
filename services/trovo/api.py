import json
import logging
from time import time
from urllib.parse import urlencode

import requests

from utils import request_oauth_login_by_user

_log = logging.getLogger(__name__)


class TrovoApi:
    login_url = 'https://open.trovo.live/page/login.html'
    api_url = 'https://open-api.trovo.live/openplatform'
    scopes = [
        'user_details_self',
        'channel_details_self',
        'channel_update_self',
        'channel_subscriptions',
        'chat_send_self',
        'send_to_my_channel',
        'manage_messages'
    ]

    def __init__(self, client_id: str, client_secret: str, redirect_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_url
        self.access_token = None
        self.refresh_token = None

    def auth(self) -> bool:
        if self.access_token is None and self.refresh_token is None:
            return self.first_auth()

        if self.refresh_token is not None and not self.is_token_valid():
            return self.refresh_access_token()

        return self.is_token_valid()

    def first_auth(self) -> bool:
        _log.info('First auth. Open browser')
        r = requests.post(f'{self.api_url}/exchangetoken', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Content-Type': 'application/json'
        }, json={
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': self._get_code(),
            'redirect_uri': self.redirect_uri
        })
        _log.debug(f'First auth response: {r.text}')
        d = json.loads(r.text)
        self.access_token = d.get('access_token')
        self.refresh_token = d.get('refresh_token')
        return self.access_token is not None

    def _get_code(self) -> str:
        d = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': '+'.join(self.scopes),
            'redirect_uri': self.redirect_uri
        }
        return request_oauth_login_by_user(f'{self.login_url}?{urlencode(d)}')

    def is_token_valid(self) -> bool:
        _log.info('Check is access token valid')
        d = self.validate_access_token()
        if 'error' in d:
            _log.error('Invalid access token. Error: ' + d['error'])
            return False
        if int(d.get('expire_ts')) < time():
            _log.warning('Expired access token')
            return False
        _log.info('Valid access token')
        return True

    def validate_access_token(self) -> dict:
        _log.info('Validate access token')
        r = requests.get(f'{self.api_url}/validate', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Authorization': 'OAuth ' + self.access_token
        })
        _log.debug(f'Validate access token response: {r.text}')
        return json.loads(r.text)

    def refresh_access_token(self) -> bool:
        _log.info('Refresh token')
        r = requests.post(f'{self.api_url}/revoke', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Authorization': 'OAuth ' + self.access_token
        }, json={
            'access_token': self.access_token
        })
        _log.debug(f'Revoke old access token response: {r.text}')
        r = requests.post(f'{self.api_url}/refreshtoken', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Content-Type': 'application/json'
        }, json={
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        })
        _log.debug(f'Refresh access token response: {r.text}')
        d = json.loads(r.text)
        self.access_token = d.get('access_token')
        self.refresh_token = d.get('refresh_token')
        return self.access_token is not None

    def send_message(self, msg: str, channel_id: str):
        _log.info(f'Send message: {msg}')
        r = requests.post(f'{self.api_url}/chat/send', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Authorization': 'OAuth ' + self.access_token,
            'Content-Type': 'application/json'
        }, json={
            'content': msg,
            'channel_id': channel_id
        })
        _log.debug(f'Send message response: {r.text}')

    def get_channel_chat_token(self, channel_id: str) -> str:
        _log.info('Get channel chat token')
        r = requests.get(f'{self.api_url}/chat/channel-token/' + channel_id, headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Authorization': 'OAuth ' + self.access_token
        })
        _log.debug(f'Get channel chat token response: {r.text}')
        d = json.loads(r.text)
        return d.get('token', '')

    def get_users(self, user_names: list) -> dict:
        _log.info(f'Get users info: ' + ', '.join(user_names))
        r = requests.post(f'{self.api_url}/getusers', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id
        }, json={
            'user': user_names
        })
        _log.debug(f'Get users info response: {r.text}')
        return json.loads(r.text)
