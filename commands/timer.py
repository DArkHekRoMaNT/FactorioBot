import logging
import time
from threading import Thread, Timer

import db
from commands import command
from models import ChatMessage, ChatBot

_log = logging.getLogger(__name__)


class Countdown:
    target_time = 0
    thread: Thread = None

    def start(self, seconds: float):
        self.target_time = time.time() + seconds

        if not self.thread:
            self.thread = Thread(target=self._loop)
            self.thread.start()

    def _loop(self):
        while True:
            seconds = self.target_time - time.time()
            if seconds < -5:
                return

            if seconds > 0:
                m, s = divmod(int(seconds), 60)
            else:
                m, s = 0, 0

            db.save('timer.txt', '{:02d}:{:02d}'.format(m, s))
            time.sleep(0.5)


_timer = Countdown()
db.save('timer.txt', '')


@command('timer', owner_only=True)
def timer_command(msg: ChatMessage, bot: ChatBot):
    args = msg.text.split()
    if len(args) < 2:
        return

    seconds = float(args[1])
    _timer.start(seconds)
    _log.debug(f'Run countdown timer on {seconds} sec')
