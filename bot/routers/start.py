import asyncio
import logging
import re
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, Message

from bot.config import Settings
from bot.google_sheets import (
    build_kod_export_with_totals,
    fetch_values,
    user_message_for_sheets_error,
)
from bot.pdf_export import rows_to_pdf_bytes

router = Router(name="start")
log = logging.getLogger(__name__)

HELP_TEXT = (
    "Assalomu alaykum! Xush kelibsiz.\n\n"
    "Iltimos, KOD raqamingizni kiriting!"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(F.text, ~F.text.startswith("/"))
async def on_kod_message(message: Message, settings: Settings) -> None:
    kod = (message.text or "").strip()
    if not kod:
        return

    loading_msg = await message.answer("⏳")

    async def clear_loading() -> None:
        try:
            await loading_msg.delete()
        except Exception:
            pass

    try:
        rows = await asyncio.to_thread(
            fetch_values,
            settings.google_sheets_credentials_path,
            settings.google_spreadsheet_id,
            settings.google_sheets_export_range,
        )
    except Exception as e:
        await clear_loading()
        await message.answer(user_message_for_sheets_error(e))
        return

    table, err = build_kod_export_with_totals(
        rows,
        kod,
        kod_header=settings.google_sheets_kod_header,
        header_row_count=settings.google_sheets_header_rows,
        sum_column_labels=settings.google_sheets_sum_columns,
        totals_text=settings.google_sheets_totals_text,
        totals_text_column_label=settings.google_sheets_totals_text_column,
    )
    if err or table is None:
        await clear_loading()
        await message.answer(err or "Noma’lum xato.")
        return

    hdr = settings.google_sheets_header_rows
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    safe = re.sub(r'[<>:"/\\|?*]', "_", kod)[:60]
    filename_pdf = f"kod_{safe}_{stamp}.pdf"

    try:
        pdf = await asyncio.to_thread(
            rows_to_pdf_bytes,
            table,
            header_row_count=hdr,
            title="",
        )
    except Exception:
        log.exception("PDF yaratishda xato")
        await clear_loading()
        await message.answer("PDF tayyorlashda xatolik yuz berdi.")
        return

    await clear_loading()

    await message.answer_document(
        BufferedInputFile(pdf, filename=filename_pdf),
        reply_to_message_id=message.message_id,
    )
