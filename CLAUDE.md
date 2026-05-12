# Dip Radar — Claude Code Setup Instructions

## Project Location
`C:\Users\97254\PycharmProjects\stock_bot`

## Status
✅ Fully built, tested, and deployed to GitHub Actions.

---

## Folder Structure

```
stock_bot/
├── .github/
│   └── workflows/
│       └── daily_check.yml
├── signals/
│   ├── __init__.py
│   ├── engine.py       ← coordinates all signals, builds report
│   ├── fear_greed.py   ← CNN Fear & Greed API (current + prev)
│   ├── vix.py          ← CBOE VIX via yfinance (current + prev)
│   ├── s5fi.py         ← S&P 500 breadth (current + prev, single batch)
│   ├── red_days.py     ← SPY consecutive red/green days
│   ├── rsi.py          ← RSI(14) on SPY with Wilder's smoothing
│   └── indices.py      ← QQQ, DJIA, RUT prices + daily change + 150MA
├── bot/
│   ├── __init__.py
│   └── telegram_alert.py
├── main.py
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── .env               ← local only, never committed
└── .gitignore
```

---

## What It Does

Scores the market on **5 buy indicators** and **5 sell indicators**. The side with the higher score wins (or MIXED if tied above zero). Sends a Telegram alert every weekday before market open.

| Indicator | Buy triggers at | Sell triggers at |
|-----------|-----------------|------------------|
| Fear and Greed (CNN) | score < 10 (Extreme Fear) | score > 80 (Extreme Greed) |
| VIX (CBOE) | >= 30 | < 15 (Complacency) |
| S5FI (S&P 500 breadth) | < 20% above 50-day SMA | > 80% above 50-day SMA |
| RSI(14) on SPY | < 30 (Oversold) | > 70 (Overbought) |
| Red/Green Days (SPY) | 3+ consecutive red days | 3+ consecutive green days |

**Signal levels (same scale for buy and sell, out of 5):**
5 = EXTREME, 4 = STRONG, 3 = moderate, 2 = WATCH, 1 = MILD, 0 = HOLD.

**Message includes:**
- SPY, QQQ, DJIA, RUT — current price, daily % change, and % vs 150-day MA
- Each indicator — current value, previous day value, and trigger threshold
- Separate Buy and Sell sections

---

## Telegram Bot
- Bot: `@Sahar_I_bot`
- Chat ID: `353419668`
- Credentials stored in `.env` locally and as GitHub Actions secrets

---

## GitHub
- Repo: https://github.com/SaharI12/stock_bot
- Runs automatically: **every weekday at 14:15 UTC (16:15 Israel time, 15 min before US market open)**
- Can also be triggered manually via Actions tab → "Daily Dip Radar" → "Run workflow"
- GitHub secrets set: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

---

## Local Development

### Run locally
```bash
pip install -r requirements.txt
python main.py
```

### .env file format
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=353419668
```

---

## Dependencies
```
python-dotenv==1.0.1
yfinance==0.2.51
pandas==2.2.3
requests==2.32.3
lxml==5.3.0
html5lib==1.1
beautifulsoup4==4.12.3
```

---

## Known Fixes Applied
- **Fear & Greed**: Added full browser User-Agent + Referer headers to bypass CNN 418 bot detection
- **S5FI Wikipedia**: Added `User-Agent` via `storage_options` to bypass 403 on `pd.read_html`
- **Windows emoji encoding**: Added `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")` in `main.py`
- **yfinance**: Upgraded to latest version to fix delisted ticker errors
