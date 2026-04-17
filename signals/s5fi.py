import yfinance as yf
import pandas as pd


SP500_TICKERS_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def get_sp500_tickers() -> list[str]:
    """Scrape S&P 500 tickers from Wikipedia."""
    try:
        tables = pd.read_html(SP500_TICKERS_URL, storage_options={"User-Agent": "Mozilla/5.0"})
        df = tables[0]
        tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
        return tickers
    except Exception as e:
        print(f"[s5fi] Failed to fetch tickers: {e}")
        return []


def get_s5fi() -> float | None:
    """
    Calculate S5FI: % of S&P 500 stocks trading above their 50-day SMA.
    Downloads in batches to avoid rate limits.
    """
    tickers = get_sp500_tickers()
    if not tickers:
        return None

    above = 0
    total = 0

    # Download in batches of 50
    batch_size = 50
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i: i + batch_size]
        try:
            data = yf.download(
                batch,
                period="60d",
                interval="1d",
                progress=False,
                threads=True,
                auto_adjust=True,
            )
            closes = data["Close"] if "Close" in data.columns else data.xs("Close", axis=1, level=0)
            for ticker in batch:
                if ticker not in closes.columns:
                    continue
                series = closes[ticker].dropna()
                if len(series) < 50:
                    continue
                sma50 = series.rolling(50).mean().iloc[-1]
                last_close = series.iloc[-1]
                total += 1
                if last_close > sma50:
                    above += 1
        except Exception as e:
            print(f"[s5fi] Batch {i} error: {e}")
            continue

    if total == 0:
        return None

    s5fi = round((above / total) * 100, 2)
    print(f"[s5fi] {above}/{total} stocks above 50MA = {s5fi}%")
    return s5fi


def check_s5fi(s5fi: float) -> bool:
    """Rule fires when S5FI < 20 (fewer than 20% of stocks above 50MA)."""
    if s5fi is None:
        return False
    return s5fi < 20
