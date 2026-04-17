import yfinance as yf


def get_vix() -> float | None:
    """Fetch latest VIX closing value."""
    try:
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="5d")
        if hist is None or hist.empty:
            return None
        return round(float(hist["Close"].iloc[-1]), 2)
    except Exception as e:
        print(f"[vix] Error: {e}")
        return None


def check_vix(vix: float) -> bool:
    """Rule fires when VIX >= 30."""
    if vix is None:
        return False
    return vix >= 30
