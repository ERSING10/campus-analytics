import requests
import pandas as pd
import os
from datetime import datetime

HAM_LOG_PATH = "data/ham_log.csv"
GUNLUK_OZET_PATH = "data/gunluk_ozet.csv"

def get_scopus_universities(api_key: str, limit: int = 20) -> list:
    # Scopus Affiliation Search API'den Türkiye üniversitelerini (isim + yayın sayısı) çeker
    url = "https://api.elsevier.com/content/search/affiliation"
    params = {
        "query": "affil(university) AND affilcountry(Turkey)",
        "count": limit,
        "apiKey": api_key,
        "httpAccept": "application/json"
    }
    response = requests.get(url, params=params)
    data = response.json()

    universities = []
    print(data)
    entries = data["search-results"]["entry"]
    for entry in entries:
        universities.append({
            "name": entry["affiliation-name"],
            "value": int(entry["document-count"])
        })
    return universities


def append_to_ham_log(records: list) -> None:
    # yeni ölçümleri ham_log.csv'nin sonuna ekler
    new_rows = pd.DataFrame(records)
    existing = pd.read_csv(HAM_LOG_PATH)
    combined = pd.concat([existing, new_rows], ignore_index=True)
    combined.to_csv(HAM_LOG_PATH, index=False)


def update_gunluk_ozet(records: list, today: str) -> None:
    # bugüne ait satırları günceller, geçmiş günlere dokunmaz
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
    universities = get_scopus_universities(api_key, limit=20)

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    records = []
    for uni in universities:
        records.append({
            "timestamp": timestamp_str,
            "university": uni["name"],
            "value": uni["value"],
        })

    append_to_ham_log(records)
    update_gunluk_ozet(records, today_str)

    print(f"{len(records)} üniversite için veri güncellendi. Zaman: {timestamp_str}")