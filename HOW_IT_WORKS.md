# How Dip Radar Works — A Learning Guide

This document explains every part of the project: what each file does, what each function does, and the reasoning behind how it was built.

---

## The Big Picture

The bot answers one question every weekday afternoon:
> "Is the market in a dip right now?"

It checks 4 indicators, counts how many are triggered, and sends you a Telegram message with the result. It runs automatically on GitHub's servers — no PC needed.

---

## Project Flow

```
GitHub Actions (cron)
        ↓
    main.py
        ↓
  signals/engine.py  ← coordinates all 4 checks
        ↓
  ┌─────────────────────────────────┐
  │ fear_greed.py  vix.py           │
  │ s5fi.py        red_days.py      │
  └─────────────────────────────────┘
        ↓
  bot/telegram_alert.py  ← formats + sends message
```

---

## File-by-File Breakdown

---

### `main.py` — Entry Point

This is the file Python runs first. It:
1. Loads the `.env` file so the Telegram credentials are available
2. Calls `run_engine()` to get the full report
3. Prints the results to the console
4. Calls `send_telegram()` to send the message

```python
from dotenv import load_dotenv
load_dotenv()  # reads .env file and sets environment variables
```

**Why `sys.path.insert`?**
This tells Python to look for modules in the current folder first.
Without it, `from signals.engine import ...` might fail if Python doesn't know where to look.

```python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
```
This fixes a Windows bug where emojis (like 🔵) cause a crash because the default Windows terminal uses an old encoding that doesn't support them.

---

### `signals/engine.py` — The Brain

This file coordinates all 4 signals and builds the final report.

**`get_signal_level(score)`**
Takes the number of triggered rules (0–4) and returns a human-readable label:
- 4 → EXTREME BUY
- 3 → STRONG BUY
- 2 → WATCH
- 1 → MILD
- 0 → HOLD

**`run_engine()`**
Calls each signal module, evaluates each rule, adds up the score, and returns a dictionary with all the data. A dictionary is used so the Telegram formatter can easily loop through the results.

---

### `signals/fear_greed.py` — CNN Fear & Greed Index

The Fear & Greed index is a score from 0–100:
- 0–24 = Extreme Fear
- 75–100 = Extreme Greed

**`get_fear_greed()`**
Makes an HTTP request to CNN's internal API and extracts the score and label.

```python
headers = {
    "User-Agent": "Mozilla/5.0 ...",
    "Referer": "https://edition.cnn.com/",
}
```
CNN blocks automated requests. By sending headers that make the request look like a real browser visit, we bypass the block. The `Referer` header makes it look like we came from CNN's own website.

**`check_fear_greed(score)`**
Returns `True` only if score < 10 — that's deep Extreme Fear territory, historically a strong buy signal.

---

### `signals/vix.py` — Volatility Index

VIX measures how much fear/uncertainty is priced into the options market. Above 30 = high fear = potential dip.

**`get_vix()`**
Uses the `yfinance` library to fetch VIX data. `^VIX` is the ticker symbol for the VIX index on Yahoo Finance. We fetch 5 days and take the latest close.

```python
hist["Close"].iloc[-1]  # .iloc[-1] means "last row"
```

**`check_vix(vix)`**
Returns `True` if VIX >= 30.

---

### `signals/s5fi.py` — S&P 500 Breadth

S5FI = what % of S&P 500 stocks are trading above their 50-day moving average.
- Above 80% = healthy market
- Below 20% = very unhealthy, most stocks in downtrend

**`get_sp500_tickers()`**
Scrapes the list of S&P 500 companies from Wikipedia using `pd.read_html()`, which reads HTML tables directly into a DataFrame.

```python
storage_options={"User-Agent": "Mozilla/5.0"}
```
Wikipedia blocks requests without a browser User-Agent, so we pass one.

**`get_s5fi()`**
Downloads price data for all ~500 stocks in batches of 50 (to avoid rate limits), then for each stock:
1. Gets the last 60 days of closing prices
2. Calculates the 50-day simple moving average (SMA)
3. Checks if the latest close is above the SMA
4. Counts how many pass the test

```python
series.rolling(50).mean().iloc[-1]  # 50-day moving average
```

**`check_s5fi(s5fi)`**
Returns `True` if fewer than 20% of stocks are above their 50-day SMA.

---

### `signals/red_days.py` — Consecutive Down Days

A simple momentum signal: if SPY has been falling for 3+ days in a row, the market is in a short-term downtrend.

**`get_spy_closes(n_days)`**
Fetches the last N closing prices for SPY (the S&P 500 ETF).

**`count_consecutive_red_days(closes)`**
Walks backwards through the list of closes. A "red day" is when today's close is lower than yesterday's.

```python
for i in range(len(closes) - 1, 0, -1):  # walk backwards
    if closes[i] < closes[i - 1]:         # today lower than yesterday
        count += 1
    else:
        break  # stop as soon as we hit a green day
```

**`check_red_days(closes)`**
Returns `True` if 3 or more consecutive red days.

---

### `bot/telegram_alert.py` — Sends the Message

**`format_rule(name, data)`**
Formats one indicator as a single line with an icon, value, and threshold.
- ✅ = triggered
- ❌ = not triggered

**`build_message(report)`**
Assembles the full Telegram message from all the data. Uses Telegram's Markdown formatting:
- `*bold*`
- `_italic_`
- `` `code` ``

**`send_telegram(report)`**
Reads the bot token and chat ID from environment variables (never hardcoded), then sends the message via Telegram's HTTP API.

```python
url = f"https://api.telegram.org/bot{token}/sendMessage"
requests.post(url, json=payload)
```
Telegram's API is simple: just POST to that URL with `chat_id`, `text`, and `parse_mode`.

---

### `.github/workflows/daily_check.yml` — Automation

This is a GitHub Actions workflow file. GitHub reads it and runs it automatically.

```yaml
on:
  schedule:
    - cron: "15 14 * * 1-5"  # 14:15 UTC = 16:15 Israel, Mon–Fri
  workflow_dispatch:           # also allows manual trigger
```

**Cron format:** `minute hour day month weekday`
- `15 14 * * 1-5` = at minute 15, hour 14, any day, any month, Mon–Fri

```yaml
env:
  TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
```
Secrets stored in GitHub are injected as environment variables at runtime — the token is never written in the code or the yml file.

---

## Key Concepts Used

| Concept | Where Used | What It Is |
|---------|-----------|------------|
| HTTP requests | fear_greed, telegram | Fetching data from web APIs |
| User-Agent spoofing | fear_greed, s5fi | Making requests look like a browser |
| yfinance | vix, s5fi, red_days | Python library for Yahoo Finance data |
| DataFrames | s5fi | Pandas table structure for stock data |
| Moving average | s5fi | Average of last N values, recalculated each day |
| Environment variables | telegram, main | Storing secrets outside the code |
| GitHub Actions | daily_check.yml | Running code on a schedule in the cloud |
| Cron syntax | daily_check.yml | Unix scheduling format |

---

## How to Add a New Signal

1. Create `signals/my_signal.py` with:
   - `get_my_signal()` → returns the raw value
   - `check_my_signal(value)` → returns `True`/`False`
2. Import both functions in `signals/engine.py`
3. Call them in `run_engine()` and add to the `rules` dict
4. Update `get_signal_level()` if you change the max score
