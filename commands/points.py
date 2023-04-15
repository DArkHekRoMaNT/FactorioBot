import db
from commands import command
from models import PointsType, ChatBot, ChatMessage


@command('addmp', owner_only=True)
def add_mp_command(msg: ChatMessage, bot: ChatBot):
    args = msg.text.split()
    if len(args) > 2:
        user = db.find_user(args[1].removeprefix('@'))
        quantity = int(args[2])
        db.add_points(user, quantity, PointsType.Mana, bot=bot)


@command('addep', owner_only=True)
def add_ep_command(msg: ChatMessage, bot: ChatBot):
    args = msg.text.split()
    if len(args) > 2:
        user = db.find_user(args[1].removeprefix('@'))
        quantity = int(args[2])
        db.add_points(user, quantity, PointsType.Elixir, bot=bot)


@command('points', aliases=['p', 'очки'])
def points_command(msg: ChatMessage, bot: ChatBot):
    username = None

    if msg.roles.__contains__('streamer'):
        args = msg.text.split()
        if len(args) > 1:
            username = args[1]
            username = username.removeprefix('@')

    if username:
        user = db.find_user(username)
    else:
        user = msg.sender

    if user:
        bot.send_message(f"{user.name}: {user.mana} mp, {user.elixir} ep")
    else:
        bot.send_message(f"{username}: {0} mp, {0} ep")
