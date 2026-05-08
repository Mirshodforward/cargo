"""Route registration."""

from aiogram import Dispatcher

from bot.routers import start


def register_routers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
