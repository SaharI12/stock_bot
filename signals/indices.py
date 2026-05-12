import yfinance as yf
import pandas as pd


def get_index_prices() -> dict:
    """
    Fetch price, daily % change, and % vs 150-day MA for QQQ, DJIA, and RUT.
    Returns a dict keyed by QQQ / DJIA / RUT.
    """
    try:
        data = yf.download(["QQQ", "^DJI", "^RUT"], period="200d", auto_adjust=True, progress=False)
        closes = data["Close"] if isinstance(data.columns, pd.MultiIndex) else data

        result = {}
        for ticker, key in [("QQQ", "QQQ"), ("^DJI", "DJIA"), ("^RUT", "RUT")]:
            series = closes[ticker].dropna()
            if len(series) < 2:
                result[key] = {"price": None, "pct_change": None, "vs_150ma": None}
                continue

            price = float(series.iloc[-1])
            prev = float(series.iloc[-2])
            pct_change = round((price - prev) / prev * 100, 2)

            sma150 = series.iloc[-150:].mean() if len(series) >= 150 else None
            vs_150ma = round((price - sma150) / sma150 * 100, 1) if sma150 else None

            price_rounded = int(round(price)) if key == "DJIA" else round(price, 2)
            result[key] = {"price": price_rounded, "pct_change": pct_change, "vs_150ma": vs_150ma}

        return result
    except Exception as e:
        print(f"[indices] Error: {e}")
        return {k: {"price": None, "pct_change": None, "vs_150ma": None} for k in ["QQQ", "DJIA", "RUT"]}
