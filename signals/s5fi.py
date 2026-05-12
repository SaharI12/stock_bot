import yfinance as yf
import pandas as pd


SP500_TICKERS_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def get_sp500_tickers() -> list[str]:
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
    Downloads all tickers in a single batch for speed.
    """
    tickers = get_sp500_tickers()
    if not tickers:
        return None

    try:
        data = yf.download(
            tickers,
            period="60d",
            interval="1d",
            progress=False,
            threads=True,
            auto_adjust=True,
        )
        closes = data["Close"] if isinstance(data.columns, pd.MultiIndex) else data[["Close"]].rename(columns={"Close": tickers[0]})
    except Exception as e:
        print(f"[s5fi] Download error: {e}")
        return None

    above = 0
    total = 0
    for ticker in tickers:
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

    if total == 0:
        return None

    s5fi = round((above / total) * 100, 2)
    print(f"[s5fi] {above}/{total} stocks above 50MA = {s5fi}%")
    return s5fi


def check_s5fi(s5fi: float) -> bool:
    if s5fi is None:
        return False
    return s5fi < 20


def check_sell_s5fi(s5fi: float) -> bool:
    if s5fi is None:
        return False
    return s5fi > 80
