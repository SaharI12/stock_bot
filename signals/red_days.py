import yfinance as yf


def get_spy_closes(n_days: int = 10) -> list[float]:
    """Fetch last N closing prices for SPY."""
    try:
        spy = yf.Ticker("SPY")
        hist = spy.history(period=f"{n_days + 10}d")
        if hist is None or hist.empty:
            return []
        closes = hist["Close"].dropna().tolist()
        return closes[-n_days:]
    except Exception as e:
        print(f"[red_days] Error: {e}")
        return []


def count_consecutive_red_days(closes: list[float]) -> int:
    """Count how many consecutive red days ending on the latest close."""
    if len(closes) < 2:
        return 0
    count = 0
    # Walk backwards from latest day
    for i in range(len(closes) - 1, 0, -1):
        if closes[i] < closes[i - 1]:
            count += 1
        else:
            break
    return count


def check_red_days(closes: list[float]) -> bool:
    """Rule fires when there are exactly 3+ consecutive red days."""
    return count_consecutive_red_days(closes) >= 3
