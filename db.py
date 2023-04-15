import json
import logging
import os
import zipfile
from datetime import datetime
from json import JSONDecodeError

import utils
from models import PointsType, UserData, ChatBot

_log = logging.getLogger(__name__)

users_filename = 'users'
users: list[UserData] = []


def init():
    global users, users_filename
    users = load(users_filename)


def save(filename: str, data: dict or list):
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(f'data/{filename}.json', 'w+', encoding='utf-8') as f:
            f.write(json.dumps(data, default=dict, indent=True))
    except Exception as e:
        _log.critical(e)


def load(filename: str) -> dict or list:
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(f'data/{filename}.json', 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    except FileNotFoundError as e:
        _log.warning(f'File not found {e.filename}')
    except JSONDecodeError as e:
        _log.error(e)
    except Exception as e:
        _log.critical(e)
    return {}


def backup():
    backup_path = f'backups/backup_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.zip'
    if not os.path.exists('backups'):
        os.makedirs('backups')
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('data/'):
            for file in files:
                filepath = os.path.join(root, file)
                zf.write(filepath)
    _log.info(f'Backup file {backup_path} created')


def add_points(user: UserData, quantity: int, points_type: PointsType, *, bot: ChatBot = None):
    global users, users_filename

    match points_type:
        case points_type.Mana:
            user.mana = user.mana + quantity
            _log.info(f'Added {quantity} mana points to {user.name}. Total: {user.elixir}')
            if bot:
                bot.send_message(f'Add {quantity} mp to {user.name}')

        case points_type.Elixir:
            user.elixir = user.elixir + quantity
            _log.info(f'Added {quantity} elixir points to {user.name}. Total: {user.mana}')
            if bot:
                bot.send_message(f'Add {quantity} ep to {user.name}')

    save(users_filename, users)


def find_user(username: str, *, trovo_id: int = -1, twitch_id: int = -1) -> UserData:
    user = utils.first(users, matcher=lambda usr: usr.name == username)

    if not user and trovo_id != -1:
        user = utils.first(users, matcher=lambda usr: usr.trovo_id == trovo_id)

    if not user and twitch_id != -1:
        user = utils.first(users, matcher=lambda usr: usr.twitch_id == twitch_id)

    if not user:
        user = UserData(
            name=username,
            mana=0,
            elixir=0,
            trovo_id=trovo_id,
            twitch_id=twitch_id
        )
        users.append(user)

    return user
