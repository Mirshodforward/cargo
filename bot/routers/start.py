import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, Message

from bot.config import Settings
from bot.google_sheets import fetch_values, rows_to_xlsx_bytes, user_message_for_sheets_error

router = Router(name="start")
log = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, settings: Settings) -> None:
    try:
        rows = await asyncio.to_thread(
            fetch_values,
            settings.google_sheets_credentials_path,
            settings.google_spreadsheet_id,
            settings.google_sheets_export_range,
        )
    except Exception as e:
        await message.answer(user_message_for_sheets_error(e))
        return

    try:
        xlsx = await asyncio.to_thread(rows_to_xlsx_bytes, rows)
    except Exception:
        log.exception("Excel yaratishda xato")
        await message.answer("Excel faylini tayyorlashda xatolik yuz berdi.")
        return

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"yuk_royxati_{stamp}.xlsx"
    await message.answer_document(
        BufferedInputFile(xlsx, filename=filename),
        caption="Google Sheetsdagi yuk ro‘yxati (Excel).",
    )
