import os
import requests
from datetime import date


def _icon(triggered: bool) -> str:
    return "✅" if triggered else "❌"


def _pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value}%"


def _index_line(name: str, data: dict, is_djia: bool = False) -> str:
    price = data.get("price")
    pct = data.get("pct_change")
    vs_ma = data.get("vs_150ma")

    if price is None:
        return f"*{name}*  N/A"

    price_str = f"`{price:,}`" if is_djia else f"`${price}`"
    pct_str = _pct(pct)
    ma_str = f"vs 150MA: {_pct(vs_ma)}"

    return f"*{name}*   {price_str}   {pct_str}   {ma_str}"


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

    fg = br["fear_greed"]
    vix = br["vix"]
    s5fi = br["s5fi"]
    rsi = br["rsi"]
    red = br["red_days"]
    grn = sr["green_days"]

    lines = [
        f"📊 *Dip Radar — {today}*",
        "",
        f"*SPY*   `${spy}`   {_pct(spy_pct)}   vs 150MA: {_pct(spy_ma)}",
        _index_line("QQQ",  indices.get("QQQ",  {})),
        _index_line("DJIA", indices.get("DJIA", {}), is_djia=True),
        _index_line("RUT",  indices.get("RUT",  {})),
        "",
        f"*{signal}* _({buy_score}/5 buy · {sell_score}/5 sell)_",
        "",
        f"*F&G*   {fg['value']} _({fg.get('rating', '')})_   B{_icon(fg['triggered'])} <10   S{_icon(sr['fear_greed']['triggered'])} >80",
        f"*VIX*   {vix['value']}   B{_icon(vix['triggered'])} ≥30   S{_icon(sr['vix']['triggered'])} <15",
        f"*S5FI*  {s5fi['value']}%   B{_icon(s5fi['triggered'])} <20%   S{_icon(sr['s5fi']['triggered'])} >80%",
        f"*RSI*   {rsi['value']}   B{_icon(rsi['triggered'])} <30   S{_icon(sr['rsi']['triggered'])} >70",
        f"*Days*  {red['value']}↓ · {grn['value']}↑   B{_icon(red['triggered'])} 3+↓   S{_icon(grn['triggered'])} 3+↑",
        "",
        "_⚠️ Not financial advice._",
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
