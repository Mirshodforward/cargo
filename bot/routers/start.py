import asyncio
import logging
import re
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, InputMediaDocument, Message

from bot.config import Settings
from bot.google_sheets import (
    build_kod_export_with_totals,
    fetch_values,
    rows_to_xlsx_bytes,
    user_message_for_sheets_error,
)
from bot.pdf_export import rows_to_pdf_bytes

router = Router(name="start")
log = logging.getLogger(__name__)

HELP_TEXT = (
    "Salom!\n\n"
    "KOD ni yuboring — shu kod bo‘yicha qatorlar: bir xil jadval "
    "Excel (.xlsx) va chiroyli PDF ko‘rinishida yuboriladi "
    "(«KOD» ustuni ikkala faylda ham chiqmaydi).\n"
    "Oxirida «umumiy» qatori: Paket soni, Og‘irlik, Hajm, Summa yig‘indilari "
    "(Qabul sana ustunida yozuv).\n\n"
    "Ko‘p qatorli sarlavha bo‘lsa GOOGLE_SHEETS_HEADER_ROWS ni sozlang."
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(F.text, ~F.text.startswith("/"))
async def on_kod_message(message: Message, settings: Settings) -> None:
    kod = (message.text or "").strip()
    if not kod:
        return

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
        await message.answer(err or "Noma’lum xato.")
        return

    hdr = settings.google_sheets_header_rows
    data_rows = max(0, len(table) - hdr - 1)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    safe = re.sub(r'[<>:"/\\|?*]', "_", kod)[:60]
    filename_xlsx = f"kod_{safe}_{stamp}.xlsx"
    filename_pdf = f"kod_{safe}_{stamp}.pdf"

    try:
        xlsx, pdf = await asyncio.gather(
            asyncio.to_thread(rows_to_xlsx_bytes, table),
            asyncio.to_thread(
                rows_to_pdf_bytes,
                table,
                header_row_count=hdr,
                title=f"KOD: {kod}",
            ),
        )
    except Exception:
        log.exception("Excel yoki PDF yaratishda xato")
        await message.answer("Fayllarni tayyorlashda xatolik yuz berdi.")
        return

    caption = (
        f"KOD: {kod} — {data_rows} ta qator + {hdr} sarlavha + umumiy qator. "
        "Excel va PDF."
    )
    await message.bot.send_media_group(
        message.chat.id,
        media=[
            InputMediaDocument(
                media=BufferedInputFile(xlsx, filename=filename_xlsx),
                caption=caption,
            ),
            InputMediaDocument(
                media=BufferedInputFile(pdf, filename=filename_pdf),
            ),
        ],
        reply_to_message_id=message.message_id,
    )
