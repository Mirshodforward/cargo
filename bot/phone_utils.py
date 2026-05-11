"""Telegram kontakt raqamini jadvaldagi NUMBER ustuni bilan solishtirish."""

from __future__ import annotations

import re
import unicodedata


def normalize_phone_digits(phone: str | None) -> str | None:
    """
    Raqamlarni ajratadi; O‘zbekiston uchun 998 prefiksini olib tashlab 9 raqamli format.
    Jadvalda 941339383 yoki 700719383 kabi saqlangan bo‘lsa mos keladi.
    """
    if not phone:
        return None
    s = unicodedata.normalize("NFKC", str(phone).strip())
    for ch in (
        "\ufeff",
        "\u200b",
        "\u200e",
        "\u200f",
        "\u202a",
        "\u202c",
        "\xa0",
        "\u202f",
    ):
        s = s.replace(ch, "")
    s = s.strip().strip("'\"")
    d = re.sub(r"\D", "", s)
    if not d:
        return None
    if d.startswith("998") and len(d) >= 11:
        d = d[3:]
    if len(d) > 9:
        d = d[-9:]
    if len(d) != 9 or not d.isdigit():
        return None
    return d
