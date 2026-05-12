# Dip Radar 📊

A Telegram bot that checks 4 market indicators every weekday and tells you whether to **buy the dip**, **sell into strength**, or **hold**.

Runs automatically on GitHub Actions — no server or PC needed.

---

## How It Works

The bot scores the market on both a **buy side** and a **sell side** (0–4 each).
Whichever side scores higher determines the final signal.

| Indicator | Buy triggers when | Sell triggers when |
|-----------|-------------------|--------------------|
| **Fear & Greed** (CNN) | score < 10 — Extreme Fear | score > 80 — Extreme Greed |
| **VIX** (CBOE) | ≥ 30 — high volatility | < 15 — complacency |
| **S5FI** (S&P 500 breadth) | < 20% stocks above 50-day SMA | > 80% stocks above 50-day SMA |
| **SPY momentum** | 3+ consecutive red days | 3+ consecutive green days |

**Signal levels:**

| Score | Buy signal | Sell signal |
|-------|-----------|-------------|
| 4/4 | 🚨 EXTREME BUY | 🚨 EXTREME SELL |
| 3/4 | 🟢 STRONG BUY | 🔴 STRONG SELL |
| 2/4 | 🟡 WATCH | 🟡 WATCH |
| 1/4 | ⚪ MILD BUY | ⚪ MILD SELL |
| 0/4 | 🔵 HOLD | 🔵 HOLD |

If buy and sell scores tie above zero: `⚠️ MIXED`.

---

## Example Telegram Message

```
📊 Dip Radar — May 12, 2026
SPY: $527.40

Signal: 🔴 STRONG SELL — 3/4 sell indicators triggered

— Buy Indicators (0/4) —
❌ Fear & Greed: 82.3 (Extreme Greed)  (trigger: < 10)
❌ VIX: 13.1  (trigger: >= 30)
❌ S5FI: 84.2%  (trigger: < 20%)
❌ Red Days: 0 days  (trigger: >= 3 consecutive)

— Sell Indicators (3/4) —
✅ Fear & Greed: 82.3 (Extreme Greed)  (trigger: > 80)
✅ VIX: 13.1  (trigger: < 15)
✅ S5FI: 84.2%  (trigger: > 80%)
❌ Green Days: 1 day  (trigger: >= 3 consecutive)

⚠️ Not financial advice. Based on historical statistics.
```

---

## Project Structure

```
stock_bot/
├── .github/workflows/daily_check.yml   ← GitHub Actions schedule
├── signals/
│   ├── engine.py       ← coordinates all signals, builds report
│   ├── fear_greed.py   ← CNN Fear & Greed API
│   ├── vix.py          ← CBOE VIX via yfinance
│   ├── s5fi.py         ← S&P 500 breadth calculation
│   └── red_days.py     ← SPY consecutive red/green days
├── bot/
│   └── telegram_alert.py  ← formats and sends Telegram message
├── main.py
└── requirements.txt
```

---

## Running Locally

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

Run:
```bash
python main.py
```

---

## Automation

The bot runs every weekday at **14:15 UTC (16:15 Israel time)** — 15 minutes before the US market opens.

You can also trigger it manually: GitHub repo → **Actions** → **Daily Dip Radar** → **Run workflow**.

GitHub secrets required: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

---

> ⚠️ Not financial advice. Based on historical statistics only.
