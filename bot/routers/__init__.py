"""Route registration."""

from aiogram import Dispatcher

from bot.routers import list_excel, start


def register_routers(dp: Dispatcher) -> None:
    dp.include_router(list_excel.router)
    dp.include_router(start.router)
