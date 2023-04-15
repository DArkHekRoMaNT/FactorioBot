import logging
import os

import factorio_rcon

import db
from commands import command
from models import ChatMessage, ChatBot, PointsType

_log = logging.getLogger(__name__)

active = False

client: factorio_rcon


def try_connect_rcon():
    global client
    try:
        if not client:
            client = factorio_rcon.RCONClient(
                os.getenv("FACTORIO_RCON_HOST"),
                int(os.getenv("FACTORIO_RCON_PORT")),
                os.getenv("FACTORIO_RCON_PASS")
            )

        if client.rcon_socket is None:
            client.connect()
    except Exception as e:
        _log.error(f"factorio client: {e}")


def factorio_command(msg: ChatMessage, bot: ChatBot, mana: int, elixir: int, cmd_name: str, answer: str):
    global client, active
    user = msg.sender

    if not active:
        _log.info(f'Module disabled, {cmd_name} by {user.name} skipped')
        return

    _log.info(f'Trigger factorio command {cmd_name} by {user.name}')
    if user.mana >= mana >= 0 or user.elixir >= elixir >= 0:
        try:
            try_connect_rcon()
            client.send_command(cmd_name)
            if user.mana >= mana >= 0:
                db.add_points(user, -mana, PointsType.Mana)
            elif user.elixir >= elixir >= 0:
                db.add_points(user, -elixir, PointsType.Elixir)
            bot.send_message(answer.replace("{user}", user.name))
        except Exception as e:
            _log.error(f"Error {cmd_name} by {user.name}: {e}")
    else:
        if mana < 0:
            bot.send_message(f"@{user.name} не хватает ({elixir} ep)")
        elif elixir < 0:
            bot.send_message(f"@{user.name} не хватает ({mana} mp)")
        else:
            bot.send_message(f"@{user.name} не хватает ({elixir} ep или {mana} mp)")


@command('biters', aliases=['кусаки'])
def bitters_command(msg: ChatMessage, bot: ChatBot):
    factorio_command(msg, bot, 3500, 70, "/spawn_biters DArkHekRoMaNT", "{user} отправил толпу кусак")


@command('splitters', aliases=['плеваки'])
def splitters_command(msg: ChatMessage, bot: ChatBot):
    factorio_command(msg, bot, 4000, 80, "/spawn_splitters DArkHekRoMaNT", "{user} отправил толпу плевак")


@command('worms', aliases=['черви'])
def worms_command(msg: ChatMessage, bot: ChatBot):
    factorio_command(msg, bot, 5000, 100, "/spawn_worms DArkHekRoMaNT", "{user} призвал червей")


@command('spawners', aliases=['гнезда'])
def spawners_command(msg: ChatMessage, bot: ChatBot):
    factorio_command(msg, bot, 10000, 200, "/spawn_spawners DArkHekRoMaNT", "{user} заспавнил метеорит из кусак")


@command('hotpotato', aliases=['горячаякартошка'])
def hotpotato_command(msg: ChatMessage, bot: ChatBot):
    factorio_command(msg, bot, 2500, 50, "/give_item DArkHekRoMaNT uranium_ore 100",
                     "{user} добавил немного радиации")


@command('reactor', aliases=['реактор'])
def reactor_command(msg: ChatMessage, bot: ChatBot):
    factorio_command(msg, bot, -1, 300, "/give_item DArkHekRoMaNT uranium_ore 999999999",
                     "{user} помог запустить реактор")


@command('dropall', aliases=['выброситьвсе'])
def dropall_command(msg: ChatMessage, bot: ChatBot):
    factorio_command(msg, bot, 2500, 50, "/drop_all DArkHekRoMaNT", "{user} разгрузил инвентарь")