import logging

from models import ChatMessage, ChatBot

_log = logging.getLogger(__name__)

command_prefix = '!'
commands = []


def command(name: str, *, aliases=None, owner_only=False, roles_required=None):
    if aliases is None:
        aliases = []

    def decorator(func):
        def can_execute(msg: ChatMessage) -> bool:
            if owner_only:
                return msg.roles.__contains__('streamer')

            if roles_required is not None:
                for role in roles_required:
                    if msg.roles.__contains__(role):
                        return True
                return False

            return True

        def wrapper(msg: ChatMessage, bot: ChatBot):
            prefix = msg.text.split(maxsplit=1)[0]

            if any([cmd for cmd in [*aliases, name] if prefix == command_prefix + cmd]):
                if can_execute(msg):
                    _log.debug(f'Trigger command "{name}": {msg.text} by {msg.sender.name}')
                    try:
                        return func(msg, bot)
                    except Exception as e:
                        _log.error(e)
                else:
                    _log.debug(f'Reject command "{name}": {msg.text} by {msg.sender.name} (no privileges)')

        wrapper.can_execute = can_execute
        wrapper.help_text = command_prefix + name
        wrapper.name = name
        commands.append(wrapper)
        return wrapper
    return decorator


@command('help', aliases=['помощь'])
def help_command(msg: ChatMessage, bot: ChatBot):
    help_text = []
    for cmd in commands:
        if cmd.can_execute(msg):
            help_text.append(cmd.help_text)

    if len(help_text) == 0:
        bot.send_message('No available commands')
    else:
        bot.send_message('\u200c' + ' '.join(help_text))  # add zero-width space first for prevent loop


def trigger_commands(msg: ChatMessage, bot: ChatBot):
    for cmd in commands:
        try:
            cmd(msg, bot)
        except Exception as e:
            _log.warning(f'Trigger command {cmd.name} by {msg.sender.name} is failed: {e}')
