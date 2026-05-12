import yfinance as yf
import pandas as pd


def get_index_prices() -> dict:
    """Fetch latest closing prices for QQQ, Dow Jones, and Russell 2000."""
    try:
        data = yf.download(["QQQ", "^DJI", "^RUT"], period="5d", auto_adjust=True, progress=False)
        closes = data["Close"] if isinstance(data.columns, pd.MultiIndex) else data
        return {
            "QQQ": round(float(closes["QQQ"].dropna().iloc[-1]), 2),
            "DJIA": int(round(float(closes["^DJI"].dropna().iloc[-1]))),
            "RUT": round(float(closes["^RUT"].dropna().iloc[-1]), 2),
        }
    except Exception as e:
        print(f"[indices] Error: {e}")
        return {"QQQ": None, "DJIA": None, "RUT": None}
