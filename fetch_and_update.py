import requests
import pandas as pd
import os
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

HAM_LOG_PATH = "data/ham_log.csv"
GUNLUK_OZET_PATH = "data/gunluk_ozet.csv"


def load_university_ids(filepath: str = "data/university_ids.csv") -> dict:
    df = pd.read_csv(filepath)
    university_ids = {}
    for _, row in df.iterrows():
        university_ids[row["name"]] = str(row["affiliation_id"])
    return university_ids


def get_scopus_publication_count_for_year(affiliation_id: str, year: str, api_key: str) -> int:
    url = "https://api.elsevier.com/content/search/scopus"
    params = {
        "query": f"AF-ID({affiliation_id}) AND PUBYEAR IS {year}",
        "apiKey": api_key,
        "httpAccept": "application/json"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "search-results" not in data:
        logging.error(f"Scopus beklenmeyen cevap dondu, affiliation_id={affiliation_id}: {data}")
        raise ValueError(f"Scopus cevabinda 'search-results' yok: {data}")

    return int(data["search-results"]["opensearch:totalResults"])


def append_to_ham_log(records: list) -> None:
    new_rows = pd.DataFrame(records)
    existing = pd.read_csv(HAM_LOG_PATH)
    combined = pd.concat([existing, new_rows], ignore_index=True)
    combined.to_csv(HAM_LOG_PATH, index=False)
    logging.info(f"ham_log.csv guncellendi, {len(new_rows)} yeni satir eklendi")


def update_gunluk_ozet(records: list, today: str) -> None:
    existing = pd.read_csv(GUNLUK_OZET_PATH)
    existing_without_today = existing[existing["date"] != today]

    today_rows = []
    for r in records:
        today_rows.append({"date": today, "university": r["university"], "value": r["value"]})
    today_df = pd.DataFrame(today_rows)

    combined = pd.concat([existing_without_today, today_df], ignore_index=True)
    combined.to_csv(GUNLUK_OZET_PATH, index=False)
    logging.info(f"gunluk_ozet.csv guncellendi, tarih={today}")


if __name__ == "__main__":
    logging.info("Veri cekme islemi basladi")

    api_key = os.environ["SCOPUS_API_KEY"]
    university_ids = load_university_ids()
    logging.info(f"{len(university_ids)} universite ID'si yuklendi")

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    records = []
    for uni_name, affiliation_id in university_ids.items():
        count = get_scopus_publication_count_for_year(affiliation_id, "2026", api_key)
        records.append({
            "timestamp": timestamp_str,
            "university": uni_name,
            "value": count,
        })
        logging.info(f"{uni_name}: {count} yayin")

    append_to_ham_log(records)
    update_gunluk_ozet(records, today_str)

    logging.info(f"{len(records)} universite icin veri guncellendi. Zaman: {timestamp_str}")