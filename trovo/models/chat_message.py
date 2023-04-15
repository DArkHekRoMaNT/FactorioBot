import enum
from dataclasses import dataclass


class ChatMessageType(enum.Enum):
    NORMAL_CHAT = 0                        # Normal chat messages
    SPELLS = 5                             # Spells, including: mana spells, elixir spells
    MAGIC_CHAT_SUPER_CAP = 6               # Magic chat - super cap chat
    MAGIC_CHAT_COLORFUL = 7                # Magic chat - colorful chat
    MAGIC_CHAT_SPELL = 8                   # Magic chat - spell chat
    MAGIC_CHAT_BULLET_SCREEN = 9           # Magic chat - bullet screen chat
    SUBSCRIPTION_MESSAGE = 5001            # Subscription message. Shows when someone subscribes to the channel
    SYSTEM_MESSAGE = 5002                  # System message
    FOLLOW_MESSAGE = 5003                  # Follow message
    WELCOME_MESSAGE = 5004                 # Welcome message when viewer joins the channel
    RANDOMLY_GIFT_SUB_MESSAGE = 5005       # Gift sub message (randomly)
    DETAILED_GIFT_SUB_MESSAGE = 5006       # Gift sub message (for selected user)
    ACTIVITY_EVENTS_MESSAGE = 5007         # Activity / events message. For platform level events
    WELCOME_MESSAGE_FROM_RAID = 5008       # Welcome message when users join the channel from raid
    CUSTOM_SPELLS = 5009                   # Custom Spells
    STREAM_ON_OFF_MESSAGES = 5012          # Stream on/off messages, invisible to the viewers
    UNFOLLOW_MESSAGE = 5013                # Unfollow message


@dataclass
class ChatMessage:
    type: ChatMessageType
    content: str
    nick_name: str
    avatar: str
    sub_tier: int
    medals: list
    roles: list
    message_id: str
    sender_id: int
    send_time: int

    @staticmethod
    def from_dict(obj: dict) -> 'ChatMessage':
        _type = ChatMessageType(obj.get('type'))
        _content = str(obj.get('content'))
        _nick_name = str(obj.get('nick_name'))
        _avatar = str(obj.get('avatar'))
        _sub_tier = int(obj.get('sub_tier', -1))
        _medals = list(obj.get('medals', []))
        _roles = list(obj.get('roles', []))
        _message_id = str(obj.get('message_id'))
        _sender_id = int(obj.get('sender_id', 0))
        _send_time = int(obj.get('send_time', 0))

        return ChatMessage(_type, _content, _nick_name, _avatar, _sub_tier, _medals, _roles,
                           _message_id, _sender_id, _send_time)
