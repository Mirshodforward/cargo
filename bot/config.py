import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _service_account_from_env() -> dict[str, Any] | None:
    """
    1) GOOGLE_SERVICE_ACCOUNT_JSON — butun JSON (bir qator, kalitdagi \\n saqlanadi)
    2) yoki GOOGLE_SA_* alohida o‘zgaruvchilar
    """
    blob = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if blob:
        try:
            data = json.loads(blob)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"GOOGLE_SERVICE_ACCOUNT_JSON noto‘g‘ri JSON: {e}") from e
        if not isinstance(data, dict):
            raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON — JSON obyekt bo‘lishi kerak")
        return data

    email = os.getenv("GOOGLE_SA_CLIENT_EMAIL", "").strip()
    pk = os.getenv("GOOGLE_SA_PRIVATE_KEY", "").strip().replace("\\n", "\n")
    project_id = os.getenv("GOOGLE_SA_PROJECT_ID", "").strip()
    private_key_id = os.getenv("GOOGLE_SA_PRIVATE_KEY_ID", "").strip()

    if email and pk and project_id and private_key_id:
        return {
            "type": os.getenv("GOOGLE_SA_TYPE", "service_account").strip(),
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": pk,
            "client_email": email,
            "client_id": os.getenv("GOOGLE_SA_CLIENT_ID", "").strip(),
            "auth_uri": os.getenv(
                "GOOGLE_SA_AUTH_URI",
                "https://accounts.google.com/o/oauth2/auth",
            ).strip(),
            "token_uri": os.getenv(
                "GOOGLE_SA_TOKEN_URI",
                "https://oauth2.googleapis.com/token",
            ).strip(),
            "auth_provider_x509_cert_url": os.getenv(
                "GOOGLE_SA_AUTH_PROVIDER_X509_CERT_URL",
                "https://www.googleapis.com/oauth2/v1/certs",
            ).strip(),
            "client_x509_cert_url": os.getenv(
                "GOOGLE_SA_CLIENT_X509_CERT_URL", ""
            ).strip(),
            "universe_domain": os.getenv(
                "GOOGLE_SA_UNIVERSE_DOMAIN", "googleapis.com"
            ).strip(),
        }

    if any((email, pk, project_id, private_key_id)):
        raise RuntimeError(
            "GOOGLE_SA_*: GOOGLE_SA_PROJECT_ID, GOOGLE_SA_PRIVATE_KEY_ID, "
            "GOOGLE_SA_CLIENT_EMAIL va GOOGLE_SA_PRIVATE_KEY birga berilishi kerak."
        )
    return None


@dataclass(frozen=True)
class Settings:
    bot_token: str
    google_sheets_credentials_path: str | None
    google_service_account_info: dict[str, Any] | None
    google_spreadsheet_id: str
    google_sheets_export_range: str
    google_sheets_lookup_range: str
    google_sheets_number_header: str
    google_sheets_kod_header: str
    google_sheets_header_rows: int
    google_sheets_sum_columns: tuple[str, ...]
    google_sheets_totals_text: str
    google_sheets_totals_text_column: str
    google_sheets_list_cell_range: str


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "").strip() or None
    sa_info = _service_account_from_env()
    sheet_id = os.getenv("GOOGLE_SPREADSHEET_ID", "").strip()
    export_range = os.getenv("GOOGLE_SHEETS_EXPORT_RANGE", "Sheet1").strip()
    lookup_range = os.getenv("GOOGLE_SHEETS_LOOKUP_RANGE", "yuk2!A:ZZ").strip()
    number_header = os.getenv("GOOGLE_SHEETS_NUMBER_HEADER", "NUMBER").strip() or "NUMBER"
    kod_header = os.getenv("GOOGLE_SHEETS_KOD_HEADER", "KOD").strip() or "KOD"

    raw_header_rows = os.getenv("GOOGLE_SHEETS_HEADER_ROWS", "1").strip()
    try:
        header_rows = max(1, int(raw_header_rows))
    except ValueError:
        header_rows = 1

    sum_raw = os.getenv(
        "GOOGLE_SHEETS_SUM_COLUMNS",
        "Paket soni,Og'irlik,Hajm,Summa",
    ).strip()
    sum_columns: tuple[str, ...] = tuple(
        p.strip() for p in sum_raw.split(",") if p.strip()
    )

    totals_text = os.getenv("GOOGLE_SHEETS_TOTALS_TEXT", "umumiy").strip() or "umumiy"
    totals_col = (
        os.getenv("GOOGLE_SHEETS_TOTALS_TEXT_COLUMN", "Qabul sana").strip()
        or "Qabul sana"
    )

    list_cell_range = os.getenv("GOOGLE_SHEETS_LIST_CELL_RANGE", "A:ZZ").strip() or "A:ZZ"

    if not sheet_id:
        raise RuntimeError("GOOGLE_SPREADSHEET_ID majburiy (Google Sheets).")

    if sa_info is not None:
        creds_path_res: str | None = None
        sa_res = sa_info
    elif creds_path:
        if not Path(creds_path).is_file():
            raise RuntimeError(f"GOOGLE_SHEETS_CREDENTIALS_PATH topilmadi: {creds_path}")
        creds_path_res = creds_path
        sa_res = None
    else:
        raise RuntimeError(
            "Google kalit: GOOGLE_SERVICE_ACCOUNT_JSON yoki GOOGLE_SA_* to‘plami, "
            "yoki GOOGLE_SHEETS_CREDENTIALS_PATH (JSON fayl yo‘li) kerak."
        )

    return Settings(
        bot_token=token,
        google_sheets_credentials_path=creds_path_res,
        google_service_account_info=sa_res,
        google_spreadsheet_id=sheet_id,
        google_sheets_export_range=export_range,
        google_sheets_lookup_range=lookup_range,
        google_sheets_number_header=number_header,
        google_sheets_kod_header=kod_header,
        google_sheets_header_rows=header_rows,
        google_sheets_sum_columns=sum_columns,
        google_sheets_totals_text=totals_text,
        google_sheets_totals_text_column=totals_col,
        google_sheets_list_cell_range=list_cell_range,
    )
