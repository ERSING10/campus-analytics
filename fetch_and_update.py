import requests
import pandas as pd
import os
from datetime import datetime

HAM_LOG_PATH = "data/ham_log.csv"
GUNLUK_OZET_PATH = "data/gunluk_ozet.csv"

# Dün Affiliation Search'ten çektiğimiz üniversite ID'leri
UNIVERSITY_IDS = {
    "Hacettepe Üniversitesi": "60020484",
    "Ankara Üniversitesi": "60012603",
    "İstanbul Teknik Üniversitesi": "60022002",
    "Istanbul Üniversitesi": "60028502",
    "Middle East Technical University (METU)": "60004305",
    "Kocaeli Üniversitesi": "60028583",
}


def get_scopus_publication_count_for_year(affiliation_id: str, year: str, api_key: str) -> int:
    url = "https://api.elsevier.com/content/search/scopus"
    params = {
        "query": f"AF-ID({affiliation_id}) AND PUBYEAR IS {year}",
        "apiKey": api_key,
        "httpAccept": "application/json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(data)  # debug için, sorunu görmek adına
    return int(data["search-results"]["opensearch:totalResults"])


def append_to_ham_log(records: list) -> None:
    new_rows = pd.DataFrame(records)
    existing = pd.read_csv(HAM_LOG_PATH)
    combined = pd.concat([existing, new_rows], ignore_index=True)
    combined.to_csv(HAM_LOG_PATH, index=False)


def update_gunluk_ozet(records: list, today: str) -> None:
    existing = pd.read_csv(GUNLUK_OZET_PATH)
    existing_without_today = existing[existing["date"] != today]

    today_rows = []
    for r in records:
        today_rows.append({"date": today, "university": r["university"], "value": r["value"]})
    today_df = pd.DataFrame(today_rows)

    combined = pd.concat([existing_without_today, today_df], ignore_index=True)
    combined.to_csv(GUNLUK_OZET_PATH, index=False)


if __name__ == "__main__":
    api_key = os.environ["SCOPUS_API_KEY"]

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    records = []
    for uni_name, affiliation_id in UNIVERSITY_IDS.items():
        count = get_scopus_publication_count_for_year(affiliation_id, "2026", api_key)
        records.append({
            "timestamp": timestamp_str,
            "university": uni_name,
            "value": count,
        })

    append_to_ham_log(records)
    update_gunluk_ozet(records, today_str)

    print(f"{len(records)} üniversite için veri güncellendi. Zaman: {timestamp_str}")