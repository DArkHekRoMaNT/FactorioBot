import asyncio
import os

from dotenv import load_dotenv

import commands
import db
from logger import setup_logger
from services.donation_alerts import DonationAlerts
from services.factorio import FactorioBot
from services.trovo import TrovoChat
from services.twitch import TwitchBot


async def main():
    load_dotenv()
    setup_logger()

    db.init()
    db.backup()

    trovo_bot = TrovoChat(
        os.getenv('TROVO_CLIENT_ID'),
        os.getenv('TROVO_CLIENT_SECRET'),
        os.getenv('TROVO_REDIRECT_URL')
    )

    twitch_bot = TwitchBot(
        os.getenv('TWITCH_CLIENT_ID'),
        os.getenv('TWITCH_CLIENT_SECRET'),
        os.getenv('TWITCH_REDIRECT_URL'),
        os.getenv('TWITCH_CHANNEL_NAME')
    )

    factorio_bot = FactorioBot(
        os.getenv('FACTORIO_RCON_HOST'),
        int(os.getenv('FACTORIO_RCON_PORT')),
        os.getenv('FACTORIO_RCON_PASS'),
        os.getenv('FACTORIO_USERNAME')
    )
    factorio_bot.start()
    commands.enable_module('factorio')

    donation_alerts = DonationAlerts(os.getenv('DA_TOKEN'), trovo_bot)

    tasks = [
        asyncio.create_task(trovo_bot.run()),
        asyncio.create_task(twitch_bot.run()),
        asyncio.create_task(donation_alerts.run())
    ]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
