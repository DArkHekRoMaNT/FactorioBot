import logging
import os

import factorio_rcon
from factorio_rcon import RCONConnectError

from .chat import TrovoChat
from .commands import command
from .models import ChatMessage

_log = logging.getLogger(__name__)
rcon_client = None


def create(client_id: str, client_secret: str, channel_id: str) -> TrovoChat:
    return TrovoChat(client_id, client_secret, channel_id)


@command('addmp', owner_only=True)
def add_mp_command(msg: ChatMessage, bot: TrovoChat):
    args = msg.content.split()
    if len(args) > 2:
        user = bot.find_user(args[1])
        bot.add_mana(user, int(args[2]))


@command('addep', owner_only=True)
def add_ep_command(msg: ChatMessage, bot: TrovoChat):
    args = msg.content.split()
    if len(args) > 2:
        user = bot.find_user(args[1])
        bot.add_elixir(user, int(args[2]))


@command('points', aliases=['p', 'очки'])
def points_command(msg: ChatMessage, bot: TrovoChat):
    user = None
    user_name = None

    if msg.roles.__contains__('streamer'):
        args = msg.content.split()
        if len(args) > 1:
            user_name = args[1]
            user_name = user_name.removeprefix('@')

    for usr in bot.users.values():
        if (user_name is None and usr.id == msg.sender_id) or usr.name == user_name:
            user = usr
            break

    if user is None:
        if user_name is None:
            user_name = msg.nick_name
        bot.send_message(f"{user_name} has {0} mp and {0} ep")
    else:
        bot.send_message(f"{user.name} has {user.mana} mp and {user.elixir} ep")


@command('bitters', aliases=['кусаки'])
def bitters_command(msg: ChatMessage, bot: TrovoChat):
    global rcon_client
    if rcon_client is None:
        try:
            rcon_client = factorio_rcon.RCONClient(
                os.getenv("FACTORIO_RCON_HOST"),
                int(os.getenv("FACTORIO_RCON_PORT")),
                os.getenv("FACTORIO_RCON_PASS"),
            )
        except RCONConnectError as e:
            _log.error(f'bitters_command: {e}')
            return

    try:
        for user in bot.users.values():
            if user.id == msg.sender_id:
                if user.mana > 5000:
                    user.mana -= 5000
                elif user.elixir > 100:
                    user.elixir -= 100
                else:
                    bot.send_message(f"@{user.name} need more points (5000 mp or 100 ep)")
                    return
                rcon_client.send_command("/sb")
                bot.send_message(f"@{user.name} summon biters around")
    except Exception as e:
        _log.error(f'/sb: {e}')
        rcon_client.close()
        rcon_client = None
