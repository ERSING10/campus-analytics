import pandas as pd

# veri okuma

def load_gunluk_ozet(filepath: str = "data/gunluk_ozet.csv") -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])
    return df


# veri isleme

def get_monthly_averages(df: pd.DataFrame, university_name: str) -> list:
    # ay ay ort hesabı
    uni_df = df[df["university"] == university_name].copy()
    uni_df["year_month"] = uni_df["date"].dt.to_period("M")

    averages = []
    for period, group in uni_df.groupby("year_month"):
        avg_val = group["value"].mean()
        averages.append({
            "month": str(period),
            "avg_value": float(round(avg_val, 2)),
            "day_count": int(len(group)),
        })
    return averages


def get_value_n_days_ago(df: pd.DataFrame, university_name: str, n: int):
    uni_df = df[df["university"] == university_name]
    if uni_df.empty:
        return None

    latest_date = uni_df["date"].max()
    target_date = latest_date - pd.Timedelta(days=n)

    past_rows = uni_df[uni_df["date"] <= target_date]
    if past_rows.empty:
        return None

    past_rows_sorted = past_rows.sort_values("date")
    closest_row = past_rows_sorted.iloc[-1]
    return closest_row["value"]

# hesaplama analiz

def calculate_change_pct(df: pd.DataFrame, university_name: str, months_back: int = 3) -> dict:
    monthly = get_monthly_averages(df, university_name)

    if len(monthly) <= months_back:
        old = monthly[0]
    else:
        old = monthly[-(months_back + 1)]
    new = monthly[-1]

    old_val = old["avg_value"]
    new_val = new["avg_value"]
    change_pct = (new_val - old_val) / old_val * 100 if old_val else 0.0

    return {
        "university": university_name,
        "old_month": old["month"],
        "old_value": old_val,
        "new_month": new["month"],
        "new_value": new_val,
        "change_pct": float(round(change_pct, 2)),
        "monthly_breakdown": monthly,
    }


def calculate_n_day_change(df: pd.DataFrame, university_name: str, n: int) -> dict:
    uni_df = df[df["university"] == university_name]
    uni_df_sorted = uni_df.sort_values("date")
    latest_value = uni_df_sorted.iloc[-1]["value"]

    old_value = get_value_n_days_ago(df, university_name, n)
    if old_value is None:
        return {"change_pct": None, "note": f"{n} günlük veri henüz yetersiz"}

    change_pct = (latest_value - old_value) / old_value * 100 if old_value else 0.0
    return {
        "change_pct": float(round(change_pct, 4)),
        "old_value": float(old_value),
        "new_value": float(latest_value),
    }


def get_latest_raw_value(df: pd.DataFrame, university_name: str) -> dict:
    # ortalama değil, o üniversitenin en son çekilen ham (gerçek) sayısı
    uni_df = df[df["university"] == university_name].sort_values("date")
    last_row = uni_df.iloc[-1]
    return {
        "date": str(last_row["date"].date()),
        "value": int(last_row["value"]),
    }


def calculate_momentum(change_10: dict, change_30: dict) -> dict:
    if change_10["change_pct"] is None or change_30["change_pct"] is None:
        return {"momentum": None, "note": "yetersiz veri"}

    momentum = change_10["change_pct"] - change_30["change_pct"]
    return {"momentum": float(round(momentum, 4))}


def get_closest_rivals(universities: list, n: int = 3) -> dict:
    kocaeli = next((u for u in universities if u["university"] == "Kocaeli Üniversitesi"), None)
    if kocaeli is None:
        return {"kocaeli": None, "above": [], "below": []}

    sirali = sorted(universities, key=lambda u: u["new_value"], reverse=True)
    kocaeli_index = next(i for i, u in enumerate(sirali) if u["university"] == "Kocaeli Üniversitesi")

    ustundekiler = sirali[max(0, kocaeli_index - n):kocaeli_index]
    altındakiler = sirali[kocaeli_index + 1: kocaeli_index + 1 + n]

    return {
        "kocaeli": kocaeli,
        "above": list(reversed(ustundekiler)),  # en yakın üstteki en başta
        "below": altındakiler,
        "sira": kocaeli_index + 1,
        "toplam": len(sirali),
    }



# rapor

def generate_report(df: pd.DataFrame, months_back: int = 3) -> dict:
    university_names = df["university"].unique()

    results = []
    for uni in university_names:
        result = calculate_change_pct(df, uni, months_back)
        result["change_10d"] = calculate_n_day_change(df, uni, 10)
        result["change_30d"] = calculate_n_day_change(df, uni, 30)
        result["momentum"] = calculate_momentum(result["change_10d"], result["change_30d"])
        result["latest"] = get_latest_raw_value(df, uni)
        results.append(result)

    ranked = sorted(results, key=lambda r: r["change_pct"], reverse=True)
    closest_rivals = get_closest_rivals(results, n=3)


    return {
        "universities": results,
        "top_gainers": ranked[:5],
        "bottom_gainers": ranked[-5:],
        "closest_rivals": closest_rivals,
    }