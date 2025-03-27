from aiogram import Bot, Dispatcher
import asyncio
import os
from dotenv import load_dotenv
from loguru import logger


from app.user import user

load_dotenv()

async def main():
    bot = Bot(token=os.getenv('TG_TOKEN'))
    dp = Dispatcher()
    dp.include_router(user)
    logger.info('Starting TG_bot polling.')
    await dp.start_polling(bot)
    
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exited by keyboard interrupt")