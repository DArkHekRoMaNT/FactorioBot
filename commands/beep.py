import sys

from commands import command
from models import ChatMessage, ChatBot


@command('beep')
def beep_command(msg: ChatMessage, bot: ChatBot):
    if sys.platform == "win32":
        import winsound
        winsound.Beep(frequency=800, duration=200)
    else:
        print('\a')
