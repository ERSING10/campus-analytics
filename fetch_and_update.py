import requests
import pandas as pd
import random
from datetime import datetime

HAM_LOG_PATH = "data/ham_log.csv"
GUNLUK_OZET_PATH = "data/gunluk_ozet.csv"

def get_university_names(limit: int = 20) -> list:
    # hipolabs API'den Türkiye'deki üniversitelerin isimlerini çeker
    # gercek veriler geldikten sonra o apiye istek atacaz. simdilik burdayız
    url = "http://universities.hipolabs.com/search?country=Turkiye"
    response = requests.get(url)
    data = response.json()
    names = []
    for uni in data[:limit]:
      names.append(uni["name"])

    return names


def load_last_values(gunluk_df: pd.DataFrame, university_names: list) -> dict:
    # her üniversite için şu ana kadarki en son (en yüksek) değeri bulur
    last_values = {}
    for uni in university_names:
        uni_rows = gunluk_df[gunluk_df["university"] == uni]
        if uni_rows.empty:
            last_values[uni] = random.randint(80, 400)  # ilk kayıt, rastgele başlangıç
        else:
            last_values[uni] = uni_rows["value"].max()
    return last_values


def generate_new_value(last_value: int) -> int:
    # değeri asla azaltmadan, küçük rastgele bir artış ekler
    increment = random.randint(0, 5)
    return int(last_value + increment)


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
    names = get_university_names()
    gunluk_df = pd.read_csv(GUNLUK_OZET_PATH)
    last_values = load_last_values(gunluk_df, names)

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    records = []
    for uni in names:
        new_value = generate_new_value(last_values[uni])
        records.append({
            "timestamp": timestamp_str,
            "university": uni,
            "value": new_value,
        })

    append_to_ham_log(records)
    update_gunluk_ozet(records, today_str)

    print(f"{len(records)} üniversite için veri güncellendi. Zaman: {timestamp_str}")