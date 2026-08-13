import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from datetime import datetime
import logging

from campus_analytics.config import (
    KOCAELI_ADI,
    RENK_KOCAELI,
    RENK_DIGER,
    UNI_RENKLERI,
    SIYAH,
    GRI,
    ACIK_GRI,
    FONT_REGULAR_PATH,
    FONT_BOLD_PATH,
    REPORT_JSON_PATH,
    REPORT_PDF_PATH,
    DEFAULT_MONTHS_BACK,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SIYAH_RENK = colors.HexColor(SIYAH)
GRI_RENK = colors.HexColor(GRI)
ACIK_GRI_RENK = colors.HexColor(ACIK_GRI)

try:
    pdfmetrics.registerFont(TTFont("TimesNewRoman", FONT_REGULAR_PATH))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", FONT_BOLD_PATH))
except Exception as hata:
    logging.error(f"Font dosyalari yuklenemedi, varsayilan font kullanilacak: {hata}")


def uni_rengi(university_name: str, yedek_index: int) -> str:
    if university_name == KOCAELI_ADI:
        return RENK_KOCAELI
    if university_name in UNI_RENKLERI:
        return UNI_RENKLERI[university_name]
    return RENK_DIGER[yedek_index % len(RENK_DIGER)]


def save_report_json(report: dict, filepath: str = REPORT_JSON_PATH) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def build_pasta_grafik(universities: list) -> Drawing:
    kocaeli = next((u for u in universities if u["university"] == KOCAELI_ADI), None)

    if kocaeli:
        ustteki = sorted(
            [u for u in universities if u["university"] != KOCAELI_ADI and u["new_value"] > kocaeli["new_value"]],
            key=lambda u: u["new_value"], reverse=True
        )
        pasta_verisi = ustteki + [kocaeli]
    else:
        pasta_verisi = sorted(universities, key=lambda u: u["new_value"], reverse=True)[:10]

    n = len(pasta_verisi)
    yukseklik = max(220, n * 16 + 40)

    drawing = Drawing(480, yukseklik)
    pie = Pie()
    pie.x = 20
    pie.y = yukseklik - 190
    pie.width = 170
    pie.height = 170
    pie.data = [u["new_value"] for u in pasta_verisi]
    pie.labels = None
    pie.sideLabels = False
    pie.slices.strokeWidth = 1
    pie.slices.strokeColor = colors.white

    yedek_index = 0
    renk_listesi = []
    for u in pasta_verisi:
        if u["university"] == KOCAELI_ADI:
            renk = RENK_KOCAELI
        elif u["university"] in UNI_RENKLERI:
            renk = UNI_RENKLERI[u["university"]]
        else:
            renk = RENK_DIGER[yedek_index % len(RENK_DIGER)]
            yedek_index += 1
        renk_listesi.append(renk)

    for i, renk in enumerate(renk_listesi):
        pie.slices[i].fillColor = colors.HexColor(renk)

    legend = Legend()
    legend.x = 230
    legend.y = yukseklik - 20
    legend.dx = 9
    legend.dy = 9
    legend.dxTextSpace = 6
    legend.deltay = 15
    legend.fontName = "TimesNewRoman"
    legend.fontSize = 8
    legend.alignment = "left"
    legend.columnMaximum = n
    legend.colorNamePairs = [
        (colors.HexColor(renk_listesi[i]), pasta_verisi[i]["university"])
        for i in range(n)
    ]

    drawing.add(pie)
    drawing.add(legend)
    return drawing


def save_report_pdf(report: dict, filepath: str = REPORT_PDF_PATH, months_back: int = DEFAULT_MONTHS_BACK) -> None:
    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    elements = []

    title_style = ParagraphStyle("TitleTR", fontName="TimesNewRoman-Bold", fontSize=18, textColor=SIYAH_RENK, spaceAfter=4)
    subtitle_style = ParagraphStyle("SubtitleTR", fontName="TimesNewRoman", fontSize=9, textColor=GRI_RENK, spaceAfter=16)
    section_style = ParagraphStyle("SectionTR", fontName="TimesNewRoman-Bold", fontSize=13, textColor=SIYAH_RENK, spaceBefore=16, spaceAfter=8)

    universities = report["universities"]
    sirali_liste = sorted(universities, key=lambda u: u["new_value"], reverse=True)
    kocaeli = next((u for u in universities if u["university"] == KOCAELI_ADI), None)
    toplam_uni = len(universities)
    toplam_yayin = sum(u["new_value"] for u in universities)
    simdi = datetime.now().strftime("%d.%m.%Y %H:%M")

    elements.append(Paragraph("Üniversite Değişim Raporu", title_style))
    elements.append(Paragraph(
        f"{toplam_uni} üniversite izleniyor · {months_back} aylık karşılaştırma · Oluşturulma: {simdi}",
        subtitle_style
    ))

    ozet_style = ParagraphStyle("OzetBaslik", fontName="TimesNewRoman", fontSize=8, textColor=GRI_RENK)
    ozet_deger_style = ParagraphStyle("OzetDeger", fontName="TimesNewRoman-Bold", fontSize=14, textColor=SIYAH_RENK)

    ozet_data = [[
        [Paragraph("TOPLAM ÜNİVERSİTE", ozet_style), Paragraph(str(toplam_uni), ozet_deger_style)],
        [Paragraph("TOPLAM YAYIN (İZLENEN)", ozet_style), Paragraph(f"{toplam_yayin:,}".replace(",", "."), ozet_deger_style)],
        [Paragraph("KOCAELİ ÜNİVERSİTESİ YAYIN SAYISI", ozet_style), Paragraph(f"{kocaeli['new_value']:,}".replace(",", ".") if kocaeli else "-", ozet_deger_style)],
    ]]
    ozet_table = Table(ozet_data, colWidths=[5.7 * cm, 5.7 * cm, 5.7 * cm])
    ozet_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACIK_GRI_RENK),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("LINEAFTER", (0, 0), (0, 0), 0.5, colors.HexColor("#d1d5db")),
        ("LINEAFTER", (1, 0), (1, 0), 0.5, colors.HexColor("#d1d5db")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(ozet_table)

    elements.append(Paragraph("Yayın Dağılımı (Kocaeli ve Üstündekiler)", section_style))
    elements.append(build_pasta_grafik(universities))

    elements.append(Paragraph("Tüm Üniversiteler (Yayın Sayısına Göre Sıralı)", section_style))
    base_style = [
        ("FONTNAME", (0, 0), (-1, -1), "TimesNewRoman"),
        ("FONTNAME", (0, 0), (-1, 0), "TimesNewRoman-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("TEXTCOLOR", (0, 1), (-1, -1), SIYAH_RENK),
        ("BACKGROUND", (0, 0), (-1, 0), SIYAH_RENK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ACIK_GRI_RENK]),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    table_data = [["Üniversite", "Toplam Yayın", "10G Değişim", "30G Değişim", "Momentum"]]
    for r in sirali_liste:
        c10 = r["change_10d"]["change_pct"]
        c30 = r["change_30d"]["change_pct"]
        mom = r["momentum"]["momentum"]
        table_data.append([
            r["university"],
            f"{r['new_value']:,}".replace(",", "."),
            f"%{c10}" if c10 is not None else "yetersiz veri",
            f"%{c30}" if c30 is not None else "yetersiz veri",
            f"{mom}" if mom is not None else "yetersiz veri",
        ])
    table = Table(table_data, repeatRows=1, colWidths=[5*cm, 2.8*cm, 2.8*cm, 2.8*cm, 2.6*cm])
    table.setStyle(TableStyle(base_style))
    elements.append(table)

    elements.append(Paragraph("En Çok Artan 5 Üniversite", section_style))
    top_data = [["Üniversite", "% Değişim"]] + [
        [g["university"], f"%{g['change_pct']}" if g["change_pct"] is not None else "yetersiz veri"]
        for g in report["top_gainers"]
    ]
    top_table = Table(top_data, colWidths=[10 * cm, 4 * cm])
    top_table.setStyle(TableStyle(base_style))
    elements.append(top_table)

    try:
        doc.build(elements)
        logging.info(f"PDF basariyla olusturuldu: {filepath}")
    except Exception as hata:
        logging.error(f"PDF olusturulurken hata olustu: {hata}")
        raise