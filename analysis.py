import pandas as pd

def load_gunluk_ozet(filepath: str = "data/gunluk_ozet.csv") -> pd.DataFrame:
    # günlük özet verisini okur, tarihi gerçek tarih tipine çevirir
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_monthly_averages(df: pd.DataFrame, university_name: str) -> list:
    # bir üniversitenin ay ay ortalama değerini hesaplar
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


def generate_report(df: pd.DataFrame, months_back: int = 3) -> dict:
    university_names = df["university"].unique()

    results = []
    for uni in university_names:
        result = calculate_change_pct(df, uni, months_back)
        results.append(result)

    ranked = sorted(results, key=lambda r: r["change_pct"], reverse=True)

    return {
        "universities": results,
        "top_gainers": ranked[:5],
        "bottom_gainers": ranked[-5:],
    }