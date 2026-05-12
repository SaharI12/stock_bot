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
│   ├── fear_greed.py
│   ├── vix.py
│   ├── s5fi.py
│   ├── red_days.py
│   └── engine.py
├── bot/
│   ├── __init__.py
│   └── telegram_alert.py
├── main.py
├── requirements.txt
├── .env               ← local only, never committed
└── .gitignore
```

---

## What It Does

Runs 4 market signal checks on both the buy side and sell side, then sends a Telegram alert.
The final signal is determined by whichever side scores higher (or MIXED if tied and > 0).

| Signal | Buy triggers at | Sell triggers at |
|--------|-----------------|------------------|
| Fear & Greed | score < 10 (Extreme Fear) | score > 80 (Extreme Greed) |
| VIX | >= 30 | < 15 (Complacency) |
| S5FI | < 20% above 50-day SMA | > 80% above 50-day SMA |
| Red/Green Days | 3+ consecutive red days | 3+ consecutive green days |

Buy: 4/4 = EXTREME BUY, 3/4 = STRONG BUY, 2/4 = WATCH, 1/4 = MILD BUY, 0/4 = HOLD.
Sell: 4/4 = EXTREME SELL, 3/4 = STRONG SELL, 2/4 = WATCH, 1/4 = MILD SELL, 0/4 = HOLD.

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
