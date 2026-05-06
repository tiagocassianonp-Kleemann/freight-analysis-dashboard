import pandas as pd
import glob
from datetime import datetime

from src.utils.storage import save_csv
from src.config import PROCESSED_PATH


def load_latest(pattern):
    files = glob.glob(pattern)

    if not files:
        raise Exception(f"Nenhum arquivo encontrado para: {pattern}")

    latest = max(files)
    return pd.read_csv(latest)


def get_price_column(df, name):
    if "price" in df.columns:
        return "price"
    elif "Close" in df.columns:
        return "Close"
    else:
        raise Exception(f"Coluna de preço não encontrada em {name}: {df.columns}")


def run():
    print("🧠 Running consolidation pipeline")

    brent = load_latest(f"{PROCESSED_PATH}/brent_processed_*.csv")
    bdi = load_latest(f"{PROCESSED_PATH}/bdi_processed_*.csv")
    freight = load_latest(f"{PROCESSED_PATH}/freight_processed_*.csv")
    usd = load_latest(f"{PROCESSED_PATH}/usd_processed_*.csv")

    brent = brent[["date", get_price_column(brent, "brent")]].rename(
        columns={get_price_column(brent, "brent"): "brent"}
    )

    bdi = bdi[["date", get_price_column(bdi, "bdi")]].rename(
        columns={get_price_column(bdi, "bdi"): "bdi"}
    )

    freight = freight[["date", get_price_column(freight, "freight")]].rename(
        columns={get_price_column(freight, "freight"): "freight"}
    )

    usd = usd[["date", get_price_column(usd, "usd")]].rename(
        columns={get_price_column(usd, "usd"): "usd"}
    )

    df = brent.merge(bdi, on="date", how="outer")
    df = df.merge(freight, on="date", how="outer")
    df = df.merge(usd, on="date", how="outer")

    df = df.sort_values("date")

    today = datetime.today().date()
    save_csv(df, PROCESSED_PATH, f"freight_dataset_{today}.csv")

    print("✅ Consolidation done")