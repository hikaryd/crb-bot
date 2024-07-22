import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers import exchange_router
from bot.services.redis import RedisService

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(exchange_router)


async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="/exchange", description="Просмотр стоимости обмена"),
        BotCommand(command="/rates", description="Просмотров курсов валют"),
    ]
    await bot.set_my_commands(commands)


async def on_startup():
    await RedisService.create()
    await set_default_commands(bot)


async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
