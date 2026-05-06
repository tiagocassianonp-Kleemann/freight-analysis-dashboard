import yfinance as yf
from datetime import datetime

from src.utils.indicators import add_indicators
from src.utils.storage import save_csv
from src.config import RAW_PATH, PROCESSED_PATH


def extract():
    # proxy de freight (shipping ETF)
    df = yf.download("SEA", period="1y", interval="1d")
    df.reset_index(inplace=True)
    return df


def transform(df):
    df = df[["Date", "Close"]]
    df.columns = ["date", "price"]
    return df


def load(df_raw, df_processed):
    today = datetime.today().date()

    save_csv(df_raw, RAW_PATH, f"freight_raw_{today}.csv")
    save_csv(df_processed, PROCESSED_PATH, f"freight_processed_{today}.csv")


def run():
    print("📦 Running Freight pipeline (SEA proxy)")

    raw = extract()
    df = transform(raw)
    df = add_indicators(df)

    load(raw, df)

    print("✅ Freight pipeline done")