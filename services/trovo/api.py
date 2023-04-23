import json
import logging
from time import time
from urllib.parse import urlencode

import requests

from utils import request_oauth_login_by_user

_log = logging.getLogger(__name__)


class TrovoAccount:
    access_token: str or None = None
    refresh_token: str or None = None


class TrovoApi:
    login_url = 'https://open.trovo.live/page/login.html'
    api_url = 'https://open-api.trovo.live/openplatform'
    scopes = [
        'user_details_self',        # View your email address and user profiles.
        'channel_details_self',     # View your channel details. Including Stream Key.
        'channel_update_self',      # Update your channel settings
        'channel_subscriptions',    # Get your subscribers list.
        'chat_send_self',           # Send chat messages on behalf of myself.
        'send_to_my_channel',       # Send chat messages to my channel.
        'manage_messages'           # Perform chat commands and delete chat messages.
    ]
    channel_id = ''

    def __init__(self, client_id: str, client_secret: str, redirect_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_url
        self.channel = TrovoAccount()
        self.bot = TrovoAccount()

    def auth(self) -> bool:
        success = self._auth(self.channel) and self._auth(self.bot)
        if success:
            info = self.get_channel_info()
            self.channel_id = info['channel_id']
        return success

    def _auth(self, acc: TrovoAccount) -> bool:
        if not acc.access_token and not acc.refresh_token:
            _log.info('First auth. Open browser')
            code = self._get_code(self.scopes)
            token = self._get_token(code)
            acc.access_token = token.get('access_token')
            acc.refresh_token = token.get('refresh_token')
            return acc.access_token

        if acc.refresh_token and not self.is_token_valid(acc.access_token):
            return self.refresh(acc)

        return self.is_token_valid(acc.access_token)

    def _get_token(self, code: str) -> dict:
        r = requests.post(f'{self.api_url}/exchangetoken', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Content-Type': 'application/json'
        }, json={
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        })
        _log.debug(f'First auth response: {r.text}')
        return json.loads(r.text)

    def _get_code(self, scopes: list) -> str:
        d = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': '+'.join(scopes),
            'redirect_uri': self.redirect_uri
        }
        return request_oauth_login_by_user(f'{self.login_url}?{urlencode(d)}')['code'][0]

    def is_token_valid(self, access_token: str) -> bool:
        _log.info('Check is access token valid')
        d = self.validate_token(access_token)
        if 'error' in d:
            _log.error('Invalid access token. Error: ' + d['error'])
            return False
        if int(d.get('expire_ts')) < time():
            _log.warning('Expired access token')
            return False
        _log.info('Valid access token')
        return True

    def validate_token(self, access_token: str) -> dict:
        _log.info('Validate access token')
        r = requests.get(f'{self.api_url}/validate', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Authorization': 'OAuth ' + access_token
        })
        _log.debug(f'Validate access token response: {r.text}')
        return json.loads(r.text)

    def refresh(self, acc: TrovoAccount) -> bool:
        _log.info('Refresh token')
        r = requests.post(f'{self.api_url}/revoke', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Authorization': 'OAuth ' + acc.access_token
        }, json={
            'access_token': acc.access_token
        })
        _log.debug(f'Revoke old access token response: {r.text}')
        r = requests.post(f'{self.api_url}/refreshtoken', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Content-Type': 'application/json'
        }, json={
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': acc.refresh_token
        })
        _log.debug(f'Refresh access token response: {r.text}')
        d = json.loads(r.text)
        acc.access_token = d.get('access_token')
        acc.refresh_token = d.get('refresh_token')
        return acc.access_token

    def send_message(self, msg: str, times: int = 1):
        if times > 3:
            _log.error(f'Can\'t send message {msg}')
            return

        _log.info(f'Send message: {msg}')
        r = requests.post(f'{self.api_url}/chat/send', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Authorization': 'OAuth ' + self.bot.access_token,
            'Content-Type': 'application/json'
        }, json={
            'content': msg,
            'channel_id': self.channel_id
        })
        _log.debug(f'Send message response: {r.text}')

        if r.text != '' and json.loads(r.text).get('error') == 'accessTokenExpired':
            self.auth()
            self.send_message(msg, times + 1)

    def get_channel_chat_token(self) -> str:
        _log.info('Get channel chat token')
        r = requests.get(f'{self.api_url}/chat/channel-token/{self.channel_id}', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Authorization': 'OAuth ' + self.channel.access_token
        })
        _log.debug(f'Get channel chat token response: {r.text}')
        d = json.loads(r.text)
        return d.get('token', '')

    def get_channel_info(self) -> dict:
        _log.info('Get channel info')
        r = requests.get(f'{self.api_url}/channel', headers={
            'Accept': 'application/json',
            'Client-ID': self.client_id,
            'Authorization': 'OAuth ' + self.channel.access_token
        })
        return json.loads(r.text)

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
