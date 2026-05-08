import asyncio
import logging
import re
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.config import Settings
from bot.google_sheets import (
    build_kod_export_with_totals,
    fetch_values,
)
from bot.i18n import (
    LANG_EN,
    LANG_RU,
    LANG_TR,
    LANG_UZ,
    LANG_ZH,
    localize_table_error,
    sheets_http_message,
    t,
)
from bot.pdf_export import rows_to_pdf_bytes

router = Router(name="start")
log = logging.getLogger(__name__)

_LANG_ORDER = (LANG_RU, LANG_EN, LANG_ZH, LANG_UZ, LANG_TR)


def _language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Русский язык 🇷🇺", callback_data="set_lang:ru"
                ),
                InlineKeyboardButton(
                    text="English language 🇬🇧", callback_data="set_lang:en"
                ),
            ],
            [
                InlineKeyboardButton(text="中文 🇨🇳", callback_data="set_lang:zh"),
                InlineKeyboardButton(
                    text="O'zbek tili 🇺🇿", callback_data="set_lang:uz"
                ),
            ],
            [
                InlineKeyboardButton(text="Türkçe 🇹🇷", callback_data="set_lang:tr"),
            ],
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        t(LANG_EN, "welcome"),
        reply_markup=_language_keyboard(),
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def on_language_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    lang = (callback.data or "").split(":", 1)[-1].strip().lower()
    if lang not in _LANG_ORDER:
        await callback.answer()
        return
    await state.update_data(lang=lang)
    await callback.answer()
    msg = callback.message
    if isinstance(msg, Message):
        try:
            await msg.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await msg.answer(t(lang, "enter_code"))


@router.message(F.text, ~F.text.startswith("/"))
async def on_kod_message(message: Message, state: FSMContext, settings: Settings) -> None:
    data = await state.get_data()
    lang = data.get("lang")
    if not lang:
        await message.answer(t(None, "need_start"))
        return

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
            settings.google_spreadsheet_id,
            settings.google_sheets_export_range,
            credentials_path=settings.google_sheets_credentials_path,
            service_account_info=settings.google_service_account_info,
        )
    except Exception as e:
        await clear_loading()
        await message.answer(sheets_http_message(e, lang))
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
        msg = localize_table_error(err, lang) if err else t(lang, "unknown_error")
        await message.answer(msg)
        return

    hdr = settings.google_sheets_header_rows
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    when_human = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    safe = re.sub(r'[<>:"/\\|?*]', "_", kod)[:60]
    filename_pdf = f"kod_{safe}_{stamp}.pdf"

    try:
        pdf = await asyncio.to_thread(
            rows_to_pdf_bytes,
            table,
            header_row_count=hdr,
            header_title=t(lang, "pdf_header_title"),
            header_code_line=t(lang, "pdf_line_code", code=kod),
            footer_line=t(lang, "pdf_footer_generated", when=when_human),
        )
    except Exception:
        log.exception("PDF yaratishda xato")
        await clear_loading()
        await message.answer(t(lang, "pdf_error"))
        return

    await clear_loading()

    await message.answer_document(
        BufferedInputFile(pdf, filename=filename_pdf),
        reply_to_message_id=message.message_id,
    )
