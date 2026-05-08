"""Foydalanuvchi tili bo‘yicha matnlar (ru, en, zh, uz, tr)."""

from __future__ import annotations

from typing import Any

LANG_RU = "ru"
LANG_EN = "en"
LANG_ZH = "zh"
LANG_UZ = "uz"
LANG_TR = "tr"
DEFAULT_LANG = LANG_EN

STRINGS: dict[str, dict[str, str]] = {
    "welcome": {
        LANG_RU: "Добро пожаловать! Выберите язык / Welcome! Select a language",
        LANG_EN: "Добро пожаловать! Выберите язык / Welcome! Select a language",
        LANG_ZH: "Добро пожаловать! Выберите язык / Welcome! Select a language",
        LANG_UZ: "Добро пожаловать! Выберите язык / Welcome! Select a language",
        LANG_TR: "Добро пожаловать! Выберите язык / Welcome! Select a language",
    },
    "enter_code": {
        LANG_RU: "Введите код.",
        LANG_EN: "Enter the code.",
        LANG_ZH: "请输入代码。",
        LANG_UZ: "Kodni kiriting.",
        LANG_TR: "Kodu girin.",
    },
    "need_start": {
        LANG_RU: "Сначала нажмите /start и выберите язык.",
        LANG_EN: "Please tap /start and choose a language first.",
        LANG_ZH: "请先发送 /start 并选择语言。",
        LANG_UZ: "Avval /start bosing va tilni tanlang.",
        LANG_TR: "Önce /start’a basın ve dil seçin.",
    },
    "pick_language_button": {
        LANG_RU: "Нажмите одну из кнопок внизу.",
        LANG_EN: "Tap one of the buttons below.",
        LANG_ZH: "请点击下方其中一个按钮。",
        LANG_UZ: "Pastdagi tugmalardan birini bosing.",
        LANG_TR: "Aşağıdaki düğmelerden birine basın.",
    },
    "pdf_error": {
        LANG_RU: "Не удалось подготовить PDF.",
        LANG_EN: "Could not prepare the PDF.",
        LANG_ZH: "无法生成 PDF。",
        LANG_UZ: "PDF tayyorlashda xatolik yuz berdi.",
        LANG_TR: "PDF hazırlanamadı.",
    },
    "unknown_error": {
        LANG_RU: "Неизвестная ошибка.",
        LANG_EN: "Unknown error.",
        LANG_ZH: "未知错误。",
        LANG_UZ: "Noma’lum xato.",
        LANG_TR: "Bilinmeyen hata.",
    },
    "sheets_403": {
        LANG_RU: "Нет доступа к таблице. В Google Sheets: «Доступ» → добавьте email сервисного аккаунта (хотя бы «Просмотр»).",
        LANG_EN: "No access to the spreadsheet. In Google Sheets: Share → add the service account email (at least Viewer).",
        LANG_ZH: "无法访问表格。在 Google 表格中：共享 → 添加服务账号邮箱（至少“查看者”）。",
        LANG_UZ: "Jadvalga ruxsat yo‘q. Google Sheetsda «Ulashish» → service account emailini qo‘shing (kamida «Ko‘rish»).",
        LANG_TR: "Tabloya erişim yok. Google Sheets: Paylaş → hizmet hesabı e-postasını ekleyin (en az Görüntüleyici).",
    },
    "sheets_404": {
        LANG_RU: "Таблица не найдена: неверный GOOGLE_SPREADSHEET_ID или файл в другом аккаунте.",
        LANG_EN: "Spreadsheet not found: wrong GOOGLE_SPREADSHEET_ID or file belongs to another account.",
        LANG_ZH: "找不到表格：GOOGLE_SPREADSHEET_ID 错误，或文件属于其他账号。",
        LANG_UZ: "Jadval topilmadi: GOOGLE_SPREADSHEET_ID noto‘g‘ri yoki fayl boshqa akkauntga tegishli.",
        LANG_TR: "Tablo bulunamadı: GOOGLE_SPREADSHEET_ID yanlış veya dosya başka hesapta.",
    },
    "sheets_400": {
        LANG_RU: "Неверный диапазон или имя листа. Проверьте GOOGLE_SHEETS_EXPORT_RANGE в .env.",
        LANG_EN: "Invalid range or sheet name. Check GOOGLE_SHEETS_EXPORT_RANGE in .env.",
        LANG_ZH: "范围或工作表名称无效。请检查 .env 中的 GOOGLE_SHEETS_EXPORT_RANGE。",
        LANG_UZ: "Jadval oralig‘i yoki varaq nomi noto‘g‘ri. .env da GOOGLE_SHEETS_EXPORT_RANGE ni tekshiring.",
        LANG_TR: "Geçersiz aralık veya sayfa adı. .env içinde GOOGLE_SHEETS_EXPORT_RANGE değerini kontrol edin.",
    },
    "sheets_generic": {
        LANG_RU: "Не удалось загрузить таблицу. Попробуйте позже.",
        LANG_EN: "Could not load the spreadsheet. Try again later.",
        LANG_ZH: "无法加载表格。请稍后重试。",
        LANG_UZ: "Jadvalni yuklab bo‘lmadi. Keyinroq urinib ko‘ring.",
        LANG_TR: "Tablo yüklenemedi. Daha sonra tekrar deneyin.",
    },
    "pdf_header_title": {
        LANG_RU: "Сведения о грузе",
        LANG_EN: "Shipment details",
        LANG_ZH: "货运明细",
        LANG_UZ: "Yuk ma’lumotlari",
        LANG_TR: "Yük bilgileri",
    },
    "pdf_line_code": {
        LANG_RU: "Код: {code}",
        LANG_EN: "Code: {code}",
        LANG_ZH: "代码：{code}",
        LANG_UZ: "Kod: {code}",
        LANG_TR: "Kod: {code}",
    },
    "pdf_footer_generated": {
        LANG_RU: "Сформировано: {when}",
        LANG_EN: "Generated: {when}",
        LANG_ZH: "生成时间：{when}",
        LANG_UZ: "Tayyorlangan: {when}",
        LANG_TR: "Oluşturulma: {when}",
    },
}


def t(lang: str | None, key: str, **kwargs: Any) -> str:
    code = (lang or DEFAULT_LANG).strip().lower()
    if code not in (LANG_RU, LANG_EN, LANG_ZH, LANG_UZ, LANG_TR):
        code = DEFAULT_LANG
    row = STRINGS.get(key, {})
    template = row.get(code) or row.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def localize_table_error(err: str, lang: str | None) -> str:
    """Jadval/KOD xabarlari: o‘zbekcha asl matn yoki boshqa tillarda umumiy xabar."""
    if (lang or DEFAULT_LANG) == LANG_UZ:
        return err
    return t(lang, "sheets_generic")


def sheets_http_message(exc: BaseException, lang: str | None) -> str:
    """Google Sheets API xatolari."""
    from googleapiclient.errors import HttpError

    from bot.google_sheets import user_message_for_sheets_error

    code = lang or DEFAULT_LANG
    if code == LANG_UZ:
        return user_message_for_sheets_error(exc)
    if isinstance(exc, HttpError):
        status = exc.resp.status if exc.resp else 0
        if status == 403:
            return t(lang, "sheets_403")
        if status == 404:
            return t(lang, "sheets_404")
        if status == 400:
            return t(lang, "sheets_400")
    return t(lang, "sheets_generic")
