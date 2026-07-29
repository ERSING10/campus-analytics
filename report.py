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

pdfmetrics.registerFont(TTFont("TimesNewRoman", "fonts/DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", "fonts/DejaVuSerif-Bold.ttf"))

KOYU_LACIVERT = colors.HexColor("#1e3a5f")
ACIK_GRI = colors.HexColor("#f8fafc")
PASTA_RENKLERI = [
    "#1e3a5f", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd",
    "#0ea5e9", "#0891b2", "#06b6d4", "#22d3ee", "#67e8f9",
]


def save_report_json(report: dict, filepath: str = "report.json") -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def build_pasta_grafik(universities: list) -> Drawing:
    ilk_10 = sorted(universities, key=lambda u: u["latest"]["value"], reverse=True)[:10]

    drawing = Drawing(400, 220)
    pie = Pie()
    pie.x = 30
    pie.y = 10
    pie.width = 160
    pie.height = 160
    pie.data = [u["latest"]["value"] for u in ilk_10]
    pie.labels = None
    pie.sideLabels = False

    for i, renk in enumerate(PASTA_RENKLERI[:len(ilk_10)]):
        pie.slices[i].fillColor = colors.HexColor(renk)
        pie.slices[i].strokeColor = colors.white
        pie.slices[i].strokeWidth = 1

    legend = Legend()
    legend.x = 210
    legend.y = 170
    legend.dx = 8
    legend.dy = 8
    legend.fontName = "TimesNewRoman"
    legend.fontSize = 7
    legend.alignment = "left"
    legend.columnMaximum = 10
    legend.colorNamePairs = [
        (colors.HexColor(PASTA_RENKLERI[i]), (u["university"][:28]))
        for i, u in enumerate(ilk_10)
    ]

    drawing.add(pie)
    drawing.add(legend)
    return drawing


def save_report_pdf(report: dict, filepath: str = "report.pdf", months_back: int = 3) -> None:
    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    elements = []

    title_style = ParagraphStyle(
        "TitleTR", fontName="TimesNewRoman-Bold", fontSize=18,
        textColor=KOYU_LACIVERT, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "SubtitleTR", fontName="TimesNewRoman", fontSize=9,
        textColor=colors.HexColor("#64748b"), spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "SectionTR", fontName="TimesNewRoman-Bold", fontSize=13,
        textColor=KOYU_LACIVERT, spaceBefore=16, spaceAfter=8,
    )

    universities = report["universities"]
    toplam_uni = len(universities)
    toplam_yayin = sum(u["latest"]["value"] for u in universities)
    en_yuksek = max(universities, key=lambda u: u["latest"]["value"])
    simdi = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Başlık
    elements.append(Paragraph("Üniversite Değişim Raporu", title_style))
    elements.append(Paragraph(
        f"{toplam_uni} üniversite izleniyor · Oluşturulma: {simdi}",
        subtitle_style
    ))


    ozet_style = ParagraphStyle("OzetBaslik", fontName="TimesNewRoman", fontSize=8, textColor=colors.HexColor("#64748b"))
    ozet_deger_style = ParagraphStyle("OzetDeger", fontName="TimesNewRoman-Bold", fontSize=14, textColor=KOYU_LACIVERT)

    ozet_data = [[
        [Paragraph("TOPLAM ÜNİVERSİTE", ozet_style), Paragraph(str(toplam_uni), ozet_deger_style)],
        [Paragraph("TOPLAM YAYIN (İZLENEN)", ozet_style), Paragraph(f"{toplam_yayin:,}".replace(",", "."), ozet_deger_style)],
        [Paragraph("EN YÜKSEK YAYIN SAYISI", ozet_style), Paragraph(f"{en_yuksek['latest']['value']:,}".replace(",", ".") + " - " + en_yuksek["university"][:22], ozet_deger_style)],
    ]]
    ozet_table = Table(ozet_data, colWidths=[5.7 * cm, 5.7 * cm, 5.7 * cm])
    ozet_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACIK_GRI),
        ("BOX", (0, 0), (0, 0), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (1, 0), (1, 0), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (2, 0), (2, 0), 0.5, colors.HexColor("#e2e8f0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(ozet_table)

    # Pasta grafiği
    elements.append(Paragraph("Yayın Dağılımı (İlk 10 Üniversite)", section_style))
    elements.append(build_pasta_grafik(universities))

    # Ana tablo
    elements.append(Paragraph("Tüm Üniversiteler", section_style))

    base_style = [
        ("FONTNAME", (0, 0), (-1, -1), "TimesNewRoman"),
        ("FONTNAME", (0, 0), (-1, 0), "TimesNewRoman-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), KOYU_LACIVERT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ACIK_GRI]),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]

    table_data = [["Üniversite", "Toplam Yayın", "10G Değişim", "30G Değişim", "Momentum"]]
    for r in universities:
        change_10 = r["change_10d"]["change_pct"]
        change_30 = r["change_30d"]["change_pct"]
        momentum = r["momentum"]["momentum"]

        table_data.append([
            r["university"],
            f"{r['latest']['value']:,}".replace(",", "."),
            f"%{change_10}" if change_10 is not None else "yetersiz veri",
            f"%{change_30}" if change_30 is not None else "yetersiz veri",
            f"{momentum}" if momentum is not None else "yetersiz veri",
        ])

    table = Table(table_data, repeatRows=1, colWidths=[5*cm, 2.6*cm, 2.6*cm, 2.6*cm, 2.4*cm])
    table.setStyle(TableStyle(base_style))
    elements.append(table)

    # En çok artan 5
    elements.append(Paragraph("En Çok Artan 5 Üniversite", section_style))
    top_style = [
        ("FONTNAME", (0, 0), (-1, -1), "TimesNewRoman"),
        ("FONTNAME", (0, 0), (-1, 0), "TimesNewRoman-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), KOYU_LACIVERT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ACIK_GRI]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    top_data = [["Üniversite", "% Değişim"]] + [
        [g["university"], f"%{g['change_pct']}" if g["change_pct"] is not None else "yetersiz veri"]
        for g in report["top_gainers"]
    ]
    top_table = Table(top_data, colWidths=[10 * cm, 4 * cm])
    top_table.setStyle(TableStyle(top_style))
    elements.append(top_table)

    doc.build(elements)