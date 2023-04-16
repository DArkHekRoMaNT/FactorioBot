import asyncio
import os

from dotenv import load_dotenv

import db
from donation_alerts import DonationAlertsService
from logger import setup_logger
from trovo import TrovoChat


async def trovo_loop():
    bot = TrovoChat(
        os.getenv('TROVO_CLIENT_ID'),
        os.getenv('TROVO_CLIENT_SECRET'),
        os.getenv('TROVO_MY_CHANNEL_ID'),
        'http://localhost:8000'
    )

    while True:
        await bot.run()
        await asyncio.sleep(3)


async def donation_alerts_loop():
    da = DonationAlertsService(
        os.getenv('DA_CLIENT_ID'),
        os.getenv('DA_CLIENT_SECRET'),
        'http://localhost:8000'
    )

    while True:
        await da.run()
        await asyncio.sleep(3)


async def main():
    load_dotenv()
    setup_logger()

    db.init()
    db.backup()

    tasks = [
        asyncio.create_task(trovo_loop()),
        asyncio.create_task(donation_alerts_loop())
    ]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
