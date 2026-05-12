import os
import requests
from datetime import date


def format_rule(name: str, data: dict) -> str:
    icon = "✅" if data["triggered"] else "❌"
    value = data.get("value")
    if value is None:
        value_str = "N/A"
    elif name == "fear_greed":
        value_str = f"{value} ({data.get('rating', '')})"
    elif name == "s5fi":
        value_str = f"{value}%"
    elif name in ("red_days", "green_days"):
        value_str = f"{value} days"
    else:
        value_str = str(value)

    threshold = data.get("threshold", "")
    label = {
        "fear_greed": "Fear & Greed",
        "vix": "VIX",
        "s5fi": "S5FI",
        "red_days": "Red Days",
        "green_days": "Green Days",
    }.get(name, name)

    return f"{icon} *{label}*: {value_str}  _(trigger: {threshold})_"


def build_message(report: dict) -> str:
    today = date.today().strftime("%B %d, %Y")
    spy = report.get("spy_price", "N/A")
    signal = report["signal"]
    buy_score = report["buy_score"]
    sell_score = report["sell_score"]

    lines = [
        f"📊 *Dip Radar — {today}*",
        f"SPY: `${spy}`",
        "",
        f"*Signal: {signal}*",
        "",
        f"— Buy Indicators ({buy_score}/4) —",
    ]

    for name, data in report["buy_rules"].items():
        lines.append(format_rule(name, data))

    lines += [
        "",
        f"— Sell Indicators ({sell_score}/4) —",
    ]

    for name, data in report["sell_rules"].items():
        lines.append(format_rule(name, data))

    lines += [
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

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("[telegram] Message sent successfully")
        return True
    except Exception as e:
        print(f"[telegram] Failed to send: {e}")
        return False
