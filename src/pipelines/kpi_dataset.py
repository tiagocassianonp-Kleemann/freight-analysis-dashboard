import pandas as pd
import glob
from datetime import datetime

from src.utils.storage import save_csv
from src.config import PROCESSED_PATH


def load_latest():
    files = glob.glob(f"{PROCESSED_PATH}/freight_dataset_*.csv")
    
    if not files:
        raise Exception("Dataset consolidado não encontrado")
    
    latest = max(files)
    return pd.read_csv(latest)


def run():
    print("📊 Building KPI dataset")

    df = load_latest()

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # 📈 Variação percentual
    df["freight_change"] = df["freight"].pct_change()
    df["brent_change"] = df["brent"].pct_change()
    df["bdi_change"] = df["bdi"].pct_change()
    df["usd_change"] = df["usd"].pct_change()

    # 📊 Médias móveis
    df["freight_ma7"] = df["freight"].rolling(7).mean()
    df["freight_ma30"] = df["freight"].rolling(30).mean()

    # 🔥 Volatilidade
    df["freight_volatility"] = df["freight_change"].rolling(7).std()

    # 🚨 Sinal de tendência
    df["trend_signal"] = df["freight_ma7"] > df["freight_ma30"]

    # 🧠 Score de pressão de freight (custom KPI)
    df["freight_pressure"] = (
        df["bdi_change"] * 0.5 +
        df["brent_change"] * 0.3 +
        df["usd_change"] * 0.2
    )

    # 🔴 Classificação
    def classify(x):
        if x > 0.02:
            return "Alta"
        elif x < -0.02:
            return "Queda"
        else:
            return "Estável"

    df["market_status"] = df["freight_pressure"].apply(classify)

    # salvar
    today = datetime.today().date()
    save_csv(df, PROCESSED_PATH, f"freight_kpi_dataset_{today}.csv")

    print("✅ KPI dataset ready")