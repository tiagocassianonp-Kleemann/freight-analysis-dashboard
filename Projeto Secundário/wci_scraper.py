# =========================================
# WCI PIPELINE (VERSÃO FINAL CORRIGIDA)
# =========================================

import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
WEEKLY_FILE = os.path.join(BASE_PATH, "wci_weekly.csv")

SEED_FILE = r"C:\Users\tiago\OneDrive\Desktop\wci_project\Projeto Secundário\Excel Data - Past Seed.xlsx"


# ==============================
# PARSER UNIVERSAL (CRÍTICO)
# ==============================
def parse_wci_value(x):
    if pd.isna(x):
        return None

    x = str(x).strip().upper()

    # Caso: 2,35K ou 2.35K
    if "K" in x:
        x = x.replace("K", "").replace(",", ".")
        return float(x) * 1000

    # Caso: 2,35
    if "," in x:
        x = x.replace(",", ".")

    try:
        return float(x)
    except:
        return None


# ==============================
# LOAD HISTÓRICO
# ==============================
def load_history():

    if os.path.exists(WEEKLY_FILE):
        df = pd.read_csv(WEEKLY_FILE, encoding="utf-8-sig")
    else:
        df = pd.DataFrame(columns=["date", "global_index"])

    df.columns = df.columns.str.strip().str.replace(" ", "_")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["global_index"] = df["global_index"].apply(parse_wci_value)

    df = df.dropna(subset=["date", "global_index"])

    # 🔥 Corrige valores inflados
    df["global_index"] = df["global_index"].apply(
        lambda x: x / 10 if x > 10000 else x
    )

    return df

# ==============================
# LOAD SEED
# ==============================
def load_seed():

    if not os.path.exists(SEED_FILE):
        raise Exception(f"🚨 Seed não encontrado: {SEED_FILE}")

    xls = pd.ExcelFile(SEED_FILE)
    print(f"📄 Abas: {xls.sheet_names}")

    df_seed = None

    for sheet in xls.sheet_names:

        # 🔥 LEITURA CONTROLADA (sem interpretação automática)
        df_temp = pd.read_excel(SEED_FILE, sheet_name=sheet, dtype=str)

        if df_temp.shape[1] >= 2:
            df_seed = df_temp
            print(f"✅ Usando aba: {sheet}")
            break

    if df_seed is None:
        raise Exception("🚨 Nenhuma aba válida encontrada")

    # 🔹 Padroniza colunas
    df_seed.columns = df_seed.columns.astype(str).str.strip().str.lower()

    date_col = [c for c in df_seed.columns if "date" in c][0]
    value_col = [c for c in df_seed.columns if "index" in c or "value" in c][0]

    df_seed = df_seed[[date_col, value_col]]
    df_seed.columns = ["date", "global_index"]

    # 🔹 Converte data
    df_seed["date"] = pd.to_datetime(df_seed["date"], errors="coerce")

    # 🔥 TRATAMENTO ROBUSTO DE NÚMERO
    df_seed["global_index"] = (
        df_seed["global_index"]
        .astype(str)
        .str.replace("K", "", regex=False)   # remove K se existir
        .str.replace(".", "", regex=False)   # remove separador de milhar
        .str.replace(",", ".", regex=False)  # ajusta decimal pt-BR
        .str.strip()
    )

    df_seed["global_index"] = pd.to_numeric(df_seed["global_index"], errors="coerce")

    # 🔥 PROTEÇÃO FINAL (caso ainda venha inflado)
    df_seed["global_index"] = df_seed["global_index"].apply(
        lambda x: x / 10 if x > 10000 else x
    )

    # 🔹 Remove inválidos
    df_seed = df_seed.dropna(subset=["date", "global_index"])

    # 🔍 DEBUG (IMPORTANTÍSSIMO AGORA)
    print("\n🔎 DEBUG SEED:")
    print(df_seed.head())
    print(df_seed["global_index"].describe())

    return df_seed


# ==============================
# MERGE
# ==============================
def merge_seed(df_hist):

    df_seed = load_seed()

    df = pd.concat([df_seed, df_hist])
    df = df.sort_values("date")
    df = df.drop_duplicates(subset=["date"], keep="last")

    print(f"📊 Após merge: {len(df)} linhas")

    return df


# ==============================
# CLEAN (ESCALA REAL)
# ==============================
def clean_history(df):

    df = df.copy()

    # 🔥 Remove valores impossíveis
    df = df[(df["global_index"] >= 1000) & (df["global_index"] <= 6000)]

    # 🔥 Remove saltos absurdos
    df["diff"] = df["global_index"].diff().abs()
    df = df[(df["diff"].isna()) | (df["diff"] < 1500)]

    df = df.drop(columns=["diff"])

    return df


# ==============================
# INPUT
# ==============================
def get_wci_value():
    valor = float(input("\n👉 Digite o WCI mais recente (ex: 2350): "))
    return valor


# ==============================
# UPDATE
# ==============================
def update_timeseries(df, valor):

    hoje = pd.Timestamp.today().normalize()

    df_novo = pd.DataFrame({
        "date": [hoje],
        "global_index": [valor]
    })

    df = pd.concat([df, df_novo])
    df = df.sort_values("date")
    df = df.drop_duplicates(subset=["date"], keep="last")

    return df


# ==============================
# SAVE
# ==============================
def save_data(df, df_antigo):

    if df.empty:
        raise Exception("🚨 Tentativa de salvar vazio")

    if len(df_antigo) > 0 and len(df) < len(df_antigo):
        print("⚠️ Limpeza aplicada no histórico")

    # 🔥 REMOVE .0 DEFINITIVAMENTE
    df["global_index"] = df["global_index"].astype(int)

    if os.path.exists(WEEKLY_FILE):
        backup = WEEKLY_FILE.replace(".csv", "_backup.csv")
        os.replace(WEEKLY_FILE, backup)

    df.to_csv(WEEKLY_FILE, index=False, encoding="utf-8-sig")

    print("📁 CSV salvo com segurança")

# ==============================
# PIPELINE
# ==============================
def run_pipeline():

    print(f"📁 Seed existe? {os.path.exists(SEED_FILE)}")

    df_hist = load_history()
    print(f"📊 Histórico inicial: {len(df_hist)}")

    df = merge_seed(df_hist)

    # 🔥 CORREÇÃO FINAL (apenas uma vez!)
    df["global_index"] = df["global_index"].apply(
        lambda x: x / 10 if x > 10000 else x
    )

    df = clean_history(df)

    # 🔥 ALERTA INTELIGENTE
    if (df["global_index"] < 1000).any():
        print("🚨 ALERTA: valores suspeitos detectados!")

    valor = get_wci_value()

    df_final = update_timeseries(df, valor)

    # 🔥 GARANTIA FINAL (antes de salvar)
    df_final["global_index"] = df_final["global_index"].apply(
        lambda x: x / 10 if x > 10000 else x
    )

    save_data(df_final, df_hist)

    print("\n✅ Pipeline finalizado")
    print(df_final.tail())


# ==============================
# EXEC
# ==============================
if __name__ == "__main__":
    run_pipeline()