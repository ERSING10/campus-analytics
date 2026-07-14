import pandas as pd

def get_monthly_averages(row: pd.Series, df: pd.DataFrame) -> list:
    """Her ay için o üniversitenin günlük değerlerinin ortalamasını hesaplar."""
    date_cols = df.columns[1:]
    dates = pd.to_datetime(date_cols, format='%d.%m.%Y')
    df_dates = pd.DataFrame({'col': date_cols, 'date': dates})
    df_dates['year_month'] = df_dates['date'].dt.to_period('M')

    averages = []
    for period, group in df_dates.groupby('year_month'):
        cols = group['col']
        avg_val = row[cols].astype(float).mean()
        averages.append({
            "month": str(period),
            "avg_value": float(round(avg_val, 2)),
            "day_count": int(len(cols)),
        })
    return averages  # groupby period'a göre otomatik kronolojik sıralı gelir


def calculate_change_pct(row: pd.Series, df: pd.DataFrame, months_back: int = 3) -> dict:
    """Aylık ortalamalara göre, months_back kadar ay önceki durum ile şimdiki durumu kıyaslar."""
    monthly = get_monthly_averages(row, df)

    if len(monthly) <= months_back:
        old = monthly[0]  # yeterli ay yoksa elimizdeki en eski ayı kullan
    else:
        old = monthly[-(months_back + 1)]
    new = monthly[-1]

    old_val = old["avg_value"]
    new_val = new["avg_value"]
    change_pct = (new_val - old_val) / old_val * 100 if old_val else 0.0

    return {
        "university": row[df.columns[0]],
        "old_month": old["month"],
        "old_value": old_val,
        "new_month": new["month"],
        "new_value": new_val,
        "change_pct": float(round(change_pct, 2)),
        "monthly_breakdown": monthly,
    }


def generate_report(df: pd.DataFrame, months_back: int = 3) -> dict:
    """Tüm üniversiteler için rapor üretir, en çok/az artanları da ekler."""
    from data import get_university_row

    results = []
    for uni_name in df[df.columns[0]]:
        row = get_university_row(df, uni_name)
        result = calculate_change_pct(row, df, months_back)
        results.append(result)

    ranked = sorted(results, key=lambda r: r["change_pct"], reverse=True)

    return {
        "universities": results,
        "top_gainers": ranked[:5],
        "bottom_gainers": ranked[-5:],
    }