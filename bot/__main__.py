import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import load_settings
from bot.middlewares import SettingsMiddleware
from bot.routers import register_routers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


async def main() -> None:
    settings = load_settings()
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.update.middleware(SettingsMiddleware(settings))

    register_routers(dispatcher)

    bot = Bot(
        settings.bot_token,
        default=DefaultBotProperties(),
    )
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
