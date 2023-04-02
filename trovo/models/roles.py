import enum


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
