import yfinance as yf
import pandas as pd


def get_vix() -> dict:
    """Fetch latest and previous VIX closing values."""
    try:
        data = yf.download("^VIX", period="10d", auto_adjust=True, progress=False)
        if data is None or data.empty:
            return {"value": None, "prev": None}
        close = data["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        close = close.dropna()
        value = round(float(close.iloc[-1]), 2)
        prev = round(float(close.iloc[-2]), 2) if len(close) >= 2 else None
        return {"value": value, "prev": prev}
    except Exception as e:
        print(f"[vix] Error: {e}")
        return {"value": None, "prev": None}


def check_vix(vix_val: float) -> bool:
    if vix_val is None:
        return False
    return vix_val >= 30


def check_sell_vix(vix_val: float) -> bool:
    if vix_val is None:
        return False
    return vix_val < 15
