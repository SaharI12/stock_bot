import os
import requests
from datetime import date


def _pct(value: float | None, suffix: str = "%") -> str:
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value}{suffix}"


def format_index_line(name: str, price, pct_change, vs_150ma, is_djia: bool = False) -> str:
    if price is None:
        return f"{name}: N/A"
    price_str = f"{price:,}" if is_djia else f"${price}"
    return (
        f"{name}: {price_str}  (prev change: {_pct(pct_change)})  "
        f"vs 150MA: {_pct(vs_150ma)}"
    )


def format_rule(label: str, data: dict, show_rating: bool = False, unit: str = "") -> str:
    icon = "✅" if data["triggered"] else "❌"
    value = data.get("value")
    prev = data.get("prev")
    threshold = data.get("threshold", "")

    if value is None:
        value_str = "N/A"
    elif show_rating:
        value_str = f"{value} ({data.get('rating', '')})"
    else:
        value_str = f"{value}{unit}"

    prev_str = ""
    if prev is not None:
        prev_display = f"{prev}{unit}" if unit else str(prev)
        prev_str = f", prev: {prev_display}"

    return f"{icon} {label}: {value_str}{prev_str}  (trigger: {threshold})"


def build_message(report: dict) -> str:
    today = date.today().strftime("%B %d, %Y")
    spy = report.get("spy_price", "N/A")
    spy_pct = report.get("spy_pct_change")
    spy_ma = report.get("spy_vs_150ma")
    indices = report.get("indices", {})
    signal = report["signal"]
    buy_score = report["buy_score"]
    sell_score = report["sell_score"]
    br = report["buy_rules"]
    sr = report["sell_rules"]

    qqq  = indices.get("QQQ",  {})
    djia = indices.get("DJIA", {})
    rut  = indices.get("RUT",  {})

    lines = [
        f"📊 *Dip Radar — {today}*",
        "",
        format_index_line("SPY",  spy,  spy_pct,  spy_ma),
        format_index_line("QQQ",  qqq.get("price"),  qqq.get("pct_change"),  qqq.get("vs_150ma")),
        format_index_line("DJIA", djia.get("price"), djia.get("pct_change"), djia.get("vs_150ma"), is_djia=True),
        format_index_line("RUT",  rut.get("price"),  rut.get("pct_change"),  rut.get("vs_150ma")),
        "",
        f"Signal: {signal}",
        f"Buy triggered: {buy_score}/5  |  Sell triggered: {sell_score}/5",
        "",
        "— Buy Indicators —",
        format_rule("Fear and Greed", br["fear_greed"], show_rating=True),
        format_rule("VIX",            br["vix"]),
        format_rule("S5FI",           br["s5fi"], unit="%"),
        format_rule("RSI(14)",        br["rsi"]),
        format_rule("Red Days",       br["red_days"], unit=" days"),
        "",
        "— Sell Indicators —",
        format_rule("Fear and Greed", sr["fear_greed"], show_rating=True),
        format_rule("VIX",            sr["vix"]),
        format_rule("S5FI",           sr["s5fi"], unit="%"),
        format_rule("RSI(14)",        sr["rsi"]),
        format_rule("Green Days",     sr["green_days"], unit=" days"),
        "",
        "⚠️ _Not financial advice. Based on historical statistics._",
    ]

    return "\n".join(lines)


def send_telegram(report: dict) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("[telegram] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID env vars")
        return False

    message = build_message(report)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("[telegram] Message sent successfully")
        return True
    except Exception as e:
        print(f"[telegram] Failed to send: {e}")
        return False
