from signals.fear_greed import get_fear_greed, check_fear_greed, check_sell_fear_greed
from signals.vix import get_vix, check_vix, check_sell_vix
from signals.s5fi import get_s5fi, check_s5fi, check_sell_s5fi
from signals.red_days import get_spy_closes, count_consecutive_red_days, check_red_days, count_consecutive_green_days, check_green_days


def get_buy_signal_level(score: int) -> str:
    if score == 4:
        return "🚨 EXTREME BUY — All 4 indicators firing!"
    elif score == 3:
        return "🟢 STRONG BUY — 3/4 indicators triggered"
    elif score == 2:
        return "🟡 WATCH — 2/4 buy indicators triggered"
    elif score == 1:
        return "⚪ MILD BUY — 1/4 indicators triggered"
    else:
        return "🔵 HOLD — No signals firing"


def get_sell_signal_level(score: int) -> str:
    if score == 4:
        return "🚨 EXTREME SELL — All 4 sell indicators firing!"
    elif score == 3:
        return "🔴 STRONG SELL — 3/4 sell indicators triggered"
    elif score == 2:
        return "🟡 WATCH — 2/4 sell indicators triggered"
    elif score == 1:
        return "⚪ MILD SELL — 1/4 sell indicators triggered"
    else:
        return "🔵 HOLD — No sell signals firing"


def run_engine() -> dict:
    print("Fetching Fear & Greed...")
    fg = get_fear_greed()

    print("Fetching VIX...")
    vix = get_vix()

    print("Fetching S5FI (this takes ~2 min)...")
    s5fi = get_s5fi()

    print("Fetching SPY closes...")
    closes = get_spy_closes()
    red_count = count_consecutive_red_days(closes)
    green_count = count_consecutive_green_days(closes)

    # Buy rules
    b1 = check_fear_greed(fg["score"])
    b2 = check_vix(vix)
    b3 = check_s5fi(s5fi)
    b4 = check_red_days(closes)
    buy_score = sum([b1, b2, b3, b4])

    # Sell rules
    s1 = check_sell_fear_greed(fg["score"])
    s2 = check_sell_vix(vix)
    s3 = check_sell_s5fi(s5fi)
    s4 = check_green_days(closes)
    sell_score = sum([s1, s2, s3, s4])

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
        "buy_rules": {
            "fear_greed": {
                "value": fg["score"],
                "rating": fg["rating"],
                "triggered": b1,
                "threshold": "< 10 (Extreme Fear)",
            },
            "vix": {
                "value": vix,
                "triggered": b2,
                "threshold": ">= 30",
            },
            "s5fi": {
                "value": s5fi,
                "triggered": b3,
                "threshold": "< 20%",
            },
            "red_days": {
                "value": red_count,
                "triggered": b4,
                "threshold": ">= 3 consecutive red days",
            },
        },
        "sell_rules": {
            "fear_greed": {
                "value": fg["score"],
                "rating": fg["rating"],
                "triggered": s1,
                "threshold": "> 80 (Extreme Greed)",
            },
            "vix": {
                "value": vix,
                "triggered": s2,
                "threshold": "< 15 (Complacency)",
            },
            "s5fi": {
                "value": s5fi,
                "triggered": s3,
                "threshold": "> 80%",
            },
            "green_days": {
                "value": green_count,
                "triggered": s4,
                "threshold": ">= 3 consecutive green days",
            },
        },
    }
