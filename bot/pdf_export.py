"""Jadval qatorlaridan chiroyli PDF (ReportLab)."""

from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

_FONT_REGISTERED: str | None = None


def _register_cargo_table_font(path: Path) -> bool:
    """TTF/OTF yoki TTC; xitoy/kirill/lotin uchun keng qamrovli shriftlar."""
    if not path.is_file():
        return False
    suf = path.suffix.lower()
    try:
        if suf == ".ttc":
            for idx in (0, 1, 2, 3):
                try:
                    pdfmetrics.registerFont(
                        TTFont("CargoTableFont", str(path), subfontIndex=idx)
                    )
                    return True
                except Exception:
                    continue
            return False
        pdfmetrics.registerFont(TTFont("CargoTableFont", str(path)))
        return True
    except Exception:
        return False


def _unicode_font_candidate_paths() -> list[Path]:
    """Tartib muhim: avvalo CJK qo‘llab-quvvatlaydigan shriftlar."""
    paths: list[Path] = []
    env = os.getenv("CARGO_PDF_FONT", "").strip()
    if env:
        paths.append(Path(env))

    windir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    paths.extend(
        [
            windir / "msyh.ttc",
            windir / "msyhl.ttc",
            windir / "msyhbd.ttc",
            windir / "simsun.ttc",
            windir / "simsunb.ttf",
            windir / "simhei.ttf",
            windir / "msjhl.ttc",
            windir / "malgun.ttf",
            windir / "malgunbd.ttf",
            windir / "segoeui.ttf",
            windir / "arial.ttf",
        ]
    )

    roots = (Path("/usr/share/fonts"), Path("/usr/local/share/fonts"))
    noto_rel = (
        "opentype/noto/NotoSansCJK-Regular.ttc",
        "opentype/noto/NotoSansCJKsc-Regular.otf",
        "noto-cjk/NotoSansCJK-Regular.ttc",
        "truetype/noto/NotoSansCJK-Regular.ttc",
        "truetype/noto/NotoSansSC-Regular.otf",
        "opentype/noto/NotoSansSC-Regular.otf",
    )
    for root in roots:
        for rel in noto_rel:
            paths.append(root / rel)

    paths.extend(
        [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        ]
    )

    mac = Path("/System/Library/Fonts/Supplemental")
    paths.extend(
        [
            mac / "Arial Unicode.ttf",
            Path("/Library/Fonts/Arial Unicode.ttf"),
        ]
    )

    seen: set[str] = set()
    unique: list[Path] = []
    for p in paths:
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def _draw_footer(canvas: Any, doc: Any, *, text: str, font: str) -> None:
    """Har sahifa pastki qismi (mijoz tili)."""
    canvas.saveState()
    canvas.setFont(font, 7)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(doc.leftMargin, 10, text)
    canvas.restoreState()


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

    for p in _unicode_font_candidate_paths():
        if _register_cargo_table_font(p):
            _FONT_REGISTERED = "CargoTableFont"
            return _FONT_REGISTERED

    _FONT_REGISTERED = "Helvetica"
    return _FONT_REGISTERED


def rows_to_pdf_bytes(
    rows: list[list[Any]],
    *,
    header_row_count: int,
    title: str = "",
    header_title: str = "",
    header_code_line: str = "",
    footer_line: str = "",
) -> bytes:
    """
    ``rows`` — Excel bilan bir xil tartibda (KOD ustuni olib tashlangandan keyin ham).
    Birinchi ``header_row_count`` qatori sarlavha, oxirgi qator — umumiy (ajratib chiziladi).
    Sahifa doim **landscape** (gorizontal), shriftlar kichik — keng jadval uchun.

    ``header_title`` / ``header_code_line`` — jadval ustidagi matn (mijoz tili).
    ``footer_line`` — har sahifa pastida (mijoz tili).
    ``title`` — eski API; bo‘sh bo‘lmasa ``header_title`` dan keyin qo‘shiladi.
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
    head_main = ParagraphStyle(
        name="CargoPdfHeaderMain",
        parent=styles["Normal"],
        fontName=font,
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        alignment=TA_CENTER,
        spaceAfter=3,
    )
    head_sub = ParagraphStyle(
        name="CargoPdfHeaderSub",
        parent=styles["Normal"],
        fontName=font,
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#334155"),
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    story: list[Any] = []
    if header_title.strip():
        story.append(
            Paragraph(
                escape(header_title).replace("\n", "<br/>"),
                head_main,
            )
        )
    if header_code_line.strip():
        story.append(
            Paragraph(
                escape(header_code_line).replace("\n", "<br/>"),
                head_sub,
            )
        )
    if title.strip():
        story.append(
            Paragraph(escape(title).replace("\n", "<br/>"), title_style)
        )
        story.append(Spacer(1, 2 * mm))
    elif header_title.strip() or header_code_line.strip():
        story.append(Spacer(1, 2 * mm))

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

    foot = footer_line.strip()
    if foot:

        def _on_page(canvas: Any, doc: Any) -> None:
            _draw_footer(canvas, doc, text=foot, font=font)

        doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    else:
        doc.build(story)
    return buf.getvalue()
