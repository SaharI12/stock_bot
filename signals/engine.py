from signals.fear_greed import get_fear_greed, check_fear_greed
from signals.vix import get_vix, check_vix
from signals.s5fi import get_s5fi, check_s5fi
from signals.red_days import get_spy_closes, count_consecutive_red_days, check_red_days


def get_signal_level(score: int) -> str:
    if score == 4:
        return "🚨 EXTREME BUY — All 4 indicators firing!"
    elif score == 3:
        return "🟢 STRONG BUY — 3/4 indicators triggered"
    elif score == 2:
        return "🟡 WATCH — 2/4 indicators triggered"
    elif score == 1:
        return "⚪ MILD — 1/4 indicators triggered"
    else:
        return "🔵 HOLD — No signals firing"


def run_engine() -> dict:
    """Fetch all data, evaluate all rules, return full report."""
    print("Fetching Fear & Greed...")
    fg = get_fear_greed()

    print("Fetching VIX...")
    vix = get_vix()

    print("Fetching S5FI (this takes ~2 min)...")
    s5fi = get_s5fi()

    print("Fetching SPY closes...")
    closes = get_spy_closes()
    red_count = count_consecutive_red_days(closes)

    # Evaluate rules
    r1 = check_fear_greed(fg["score"])
    r2 = check_vix(vix)
    r3 = check_s5fi(s5fi)
    r4 = check_red_days(closes)

    score = sum([r1, r2, r3, r4])
    signal = get_signal_level(score)

    spy_price = round(closes[-1], 2) if closes else None

    return {
        "signal": signal,
        "score": score,
        "spy_price": spy_price,
        "rules": {
            "fear_greed": {
                "value": fg["score"],
                "rating": fg["rating"],
                "triggered": r1,
                "threshold": "< 10 (Extreme Fear)",
            },
            "vix": {
                "value": vix,
                "triggered": r2,
                "threshold": ">= 30",
            },
            "s5fi": {
                "value": s5fi,
                "triggered": r3,
                "threshold": "< 20%",
            },
            "red_days": {
                "value": red_count,
                "triggered": r4,
                "threshold": ">= 3 consecutive red days",
            },
        },
    }
