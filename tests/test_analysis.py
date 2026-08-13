import pandas as pd
import pytest

from campus_analytics.processing.analysis import (
    get_monthly_averages,
    calculate_change_pct,
    get_value_n_days_ago,
    calculate_n_day_change,
    get_latest_raw_value,
    calculate_momentum,
    get_closest_rivals,
)


@pytest.fixture
def ornek_veri():
    satirlar = [
        {"date": "2026-06-01", "university": "Kocaeli Üniversitesi", "value": 1000},
        {"date": "2026-06-15", "university": "Kocaeli Üniversitesi", "value": 1050},
        {"date": "2026-07-01", "university": "Kocaeli Üniversitesi", "value": 1100},
        {"date": "2026-08-01", "university": "Kocaeli Üniversitesi", "value": 1200},

        {"date": "2026-06-01", "university": "Ankara Üniversitesi", "value": 2000},
        {"date": "2026-08-01", "university": "Ankara Üniversitesi", "value": 2100},

        {"date": "2026-06-01", "university": "Fırat Üniversitesi", "value": 900},
        {"date": "2026-08-01", "university": "Fırat Üniversitesi", "value": 950},
    ]
    df = pd.DataFrame(satirlar)
    df["date"] = pd.to_datetime(df["date"])
    return df


# ay sayısı doğru mu
def test_ay_sayisi(ornek_veri):
    aylar = get_monthly_averages(ornek_veri, "Kocaeli Üniversitesi")
    assert len(aylar) == 3


# ortalama doğru hesaplanıyor mu
def test_ay_ortalamasi(ornek_veri):
    aylar = get_monthly_averages(ornek_veri, "Kocaeli Üniversitesi")
    haziran = aylar[0]
    assert haziran["avg_value"] == 1025.0


# artan veride yüzde pozitif mi
def test_degisim_pozitif(ornek_veri):
    sonuc = calculate_change_pct(ornek_veri, "Kocaeli Üniversitesi", months_back=3)
    assert sonuc["change_pct"] > 0


# geçmiş değer bulunuyor mu
def test_gecmis_deger_bulunur(ornek_veri):
    deger = get_value_n_days_ago(ornek_veri, "Kocaeli Üniversitesi", n=30)
    assert deger is not None


# olmayan üniversite None dönüyor mu
def test_olmayan_uni_none_doner(ornek_veri):
    deger = get_value_n_days_ago(ornek_veri, "Olmayan Üniversite", n=10)
    assert deger is None

# yetersiz veri notu doğru mu
def test_yetersiz_veri_notu(ornek_veri):
    tek_kayit = pd.DataFrame([
        {"date": pd.Timestamp("2026-08-01"), "university": "Fırat Üniversitesi", "value": 950}
    ])

    sonuc = calculate_n_day_change(tek_kayit, "Fırat Üniversitesi", n=10)
    assert sonuc["change_pct"] is None
    assert "yetersiz" in sonuc["note"]

# en son kayıt doğru mu
def test_son_kayit_dogru(ornek_veri):
    sonuc = get_latest_raw_value(ornek_veri, "Kocaeli Üniversitesi")
    assert sonuc["value"] == 1200
    assert sonuc["date"] == "2026-08-01"


# eksik veride momentum None mu
def test_momentum_eksik_veri():
    change_10 = {"change_pct": None}
    change_30 = {"change_pct": 5.0}
    sonuc = calculate_momentum(change_10, change_30)
    assert sonuc["momentum"] is None


# momentum hesabı doğru mu
def test_momentum_hesabi():
    change_10 = {"change_pct": 8.0}
    change_30 = {"change_pct": 5.0}
    sonuc = calculate_momentum(change_10, change_30)
    assert sonuc["momentum"] == 3.0


# kocaeli doğru bulunuyor mu
def test_kocaeli_bulunur():
    universities = [
        {"university": "Ankara Üniversitesi", "new_value": 2000},
        {"university": "Kocaeli Üniversitesi", "new_value": 1200},
        {"university": "Fırat Üniversitesi", "new_value": 950},
    ]
    sonuc = get_closest_rivals(universities, n=3)
    print("DEBUG sonuc:", sonuc)
    assert sonuc["kocaeli"]["university"] == "Kocaeli Üniversitesi"
    assert sonuc["sira"] == 2
    assert sonuc["toplam"] == 3