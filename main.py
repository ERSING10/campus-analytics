from data import load_data
from analysis import generate_report
from report import save_report_json, save_report_pdf

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJrWRmkkmRDm9w5AId8j7YwWBNE5cCgvdNQWG8-vm_ud7URYbYeViMCenHENPjtXdx67Ko3qOz2cZM/pub?gid=171772518&single=true&output=csv"
df = load_data(url)

report = generate_report(df, months_back=3)
save_report_json(report, "report.json")
save_report_pdf(report, "report.pdf", months_back=3)

print(f"{len(report['universities'])} üniversite için rapor üretildi.")