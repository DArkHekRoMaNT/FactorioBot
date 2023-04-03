import logging
import os

import factorio_rcon

from .chat import TrovoChat
from .commands import command
from .models import ChatMessage

_log = logging.getLogger(__name__)


class FactorioClient(factorio_rcon.RCONClient):
    def __init__(self, ip_address: str, port: int, password: str):
        super().__init__(ip_address, port, password, connect_on_init=False)

    def try_connect(self):
        try:
            self.connect()
            return True
        except Exception as e:
            _log.error(f"factorio client: {e}")
            return False


factorio_client: FactorioClient


def create(client_id: str, client_secret: str, channel_id: str) -> TrovoChat:
    global factorio_client
    factorio_client = FactorioClient(
        os.getenv("FACTORIO_RCON_HOST"),
        int(os.getenv("FACTORIO_RCON_PORT")),
        os.getenv("FACTORIO_RCON_PASS")
    )
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
        bot.send_message(f"{user_name}: {0} mp, {0} ep")
    else:
        bot.send_message(f"{user.name}: {user.mana} mp, {user.elixir} ep")


def factorio_command(msg: ChatMessage, bot: TrovoChat, mana: int, elixir: int, cmd_name: str, answer: str):
    user = bot.get_user(msg.sender_id, msg.nick_name)
    if user.mana >= mana >= 0 or user.elixir >= elixir >= 0:
        try:
            factorio_client.send_command(cmd_name)
            if user.mana >= mana >= 0:
                bot.add_mana(user, -mana)
            elif user.elixir >= elixir >= 0:
                bot.add_elixir(user, -elixir)
            bot.send_message(answer.replace("{user}", user.name))
        except Exception as e:
            _log.error(f"Try trigger factorio command {cmd_name} by {user.name}: {e}")
            factorio_client.try_connect()
    else:
        if mana < 0:
            bot.send_message(f"@{user.name} не хватает ({elixir} ep)")
        elif elixir < 0:
            bot.send_message(f"@{user.name} не хватает ({mana} mp)")
        else:
            bot.send_message(f"@{user.name} не хватает ({elixir} ep или {mana} mp)")


@command('biters', aliases=['кусаки'])
def bitters_command(msg: ChatMessage, bot: TrovoChat):
    factorio_command(msg, bot, 3500, 70, "/spawn_biters DArkHekRoMaNT", "{user} отправил толпу кусак")


@command('splitters', aliases=['плеваки'])
def bitters_command(msg: ChatMessage, bot: TrovoChat):
    factorio_command(msg, bot, 4000, 80, "/spawn_splitters DArkHekRoMaNT", "{user} отправил толпу плевак")


@command('worms', aliases=['черви'])
def bitters_command(msg: ChatMessage, bot: TrovoChat):
    factorio_command(msg, bot, 5000, 100, "/spawn_worms DArkHekRoMaNT", "{user} призвал червей")


@command('spawners', aliases=['гнезда'])
def bitters_command(msg: ChatMessage, bot: TrovoChat):
    factorio_command(msg, bot, 10000, 200, "/spawn_spawners DArkHekRoMaNT", "{user} заспавнил метеорит из кусак")


@command('hotpotato', aliases=['горячаякартошка'])
def bitters_command(msg: ChatMessage, bot: TrovoChat):
    factorio_command(msg, bot, 2500, 50, "/give_item DArkHekRoMaNT uranium_ore 10", "{user} добавил немного радиации")


@command('reactor', aliases=['реактор'])
def bitters_command(msg: ChatMessage, bot: TrovoChat):
    factorio_command(msg, bot, -1, 300, "/give_item DArkHekRoMaNT uranium_ore 999999999",
                     "{user} помог запустить реактор")


@command('dropall', aliases=['выброситьвсе'])
def bitters_command(msg: ChatMessage, bot: TrovoChat):
    factorio_command(msg, bot, 2500, 50, "/drop_all DArkHekRoMaNT", "{user} разгрузил инвентарь")
