import os

def save_csv(df, path, filename):
    os.makedirs(path, exist_ok=True)
    full_path = f"{path}/{filename}"

    df.to_csv(full_path, index=False)
    print(f"✅ Saved: {full_path}")