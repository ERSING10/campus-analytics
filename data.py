import pandas as pd

# url alıyor ve csv kullanarak pandas DataFrame döndürüyor
def load_data(csv_url: str) -> pd.DataFrame:
    df = pd.read_csv(csv_url)
    return df

# üniversite ismi ile satır döndürüyor, eğer yoksa ValueError yazar
def get_university_row (df: pd.DataFrame, university_name: str):
    col_name = df.columns[0]
    result = df[df[col_name] == university_name]
    if result.empty:
        raise ValueError(f"University '{university_name}' not found in the DataFrame.")
    return result.iloc[0]