import asyncio
import os

from dotenv import load_dotenv

import db
import donation_alerts
from logger import setup_logger
from trovo import TrovoChat


async def main():
    load_dotenv()
    setup_logger()

    db.init()
    db.backup()

    bot = TrovoChat(
        os.getenv('TROVO_CLIENT_ID'),
        os.getenv('TROVO_CLIENT_SECRET'),
        os.getenv('TROVO_MY_CHANNEL_ID'),
        'http://localhost:8000'
    )

    async def trovo_loop():
        while True:
            await bot.run()
            await asyncio.sleep(3)

    tasks = [
        asyncio.create_task(trovo_loop()),
        asyncio.create_task(donation_alerts.run(os.getenv('DA_TOKEN'), bot))
    ]

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
