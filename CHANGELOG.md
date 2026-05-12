# Changelog

## [2026-05-12] — Major feature update

### Added
- **Sell signals**: symmetric sell-side scoring mirrors the buy side. Each indicator now has both a buy trigger and a sell trigger. The final signal is determined by whichever side scores higher (or MIXED if tied above zero).
- **RSI(14) on SPY** as a 5th indicator: buy when RSI < 30 (oversold), sell when RSI > 70 (overbought).
- **Index prices in message header**: QQQ, DJIA, and Russell 2000 (RUT) shown alongside SPY.
- **150-day MA distance** for all 4 indices (SPY, QQQ, DJIA, RUT) — shows how far each index is above or below its 150-day moving average.
- **Previous day values** for every indicator (Fear and Greed, VIX, S5FI, RSI, Red/Green Days) and every index, so you can see the trend at a glance.
- **README.md** added to the repo.

### Changed
- Score scale changed from 4 to **5 indicators per side**.
- **S5FI** now downloads all ~500 S&P 500 tickers in a **single batch** instead of 10 batches of 50 — significantly faster.
- Message format: restored original layout (section headers, trigger thresholds on each line), now with `prev:` value shown per indicator.
- Full name **"Fear and Greed"** used in the message instead of abbreviation "F&G".
- SPY fetches 200 days of history (was 10) to support 150MA and stable RSI calculation.

### New files
- `signals/rsi.py` — RSI calculation with Wilder's smoothing, buy/sell checks
- `signals/indices.py` — fetches QQQ, DJIA, RUT prices + daily change + 150MA distance

### Signal levels (buy and sell, out of 5)
| Score | Buy | Sell |
|-------|-----|------|
| 5/5 | 🚨 EXTREME BUY | 🚨 EXTREME SELL |
| 4/5 | 🟢 STRONG BUY | 🔴 STRONG SELL |
| 3/5 | 🟢 BUY | 🔴 SELL |
| 2/5 | 🟡 WATCH | 🟡 WATCH |
| 1/5 | ⚪ MILD BUY | ⚪ MILD SELL |
| 0/5 | 🔵 HOLD | 🔵 HOLD |

---

## [2026-05-07] — Initial release

### Added
- 4 buy indicators: Fear and Greed < 10, VIX >= 30, S5FI < 20%, 3+ consecutive red days on SPY.
- Telegram alert via `@Sahar_I_bot` sent every weekday at 14:15 UTC (16:15 Israel time).
- GitHub Actions workflow (`daily_check.yml`) for fully automated daily runs.
- Experiment tracker CLI (`tracker/tracker.py`) for logging runs and scores.
- Known fixes: CNN 418 bypass (User-Agent + Referer headers), Wikipedia 403 bypass, Windows emoji encoding fix.
