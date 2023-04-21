import logging
import traceback

import factorio_rcon

from commands import command
from models import ChatMessage, ChatBot

_log = logging.getLogger(__name__)


class FactorioBot(ChatBot):
    client: factorio_rcon.RCONClient = None
    cmd_queue = []

    def __init__(self, rcon_host: str, rcon_port: int, rcon_password: str, username: str):
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_password = rcon_password
        self.username = username
        self._registry()

    def start(self):
        self.client = factorio_rcon.RCONClient(
            ip_address=self.rcon_host,
            port=self.rcon_port,
            password=self.rcon_password,
            connect_on_init=False
        )

    def send_message(self, msg: str):
        self.reconnect()
        # Console input that does not start with / is shown as a chat message to your team.
        self.client.send_command(msg)

    def reconnect(self):
        try:
            if not self.client.rcon_socket:
                self.client.connect()
                _log.info(f'Factorio client connected')
        except Exception as e:
            _log.error(f'Factorio client error: {e}')
            _log.debug(traceback.format_exc())

    def _registry(self):
        def execute(cmd: str):
            _log.info(f'Trigger factorio command {cmd}')
            self.reconnect()
            self.client.send_command(cmd)

        @command('biters', aliases=['кусаки'], mana=3500, elixir=70, module='factorio')
        def bitters_command(msg: ChatMessage, bot: ChatBot):
            execute(f'/spawn_biters {self.username}')
            bot.send_message(f'{msg.sender.name} отправил толпу кусак')

        @command('spitters', aliases=['плеваки'], mana=4000, elixir=80, module='factorio')
        def splitters_command(msg: ChatMessage, bot: ChatBot):
            execute(f'/spawn_spitters {self.username}')
            bot.send_message(f'{msg.sender.name} отправил толпу плевак')

        @command('worms', aliases=['черви'], mana=5000, elixir=100, module='factorio')
        def worms_command(msg: ChatMessage, bot: ChatBot):
            execute(f'/spawn_worms {self.username}')
            bot.send_message(f'{msg.sender.name} призвал червей')

        @command('spawners', aliases=['гнезда'], mana=10000, elixir=200, module='factorio')
        def spawners_command(msg: ChatMessage, bot: ChatBot):
            execute(f'/spawn_spawners {self.username}')
            bot.send_message(f'{msg.sender.name} заспавнил метеорит из кусак')

        @command('hotpotato', aliases=['горячаякартошка'], mana=2500, elixir=50, module='factorio')
        def hotpotato_command(msg: ChatMessage, bot: ChatBot):
            execute(f'/give_item {self.username} uranium_ore 100')
            bot.send_message(f'{msg.sender.name} добавил немного радиации')

        @command('reactor', aliases=['реактор'], mana=-1, elixir=100, module='factorio')
        def reactor_command(msg: ChatMessage, bot: ChatBot):
            execute(f'/give_item {self.username} uranium_ore 999999999')
            bot.send_message(f'{msg.sender.name} помог запустить реактор')

        @command('dropall', aliases=['выброситьвсе'], mana=2500, elixir=50, module='factorio')
        def dropall_command(msg: ChatMessage, bot: ChatBot):
            execute(f'/drop_all {self.username}')
            bot.send_message(f'{msg.sender.name} разгрузил инвентарь')

        # nopep8 /c remote.call("space-exploration", "begin_meteor_shower", {target_entity = game.player, meteors = 10})
        # nopep8 /c remote.call("space-exploration", "begin_meteor_shower", {target_entity = game.player.selected or game.player})
        # nopep8 /c remote.call("space-exploration", "begin_meteor_shower", {zone_name = "Nauvis", position = {x = 0, y = 0}, range = 1, meteors = 100})
        # nopep8 /c for i = 1, 10 do remote.call("space-exploration", "begin_meteor_shower", {target_entity = game.player, meteors = 100}) end
        @command('shower', aliases=['душ'], mana=7500, elixir=150, module='factorio')
        def shower_command(msg: ChatMessage, bot: ChatBot):
            execute(f'/ca player = game.get_player("{self.username}")'
                    'for i = 1, 5 do '
                    'remote.call("space-exploration", "begin_meteor_shower", '
                    '{target_entity = player, meteors = 5, range = 100}) '
                    'end')
            bot.send_message(f'{msg.sender.name} запустил метеоритный дождь')

