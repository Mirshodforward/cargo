import asyncio
import logging
import re
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from bot.config import Settings
from bot.google_sheets import (
    build_kod_export_with_totals,
    fetch_values,
    lookup_unique_kods_by_number,
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
from bot.phone_utils import normalize_phone_digits
from bot.pdf_export import rows_to_pdf_bytes

router = Router(name="start")
log = logging.getLogger(__name__)


class UserStates(StatesGroup):
    choosing_language = State()
    waiting_contact = State()
    waiting_kod = State()


BTN_RU = "Русский язык 🇷🇺"
BTN_EN = "English language 🇬🇧"
BTN_ZH = "中文 🇨🇳"
BTN_UZ = "O'zbek tili 🇺🇿"
BTN_TR = "Türkçe 🇹🇷"

_REPLY_TEXT_TO_LANG: dict[str, str] = {
    BTN_RU: LANG_RU,
    BTN_EN: LANG_EN,
    BTN_ZH: LANG_ZH,
    BTN_UZ: LANG_UZ,
    BTN_TR: LANG_TR,
}


def _language_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_RU), KeyboardButton(text=BTN_EN)],
            [KeyboardButton(text=BTN_ZH), KeyboardButton(text=BTN_UZ)],
            [KeyboardButton(text=BTN_TR)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Til / Language",
    )


def _contact_reply_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=t(lang, "contact_share_btn"),
                    request_contact=True,
                )
            ],
        ],
        resize_keyboard=True,
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(UserStates.choosing_language)
    await message.answer(
        t(LANG_EN, "welcome"),
        reply_markup=_language_reply_keyboard(),
    )


@router.message(UserStates.choosing_language, F.text)
async def on_language_reply(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    lang = _REPLY_TEXT_TO_LANG.get(raw)
    if not lang:
        await message.answer(t(LANG_EN, "pick_language_button"))
        return
    await state.update_data(lang=lang)
    await state.set_state(UserStates.waiting_contact)
    await message.answer(
        t(lang, "share_contact"),
        reply_markup=_contact_reply_keyboard(lang),
    )


@router.message(UserStates.waiting_contact, F.contact)
async def on_contact_shared(message: Message, state: FSMContext, settings: Settings) -> None:
    data = await state.get_data()
    lang = data.get("lang") or LANG_EN
    contact = message.contact
    if not contact or not contact.phone_number:
        await message.answer(t(lang, "contact_invalid"))
        return
    digits = normalize_phone_digits(contact.phone_number)
    if not digits:
        await message.answer(t(lang, "contact_invalid"))
        return

    loading = await message.answer("⏳")
    try:
        rows = await asyncio.to_thread(
            fetch_values,
            settings.google_spreadsheet_id,
            settings.google_sheets_lookup_range,
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

    kods = await asyncio.to_thread(
        lookup_unique_kods_by_number,
        rows,
        digits,
        number_header=settings.google_sheets_number_header,
        kod_header=settings.google_sheets_kod_header,
        header_row_count=settings.google_sheets_header_rows,
    )
    try:
        await loading.delete()
    except Exception:
        pass

    if not kods:
        await message.answer(
            t(lang, "customer_not_found"),
            reply_markup=_contact_reply_keyboard(lang),
        )
        return

    codes_block = "\n".join(f"• {k}" for k in kods)
    await state.update_data(allowed_kods=tuple(kods))
    await state.set_state(UserStates.waiting_kod)
    await message.answer(
        t(lang, "customer_found_codes", codes=codes_block),
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(t(lang, "enter_code"))


@router.message(UserStates.waiting_contact, F.text)
async def on_waiting_contact_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang") or LANG_EN
    await message.answer(t(lang, "contact_text_only"))


@router.message(UserStates.waiting_kod, F.text, ~F.text.startswith("/"))
async def on_kod_message(message: Message, state: FSMContext, settings: Settings) -> None:
    data = await state.get_data()
    lang = data.get("lang") or LANG_EN
    allowed = data.get("allowed_kods")
    if not isinstance(allowed, tuple) or not allowed:
        await message.answer(t(lang, "need_start"))
        return

    kod = (message.text or "").strip()
    if not kod:
        return
    if kod not in allowed:
        await message.answer(t(lang, "kod_not_in_list"))
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
