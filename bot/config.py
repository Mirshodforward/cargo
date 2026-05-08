from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    google_sheets_credentials_path: str
    google_spreadsheet_id: str
    google_sheets_export_range: str
    google_sheets_kod_header: str
    google_sheets_header_rows: int
    google_sheets_sum_columns: tuple[str, ...]
    google_sheets_totals_text: str
    google_sheets_totals_text_column: str


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "").strip()
    sheet_id = os.getenv("GOOGLE_SPREADSHEET_ID", "").strip()
    export_range = os.getenv("GOOGLE_SHEETS_EXPORT_RANGE", "Sheet1").strip()
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

    if not creds_path or not sheet_id:
        raise RuntimeError(
            "GOOGLE_SHEETS_CREDENTIALS_PATH va GOOGLE_SPREADSHEET_ID majburiy "
            "(Google Sheetsdan eksport uchun)."
        )

    if not Path(creds_path).is_file():
        raise RuntimeError(f"GOOGLE_SHEETS_CREDENTIALS_PATH topilmadi: {creds_path}")

    return Settings(
        bot_token=token,
        google_sheets_credentials_path=creds_path,
        google_spreadsheet_id=sheet_id,
        google_sheets_export_range=export_range,
        google_sheets_kod_header=kod_header,
        google_sheets_header_rows=header_rows,
        google_sheets_sum_columns=sum_columns,
        google_sheets_totals_text=totals_text,
        google_sheets_totals_text_column=totals_col,
    )
