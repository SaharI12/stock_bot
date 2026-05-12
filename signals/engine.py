from signals.fear_greed import get_fear_greed, check_fear_greed, check_sell_fear_greed
from signals.vix import get_vix, check_vix, check_sell_vix
from signals.s5fi import get_s5fi, check_s5fi, check_sell_s5fi
from signals.red_days import get_spy_closes, count_consecutive_red_days, check_red_days, count_consecutive_green_days, check_green_days
from signals.rsi import calculate_rsi, check_buy_rsi, check_sell_rsi
from signals.indices import get_index_prices


def get_buy_signal_level(score: int) -> str:
    if score == 5:   return "🚨 EXTREME BUY — All 5 indicators firing!"
    elif score == 4: return "🟢 STRONG BUY — 4/5 indicators triggered"
    elif score == 3: return "🟢 BUY — 3/5 indicators triggered"
    elif score == 2: return "🟡 WATCH — 2/5 buy indicators triggered"
    elif score == 1: return "⚪ MILD BUY — 1/5 indicators triggered"
    else:            return "🔵 HOLD — No signals firing"


def get_sell_signal_level(score: int) -> str:
    if score == 5:   return "🚨 EXTREME SELL — All 5 sell indicators firing!"
    elif score == 4: return "🔴 STRONG SELL — 4/5 sell indicators triggered"
    elif score == 3: return "🔴 SELL — 3/5 sell indicators triggered"
    elif score == 2: return "🟡 WATCH — 2/5 sell indicators triggered"
    elif score == 1: return "⚪ MILD SELL — 1/5 sell indicators triggered"
    else:            return "🔵 HOLD — No signals firing"


def run_engine() -> dict:
    print("Fetching Fear & Greed...")
    fg = get_fear_greed()

    print("Fetching VIX...")
    vix = get_vix()

    print("Fetching S5FI...")
    s5fi = get_s5fi()

    print("Fetching SPY closes...")
    closes = get_spy_closes(200)
    red_count = count_consecutive_red_days(closes)
    green_count = count_consecutive_green_days(closes)
    rsi = calculate_rsi(closes)

    print("Fetching index prices...")
    indices = get_index_prices()

    # 150-day MA distance
    sma150 = sum(closes[-150:]) / 150 if len(closes) >= 150 else None
    spy_vs_150ma = round((closes[-1] - sma150) / sma150 * 100, 1) if sma150 and closes else None

    # Buy rules
    b1 = check_fear_greed(fg["score"])
    b2 = check_vix(vix)
    b3 = check_s5fi(s5fi)
    b4 = check_red_days(closes)
    b5 = check_buy_rsi(rsi)
    buy_score = sum([b1, b2, b3, b4, b5])

    # Sell rules
    s1 = check_sell_fear_greed(fg["score"])
    s2 = check_sell_vix(vix)
    s3 = check_sell_s5fi(s5fi)
    s4 = check_green_days(closes)
    s5 = check_sell_rsi(rsi)
    sell_score = sum([s1, s2, s3, s4, s5])

    if sell_score > buy_score:
        signal = get_sell_signal_level(sell_score)
    elif buy_score > sell_score:
        signal = get_buy_signal_level(buy_score)
    elif buy_score > 0:
        signal = "⚠️ MIXED — Buy and sell signals equally triggered"
    else:
        signal = "🔵 HOLD — No signals firing"

    spy_price = round(closes[-1], 2) if closes else None

    return {
        "signal": signal,
        "buy_score": buy_score,
        "sell_score": sell_score,
        "spy_price": spy_price,
        "spy_vs_150ma": spy_vs_150ma,
        "indices": indices,
        "buy_rules": {
            "fear_greed": {"value": fg["score"], "rating": fg["rating"], "triggered": b1},
            "vix":        {"value": vix,          "triggered": b2},
            "s5fi":       {"value": s5fi,          "triggered": b3},
            "rsi":        {"value": rsi,           "triggered": b5},
            "red_days":   {"value": red_count,     "triggered": b4},
        },
        "sell_rules": {
            "fear_greed": {"value": fg["score"], "rating": fg["rating"], "triggered": s1},
            "vix":        {"value": vix,          "triggered": s2},
            "s5fi":       {"value": s5fi,          "triggered": s3},
            "rsi":        {"value": rsi,           "triggered": s5},
            "green_days": {"value": green_count,   "triggered": s4},
        },
    }
