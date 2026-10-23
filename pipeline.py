import os
import requests
import pandas as pd

URL = "https://data.cityofchicago.org/resource/5neh-572f.json"


def extract(start_date="2023-01-01"):
    """Download daily ridership rows from the Chicago Data Portal API."""
    params = {
        "$where": f"date >= '{start_date}'",
        "$order": "date",
        "$limit": 500000,
    }
    response = requests.get(URL, params=params, timeout=60)
    response.raise_for_status()
    df = pd.DataFrame(response.json())
    print(f"Extracted {len(df):,} rows. Columns: {list(df.columns)}")
    return df


def transform(df):
    """Clean types, rename columns, and remove bad rows."""
    df = df.rename(columns={"stationname": "station_name", "daytype": "day_type"})
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["rides"] = pd.to_numeric(df["rides"], errors="coerce")
    df = df.dropna(subset=["rides"]).drop_duplicates()
    df["rides"] = df["rides"].astype(int)
    df["day_type"] = df["day_type"].map(
        {"W": "Weekday", "A": "Saturday", "U": "Sunday/Holiday"}
    )
    df = df[["station_id", "station_name", "date", "day_type", "rides"]]
    print(f"Clean rows: {len(df):,}")
    return df


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    raw = extract()
    clean = transform(raw)
    clean.to_csv("data/cta_ridership.csv", index=False)
    print("Saved data/cta_ridership.csv")
