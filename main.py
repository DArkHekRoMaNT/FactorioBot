import asyncio
import os

from dotenv import load_dotenv

import db
from logger import setup_logger
from trovo import bot


async def main():
    load_dotenv()
    setup_logger()
    db.backup()
    trovo = bot.create(
        os.getenv('TROVO_CLIENT_ID'),
        os.getenv('TROVO_CLIENT_SECRET'),
        os.getenv('TROVO_MY_CHANNEL_ID')
    )
    while True:
        await trovo.run()
        await asyncio.sleep(3)

if __name__ == '__main__':
    asyncio.run(main())
