import logging

from .models import ChatMessage, ChatMessageType

_log = logging.getLogger(__name__)

command_prefix = '!'
commands = []


def command(name: str, *, aliases=None, owner_only=False, sub_tier_required=-1, roles_required=None):
    if aliases is None:
        aliases = []

    def decorator(func):
        def can_execute(msg: ChatMessage, bot: 'TrovoChat') -> bool:
            if owner_only:
                return msg.roles.__contains__('streamer')

            if sub_tier_required != -1:
                return sub_tier_required >= msg.sub_tier

            if roles_required is not None:
                for role in roles_required:
                    if msg.roles.__contains__(role):
                        return True
                return False

            return True

        def wrapper(msg: ChatMessage, bot: 'TrovoChat'):
            def is_this_command():
                for cmd in [*aliases, name]:
                    if msg.content.startswith(command_prefix + cmd):
                        return True
                return False

            if msg.type == ChatMessageType.NORMAL_CHAT and is_this_command():
                if can_execute(msg, bot):
                    _log.debug(f'Trigger command "{name}": {msg.content} by {msg.nick_name}')
                    try:
                        return func(msg, bot)
                    except Exception as e:
                        _log.error(e)
                else:
                    _log.debug(f'Reject command "{name}": {msg.content} by {msg.nick_name} (no privileges)')

        wrapper.can_execute = can_execute
        wrapper.help_text = command_prefix + name
        wrapper.name = name
        commands.append(wrapper)
        return wrapper
    return decorator


@command('help', aliases=['h', 'помощь'])
def help_command(msg: ChatMessage, bot: 'TrovoChat'):
    help_text = []
    for cmd in commands:
        if cmd.can_execute(msg, bot):
            help_text.append(cmd.help_text)

    if len(help_text) == 0:
        bot.send_message('No available commands')
    else:
        bot.send_message('\u200c' + ' '.join(help_text))  # add zero-width space first for prevent loop
