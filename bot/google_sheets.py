"""Google Sheets o‘qish va Excel (.xlsx) ga eksport."""

from __future__ import annotations

import json
import logging
from io import BytesIO
from typing import Any

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openpyxl import Workbook

log = logging.getLogger(__name__)

SCOPES = ("https://www.googleapis.com/auth/spreadsheets",)


def _service(credentials_path: str):
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def fetch_values(credentials_path: str, spreadsheet_id: str, range_a1: str) -> list[list[Any]]:
    """Jadvaldan qiymatlarni o‘qish (sinxron). asyncio.to_thread orqali chaqiring."""
    svc = _service(credentials_path)
    result = (
        svc.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_a1)
        .execute()
    )
    return result.get("values", [])


def _http_error_detail(exc: HttpError) -> str:
    try:
        payload = json.loads(exc.content.decode("utf-8"))
        return str(payload.get("error", {}).get("message", ""))
    except Exception:
        return str(exc)


def user_message_for_sheets_error(exc: Exception) -> str:
    """Telegram foydalanuvchisiga tushunarli xabar (keng tarqalgan API xatolari)."""
    if isinstance(exc, HttpError):
        status = exc.resp.status if exc.resp else 0
        detail = _http_error_detail(exc)
        log.warning("Google Sheets API: status=%s detail=%s", status, detail)

        if status == 403:
            return (
                "Jadvalga ruxsat yo‘q. Google Sheetsda «Ulashish» → JSON kalitdagi "
                "service account emailini qo‘shing (kamida «Ko‘rish» / Viewer)."
            )
        if status == 404:
            return (
                "Jadval topilmadi: GOOGLE_SPREADSHEET_ID noto‘g‘ri yoki fayl "
                "boshqa akkauntga tegishli."
            )
        if status == 400:
            return (
                "Jadval oralig‘i yoki varaq nomi noto‘g‘ri. .env da "
                "GOOGLE_SHEETS_EXPORT_RANGE ni Google Sheetsdagi varaq nomiga "
                "moslang (masalan: «Лист1!A:ZZ» yoki «Data!A1:Z»)."
            )
        log.warning("Google Sheets API: boshqa HTTP xato status=%s", status)
        return (
            "Jadvalni yuklab bo‘lmadi. Keyinroq urinib ko‘ring yoki "
            "administrator bilan bog‘laning."
        )
    log.exception("Google Sheets: kutilmagan xato")
    return (
        "Jadvalni yuklab bo‘lmadi. Keyinroq urinib ko‘ring yoki "
        "administrator bilan bog‘laning."
    )


def rows_to_xlsx_bytes(
    rows: list[list[Any]],
    *,
    worksheet_name: str = "Yuk",
) -> bytes:
    """2D qatorlardan .xlsx fayl baytlari."""
    wb = Workbook()
    ws = wb.active
    ws.title = (worksheet_name or "Sheet")[:31]

    for ri, row in enumerate(rows, start=1):
        for ci, val in enumerate(row, start=1):
            ws.cell(row=ri, column=ci, value="" if val is None else val)

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
