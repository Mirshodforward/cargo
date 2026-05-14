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
    "share_contact": {
        LANG_RU: "Отправьте свой контакт — мы проверим номер в базе.",
        LANG_EN: "Share your contact so we can verify your number in the database.",
        LANG_ZH: "请发送您的联系人，以便我们在数据库中验证号码。",
        LANG_UZ: "Kontaktingizni yuboring — raqamingiz bazada tekshiriladi.",
        LANG_TR: "Kişinizi paylaşın — numaranızı veritabanında doğrulayalım.",
    },
    "contact_share_btn": {
        LANG_RU: "📱 Отправить контакт",
        LANG_EN: "📱 Share contact",
        LANG_ZH: "📱 分享联系人",
        LANG_UZ: "📱 Kontaktni ulash",
        LANG_TR: "📱 Kişiyi paylaş",
    },
    "customer_not_found": {
        LANG_RU: "Клиент не найден в базе данных.",
        LANG_EN: "Customer not found in the database.",
        LANG_ZH: "数据库中未找到该客户。",
        LANG_UZ: "Mijoz ma'lumotlar bazasida topilmadi!",
        LANG_TR: "Müşteri veritabanında bulunamadı.",
    },
    "customer_found_codes": {
        LANG_RU: "Номер найден. Сначала выберите код, затем тип груза (кнопки внизу) — пришлём PDF.",
        LANG_EN: "Number found. Pick a code, then the shipment type below — we’ll send the PDF.",
        LANG_ZH: "号码已找到。请先选择代码，再选择货物类型 — 我们将发送 PDF。",
        LANG_UZ: "Raqam topildi. Avval kodni, keyin yuk turini (pastdagi tugmalar) tanlang — PDF yuboramiz.",
        LANG_TR: "Numara bulundu. Önce kodu, sonra yük türünü seçin — PDF göndeririz.",
    },
    "kod_not_in_list": {
        LANG_RU: "Этот код не подходит. Нажмите одну из кнопок ниже.",
        LANG_EN: "That code does not match. Use one of the buttons below.",
        LANG_ZH: "此代码无效。请使用下方按钮。",
        LANG_UZ: "Bu kod mos emas. Pastdagi tugmalardan foydalaning.",
        LANG_TR: "Bu kod uygun değil. Aşağıdaki düğmeleri kullanın.",
    },
    "contact_invalid": {
        LANG_RU: "Не удалось прочитать номер телефона.",
        LANG_EN: "Could not read the phone number from the contact.",
        LANG_ZH: "无法读取联系人中的电话号码。",
        LANG_UZ: "Telefon raqamini o‘qib bo‘lmadi.",
        LANG_TR: "Telefon numarası okunamadı.",
    },
    "contact_text_only": {
        LANG_RU: "Используйте кнопку «Отправить контакт».",
        LANG_EN: "Please use the «Share contact» button.",
        LANG_ZH: "请使用「分享联系人」按钮。",
        LANG_UZ: "«Kontaktni ulash» tugmasidan foydalaning.",
        LANG_TR: "Lütfen «Kişiyi paylaş» düğmesini kullanın.",
    },
    "list_exporting": {
        LANG_RU: "⏳ Собираю все листы в Excel (.xlsx)…",
        LANG_EN: "⏳ Building Excel (.xlsx) from all sheets…",
        LANG_ZH: "⏳ 正在将所有工作表导出为 Excel (.xlsx)…",
        LANG_UZ: "⏳ Barcha varaqlar Excel (.xlsx) ga yig‘ilmoqda…",
        LANG_TR: "⏳ Tüm sayfalar Excel (.xlsx) olarak hazırlanıyor…",
    },
    "list_caption": {
        LANG_RU: "Экспорт Google Sheets (все вкладки).",
        LANG_EN: "Google Sheets export (all tabs).",
        LANG_ZH: "Google 表格导出（所有工作表）。",
        LANG_UZ: "Google Sheets eksporti (barcha varaqlar).",
        LANG_TR: "Google Sheets dışa aktarımı (tüm sekmeler).",
    },
    "list_too_large": {
        LANG_RU: "Файл слишком большой для Telegram (лимит ~50 МБ). Уменьшите таблицу или диапазон GOOGLE_SHEETS_LIST_CELL_RANGE.",
        LANG_EN: "File is too large for Telegram (~50 MB limit). Reduce the sheet or narrow GOOGLE_SHEETS_LIST_CELL_RANGE.",
        LANG_ZH: "文件超过 Telegram 上限（约 50 MB）。请缩小表格或调整 GOOGLE_SHEETS_LIST_CELL_RANGE。",
        LANG_UZ: "Fayl Telegram uchun juda katta (~50 MB cheklovi). Jadvalni kichraytiring yoki GOOGLE_SHEETS_LIST_CELL_RANGE ni toraytiring.",
        LANG_TR: "Dosya Telegram limitini aşıyor (~50 MB). Tabloyu küçültün veya GOOGLE_SHEETS_LIST_CELL_RANGE değerini daraltın.",
    },
    "pick_status_filter": {
        LANG_RU: "Выберите категорию для PDF: в пути, прибывшие или забрал.",
        LANG_EN: "Choose a category for the PDF: in transit, arrived, or picked up.",
        LANG_ZH: "请选择 PDF 类别：在途、已到或已取走。",
        LANG_UZ: "PDF uchun: yo‘lda, kelgan yoki olib ketilgan — tugmani tanlang.",
        LANG_TR: "PDF için kategori seçin: yolda, varmış veya teslim alındı.",
    },
    "status_filter_btn_in_transit": {
        LANG_RU: "Товары в пути",
        LANG_EN: "Goods in transit",
        LANG_ZH: "在途货物",
        LANG_UZ: "Yo‘ldagi yuklar",
        LANG_TR: "Yoldaki yükler",
    },
    "status_filter_btn_arrived": {
        LANG_RU: "Прибывшие товары",
        LANG_EN: "Arrived goods",
        LANG_ZH: "已到货物",
        LANG_UZ: "Kelgan yuklar",
        LANG_TR: "Varış yapan yükler",
    },
    "status_filter_btn_picked_up": {
        LANG_RU: "Забрал (олиб кетилган)",
        LANG_EN: "Picked up",
        LANG_ZH: "已取走",
        LANG_UZ: "Olib ketilgan",
        LANG_TR: "Teslim alındı",
    },
    "status_filter_buttons_only": {
        LANG_RU: "Нажмите одну из кнопок ниже.",
        LANG_EN: "Please tap one of the buttons below.",
        LANG_ZH: "请点击下方按钮之一。",
        LANG_UZ: "Pastdagi tugmalardan birini bosing.",
        LANG_TR: "Lütfen aşağıdaki düğmelerden birine basın.",
    },
    "pdf_line_status_in_transit": {
        LANG_RU: "Фильтр: только «В пути»",
        LANG_EN: "Filter: in transit only",
        LANG_ZH: "筛选：仅「在途」",
        LANG_UZ: "Filtr: faqat «Yo‘lda» (В пути)",
        LANG_TR: "Filtre: yolda (В пути)",
    },
    "pdf_line_status_arrived": {
        LANG_RU: "Фильтр: только прибывшие",
        LANG_EN: "Filter: arrived only",
        LANG_ZH: "筛选：仅已到",
        LANG_UZ: "Filtr: faqat kelganlar (Прибывшие)",
        LANG_TR: "Filtre: varmış",
    },
    "pdf_line_status_picked_up": {
        LANG_RU: "Фильтр: только «Забрал» / олиб кетилган",
        LANG_EN: "Filter: picked up only",
        LANG_ZH: "筛选：仅已取走",
        LANG_UZ: "Filtr: faqat olib ketilgan (Забрал)",
        LANG_TR: "Filtre: teslim alınmış",
    },
    "pdf_sent_pick_again": {
        LANG_RU: "Можно выбрать другой код или категорию.",
        LANG_EN: "You can pick another code or category.",
        LANG_ZH: "可以选择其他代码或类别。",
        LANG_UZ: "Boshqa kod yoki toifani tanlashingiz mumkin.",
        LANG_TR: "Başka kod veya kategori seçebilirsiniz.",
    },
    "table_err_status_column": {
        LANG_RU: "В заголовках таблицы не найдена колонка «Status» (Status / Статус / 状态).",
        LANG_EN: "Could not find a «Status» column in the table headers (Status / Статус / 状态).",
        LANG_ZH: "表头中找不到「状态」列。",
        LANG_UZ: "Jadval sarlavhalarida «Status» ustuni topilmadi (Status / Статус / 状态).",
        LANG_TR: "Tablo başlıklarında «Status» sütunu bulunamadı.",
    },
    "table_err_status_empty": {
        LANG_RU: "Нет строк для выбранного статуса (В пути / прибывшие / Забрал).",
        LANG_EN: "No rows for the selected status (in transit / arrived / picked up).",
        LANG_ZH: "所选状态下没有数据行。",
        LANG_UZ: "Tanlangan status bo‘yicha qatorlar yo‘q (В пути / Прибывшие / Забрал).",
        LANG_TR: "Seçilen durum için satır yok.",
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
    """Jadval/KOD xabarlari: o‘zbekcha asl matn yoki boshqa tillarda tarjima."""
    code = (lang or DEFAULT_LANG).strip().lower()
    if code == LANG_UZ:
        return err
    if "«Status» ustuni topilmadi" in err:
        return t(lang, "table_err_status_column")
    if "Tanlangan status bo‘yicha qatorlar yo‘q" in err:
        return t(lang, "table_err_status_empty")
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
