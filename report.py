import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("TimesNewRoman", "C:/Windows/Fonts/times.ttf"))
pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", "C:/Windows/Fonts/timesbd.ttf"))

def save_report_json(report: dict, filepath: str = "report.json") -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def save_report_pdf(report: dict, filepath: str = "report.pdf", months_back: int = 3) -> None:
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []

    title_style = ParagraphStyle(
        "TitleTR", fontName="TimesNewRoman-Bold", fontSize=16,
        textColor=colors.black, spaceAfter=12,
    )
    elements.append(Paragraph(f"Üniversite {months_back} Aylık Değişim Raporu (Aylık Ortalamaya Göre)", title_style))
    elements.append(Spacer(1, 1 * cm))

    base_style = [
        ("FONTNAME", (0, 0), (-1, -1), "TimesNewRoman"),
        ("FONTNAME", (0, 0), (-1, 0), "TimesNewRoman-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]

    table_data = [["Üniversite", "Eski Ay", "Eski Ort.", "Yeni Ay", "Yeni Ort.", "% Değişim"]]
    for r in report["universities"]:
        table_data.append([
            r["university"], r["old_month"], str(r["old_value"]),
            r["new_month"], str(r["new_value"]), f"{r['change_pct']}%"
        ])
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle(base_style))
    elements.append(table)

    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph("En Çok Artan 5 Üniversite", title_style))
    top_data = [["Üniversite", "% Değişim"]] + [[g["university"], f"{g['change_pct']}%"] for g in report["top_gainers"]]
    top_table = Table(top_data)
    top_table.setStyle(TableStyle(base_style))
    elements.append(top_table)

    doc.build(elements)