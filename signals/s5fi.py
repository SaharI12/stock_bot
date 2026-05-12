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


def get_s5fi() -> dict:
    """
    Calculate S5FI: % of S&P 500 stocks above their 50-day SMA, for today and yesterday.
    Downloads all tickers in a single batch for speed.
    """
    tickers = get_sp500_tickers()
    if not tickers:
        return {"value": None, "prev": None}

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
        return {"value": None, "prev": None}

    above_today = 0
    above_prev = 0
    total_today = 0
    total_prev = 0

    for ticker in tickers:
        if ticker not in closes.columns:
            continue
        series = closes[ticker].dropna()
        sma = series.rolling(50).mean()

        if len(series) >= 50:
            total_today += 1
            if series.iloc[-1] > sma.iloc[-1]:
                above_today += 1

        if len(series) >= 51:
            total_prev += 1
            if series.iloc[-2] > sma.iloc[-2]:
                above_prev += 1

    value = round((above_today / total_today) * 100, 2) if total_today else None
    prev = round((above_prev / total_prev) * 100, 2) if total_prev else None

    print(f"[s5fi] today {above_today}/{total_today} = {value}%  |  prev {above_prev}/{total_prev} = {prev}%")
    return {"value": value, "prev": prev}


def check_s5fi(s5fi_val: float) -> bool:
    if s5fi_val is None:
        return False
    return s5fi_val < 20


def check_sell_s5fi(s5fi_val: float) -> bool:
    if s5fi_val is None:
        return False
    return s5fi_val > 80
