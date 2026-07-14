from analysis import load_gunluk_ozet, generate_report
from report import save_report_json, save_report_pdf

df = load_gunluk_ozet("data/gunluk_ozet.csv")
report = generate_report(df, months_back=3)

save_report_json(report, "report.json")
save_report_pdf(report, "report.pdf", months_back=3)

print(f"{len(report['universities'])} üniversite için rapor üretildi.")