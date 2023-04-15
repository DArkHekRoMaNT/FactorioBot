import enum
from dataclasses import dataclass


class TrovoChatMessageType(enum.Enum):
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


class ChannelUserRole(enum.Enum):
    STREAMER = 100000     # Streamer of the current channel
    MOD = 100001          # Moderator of the current channel
    EDITOR = 100002       # Editor of the current channel
    SUB = 100004          # User who subscribed the current channel
    SUPER_MOD = 100005    # Super moderator of the current channel
    FOLLOWER = 100006     # User who followed of the current channel
    CUSTOM_ROLE = 200000  # User who have a role customized by the streamer of the current channel
    ACE = 300000          # Primary tier of Trovo membership
    ACE_PREMIUM = 300001  # Premium tier of Trovo membership
    ADMIN = 500000        # Admin of Trovo platform, across all channels
    WARDEN = 500001       # Warden of Trovo platform, across all channels, who helps to maintain the platform order


@dataclass
class TrovoChatMessage:
    type: TrovoChatMessageType
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
    def from_dict(obj: dict) -> 'TrovoChatMessage':
        _type = TrovoChatMessageType(obj.get('type'))
        _content = str(obj.get('content'))
        _nick_name = str(obj.get('nick_name'))
        _avatar = str(obj.get('avatar'))
        _sub_tier = int(obj.get('sub_tier', -1))
        _medals = list(obj.get('medals', []))
        _roles = list(obj.get('roles', []))
        _message_id = str(obj.get('message_id'))
        _sender_id = int(obj.get('sender_id', 0))
        _send_time = int(obj.get('send_time', 0))

        return TrovoChatMessage(_type, _content, _nick_name, _avatar, _sub_tier, _medals, _roles,
                                _message_id, _sender_id, _send_time)
