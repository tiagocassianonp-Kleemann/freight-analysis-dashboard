def add_indicators(df):
    df = df.sort_values("date")

    df["ma_7"] = df["price"].rolling(7).mean()
    df["ma_30"] = df["price"].rolling(30).mean()

    df["pct_change"] = df["price"].pct_change()
    df["volatility"] = df["pct_change"].rolling(7).std()

    return df