import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from campus_analytics.processing.analysis import load_gunluk_ozet, generate_report
from campus_analytics.reporting.report import save_report_json, save_report_pdf
from campus_analytics.config import GUNLUK_OZET_PATH, REPORT_JSON_PATH, REPORT_PDF_PATH, DEFAULT_MONTHS_BACK

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

df = load_gunluk_ozet(GUNLUK_OZET_PATH)

if df.empty:
    logging.warning(f"{GUNLUK_OZET_PATH} henuz bos — fetch_and_update.py en az bir kez calismadan rapor uretilemez.")
else:
    report = generate_report(df, months_back=DEFAULT_MONTHS_BACK)
    save_report_json(report, REPORT_JSON_PATH)
    save_report_pdf(report, REPORT_PDF_PATH, months_back=DEFAULT_MONTHS_BACK)
    logging.info(f"{len(report['universities'])} universite icin rapor uretildi.")