"""Jadval qatorlaridan chiroyli PDF (ReportLab)."""

from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

_FONT_REGISTERED: str | None = None


def _cell_text(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return str(val)
    return str(val).strip()


def _pick_unicode_font_name() -> str:
    global _FONT_REGISTERED
    if _FONT_REGISTERED is not None:
        return _FONT_REGISTERED

    candidates: list[Path] = []
    windir = os.environ.get("WINDIR", r"C:\Windows")
    candidates.extend(
        [
            Path(windir) / "Fonts" / "arial.ttf",
            Path(windir) / "Fonts" / "segoeui.ttf",
        ]
    )
    candidates.extend(
        [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        ]
    )

    for p in candidates:
        if p.is_file():
            try:
                pdfmetrics.registerFont(TTFont("CargoTableFont", str(p)))
                _FONT_REGISTERED = "CargoTableFont"
                return _FONT_REGISTERED
            except Exception:
                continue

    _FONT_REGISTERED = "Helvetica"
    return _FONT_REGISTERED


def rows_to_pdf_bytes(
    rows: list[list[Any]],
    *,
    header_row_count: int,
    title: str = "",
) -> bytes:
    """
    ``rows`` — Excel bilan bir xil tartibda (KOD ustuni olib tashlangandan keyin ham).
    Birinchi ``header_row_count`` qatori sarlavha, oxirgi qator — umumiy (ajratib chiziladi).
    Sahifa doim **landscape** (gorizontal), shriftlar kichik — keng jadval uchun.
    """
    if not rows:
        rows = [[""]]

    font = _pick_unicode_font_name()
    ncols = max(len(r) for r in rows)
    data: list[list[str]] = []
    for r in rows:
        padded = [_cell_text(r[i]) if i < len(r) else "" for i in range(ncols)]
        data.append(padded)

    # Doimiy gorizontal (landscape) — keng yozuv maydoni
    page = landscape(A4)
    page_w, page_h = page
    margin_h = 8 * mm
    margin_v = 10 * mm
    usable_w = page_w - 2 * margin_h

    col_w = usable_w / ncols if ncols else usable_w
    col_widths = [col_w] * ncols

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=page,
        leftMargin=margin_h,
        rightMargin=margin_h,
        topMargin=margin_v,
        bottomMargin=margin_v,
        title="Yuk",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="CargoTitle",
        parent=styles["Normal"],
        fontName=font,
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=6,
    )
    story: list[Any] = []
    if title.strip():
        story.append(
            Paragraph(escape(title).replace("\n", "<br/>"), title_style)
        )
        story.append(Spacer(1, 4 * mm))

    nrows = len(data)
    last_is_total = nrows > header_row_count
    header_depth = max(1, min(header_row_count, nrows))

    tbl = Table(
        data,
        colWidths=col_widths,
        repeatRows=header_depth,
        splitByRow=1,
    )

    header_bg = colors.HexColor("#2563eb")
    header_fg = colors.white
    body_bg = colors.HexColor("#f8fafc")
    body_alt = colors.HexColor("#f1f5f9")
    total_bg = colors.HexColor("#fef3c7")
    grid = colors.HexColor("#cbd5e1")

    # Kichik shrift + keng sahifa — gorizontalda ko‘proq matn sig‘adi
    fz_body = 5 if ncols > 14 else (6 if ncols > 10 else 7)
    fz_head = fz_body + 1
    fz_total = fz_body + 1

    ts = TableStyle(
        [
            ("FONTNAME", (0, 0), (-1, -1), font),
            ("FONTSIZE", (0, 0), (-1, -1), fz_body),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, header_depth), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("BOX", (0, 0), (-1, -1), 0.6, grid),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, grid),
        ]
    )

    if header_depth > 0:
        ts.add("BACKGROUND", (0, 0), (-1, header_depth - 1), header_bg)
        ts.add("TEXTCOLOR", (0, 0), (-1, header_depth - 1), header_fg)
        ts.add("FONTNAME", (0, 0), (-1, header_depth - 1), font)
        ts.add("FONTSIZE", (0, 0), (-1, header_depth - 1), fz_head)
    if header_depth <= nrows - 2:
        ts.add(
            "ROWBACKGROUNDS",
            (0, header_depth),
            (-1, nrows - 2),
            [body_bg, body_alt],
        )

    if last_is_total and nrows > header_depth:
        ts.add("BACKGROUND", (0, nrows - 1), (-1, nrows - 1), total_bg)
        ts.add("TEXTCOLOR", (0, nrows - 1), (-1, nrows - 1), colors.HexColor("#92400e"))
        ts.add("FONTNAME", (0, nrows - 1), (-1, nrows - 1), font)
        ts.add("FONTSIZE", (0, nrows - 1), (-1, nrows - 1), fz_total)
        ts.add("LINEABOVE", (0, nrows - 1), (-1, nrows - 1), 1, colors.HexColor("#f59e0b"))

    tbl.setStyle(ts)
    story.append(tbl)

    doc.build(story)
    return buf.getvalue()
