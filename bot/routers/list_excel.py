"""``/list`` — jadvalning barcha varaqlarini .xlsx sifatida yuklash."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from bot.config import Settings
from bot.google_sheets import full_spreadsheet_to_xlsx_bytes
from bot.i18n import LANG_EN, LANG_RU, LANG_TR, LANG_UZ, LANG_ZH, sheets_http_message, t

router = Router(name="list_excel")
log = logging.getLogger(__name__)


def _lang_from_telegram(message: Message) -> str:
    code = (message.from_user.language_code if message.from_user else None) or "en"
    code = code.lower()
    if code.startswith("ru"):
        return LANG_RU
    if code.startswith("uz"):
        return LANG_UZ
    if code.startswith("zh"):
        return LANG_ZH
    if code.startswith("tr"):
        return LANG_TR
    return LANG_EN


@router.message(Command("list"))
async def cmd_list(message: Message, settings: Settings) -> None:
    lang = _lang_from_telegram(message)
    loading = await message.answer(t(lang, "list_exporting"))
    try:
        data = await asyncio.to_thread(
            full_spreadsheet_to_xlsx_bytes,
            settings.google_spreadsheet_id,
            cell_range=settings.google_sheets_list_cell_range,
            credentials_path=settings.google_sheets_credentials_path,
            service_account_info=settings.google_service_account_info,
        )
    except Exception as e:
        try:
            await loading.delete()
        except Exception:
            pass
        await message.answer(sheets_http_message(e, lang))
        return

    try:
        await loading.delete()
    except Exception:
        pass

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    fname = f"cargo_sheets_{stamp}.xlsx"
    try:
        await message.answer_document(
            BufferedInputFile(data, filename=fname),
            caption=t(lang, "list_caption"),
        )
    except Exception:
        log.exception("/list: hujjat yuborishda xato (ehtimol fayl juda katta)")
        await message.answer(t(lang, "list_too_large"))
