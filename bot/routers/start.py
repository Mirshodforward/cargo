import asyncio
import logging
import re
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import CommandStart
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

ALL_LANGS = (LANG_RU, LANG_EN, LANG_UZ, LANG_ZH, LANG_TR)


class UserStates(StatesGroup):
    choosing_language = State()
    waiting_contact = State()
    waiting_kod = State()
    waiting_status_filter = State()


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


def _kod_choice_keyboard(kods: tuple[str, ...]) -> ReplyKeyboardMarkup:
    """Har bir KOD alohida tugma; qatorlarda 2 tadan."""
    keyboard: list[list[KeyboardButton]] = []
    lst = list(kods)
    for i in range(0, len(lst), 2):
        row = [KeyboardButton(text=lst[i])]
        if i + 1 < len(lst):
            row.append(KeyboardButton(text=lst[i + 1]))
        keyboard.append(row)
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Kod",
    )


def _status_filter_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t(lang, "status_filter_btn_in_transit")),
                KeyboardButton(text=t(lang, "status_filter_btn_arrived")),
            ],
            [KeyboardButton(text=t(lang, "status_filter_btn_picked_up"))],
        ],
        resize_keyboard=True,
    )


def _status_filter_id_from_button_text(text: str) -> str | None:
    raw = (text or "").strip()
    for code in ALL_LANGS:
        if raw == t(code, "status_filter_btn_in_transit"):
            return "in_transit"
        if raw == t(code, "status_filter_btn_arrived"):
            return "arrived"
        if raw == t(code, "status_filter_btn_picked_up"):
            return "picked_up"
    return None


async def _build_and_send_kod_pdf(
    message: Message,
    state: FSMContext,
    settings: Settings,
    *,
    lang: str,
    kod: str,
    status_filter: str,
) -> None:
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

    table, err, eff_h = build_kod_export_with_totals(
        rows,
        kod,
        kod_header=settings.google_sheets_kod_header,
        header_row_count=settings.google_sheets_header_rows,
        sum_column_labels=settings.google_sheets_sum_columns,
        totals_text=settings.google_sheets_totals_text,
        totals_text_column_label=settings.google_sheets_totals_text_column,
        status_filter=status_filter,
    )
    if err or table is None:
        await clear_loading()
        msg = localize_table_error(err, lang) if err else t(lang, "unknown_error")
        await message.answer(msg)
        return

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    when_human = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    safe = re.sub(r'[<>:"/\\|?*]', "_", kod)[:60]
    filename_pdf = f"kod_{safe}_{status_filter}_{stamp}.pdf"

    line_code = t(lang, "pdf_line_code", code=kod)
    if status_filter == "in_transit":
        line_code = line_code + "\n" + t(lang, "pdf_line_status_in_transit")
    elif status_filter == "arrived":
        line_code = line_code + "\n" + t(lang, "pdf_line_status_arrived")
    elif status_filter == "picked_up":
        line_code = line_code + "\n" + t(lang, "pdf_line_status_picked_up")

    try:
        pdf = await asyncio.to_thread(
            rows_to_pdf_bytes,
            table,
            header_row_count=eff_h,
            header_title=t(lang, "pdf_header_title"),
            header_code_line=line_code,
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
        reply_markup=ReplyKeyboardRemove(),
    )

    data = await state.get_data()
    allowed = data.get("allowed_kods")
    if isinstance(allowed, tuple) and allowed:
        await state.set_state(UserStates.waiting_kod)
        await message.answer(
            t(lang, "pdf_sent_pick_again"),
            reply_markup=_kod_choice_keyboard(allowed),
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

    allowed = tuple(kods)
    await state.update_data(allowed_kods=allowed)
    await state.set_state(UserStates.waiting_kod)
    await message.answer(
        t(lang, "customer_found_codes"),
        reply_markup=_kod_choice_keyboard(allowed),
    )


@router.message(UserStates.waiting_contact, F.text)
async def on_waiting_contact_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang") or LANG_EN
    await message.answer(t(lang, "contact_text_only"))


@router.message(UserStates.waiting_kod, F.text, ~F.text.startswith("/"))
async def on_kod_message(message: Message, state: FSMContext) -> None:
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

    await state.update_data(pending_kod=kod)
    await state.set_state(UserStates.waiting_status_filter)
    await message.answer(
        t(lang, "pick_status_filter"),
        reply_markup=_status_filter_keyboard(lang),
    )


@router.message(UserStates.waiting_status_filter, F.text, ~F.text.startswith("/"))
async def on_status_filter_choice(message: Message, state: FSMContext, settings: Settings) -> None:
    data = await state.get_data()
    lang = data.get("lang") or LANG_EN
    kod = data.get("pending_kod")
    if not isinstance(kod, str) or not kod.strip():
        await message.answer(t(lang, "need_start"))
        return

    fid = _status_filter_id_from_button_text(message.text or "")
    if not fid:
        await message.answer(t(lang, "status_filter_buttons_only"))
        return

    await _build_and_send_kod_pdf(
        message,
        state,
        settings,
        lang=lang,
        kod=kod.strip(),
        status_filter=fid,
    )


@router.message(UserStates.waiting_status_filter, F.contact)
async def on_status_filter_contact_instead(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang") or LANG_EN
    await message.answer(t(lang, "status_filter_buttons_only"))

