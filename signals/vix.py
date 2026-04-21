import yfinance as yf
import pandas as pd


def get_vix() -> float | None:
    """Fetch latest VIX closing value."""
    try:
        data = yf.download("^VIX", period="5d", auto_adjust=True, progress=False)
        if data is None or data.empty:
            return None
        close = data["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        return round(float(close.iloc[-1]), 2)
    except Exception as e:
        print(f"[vix] Error: {e}")
        return None


def check_vix(vix: float) -> bool:
    """Rule fires when VIX >= 30."""
    if vix is None:
        return False
    return vix >= 30
