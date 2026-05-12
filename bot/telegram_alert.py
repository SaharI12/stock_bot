import os
import requests
from datetime import date


def _icon(triggered: bool) -> str:
    return "✅" if triggered else "❌"


def build_message(report: dict) -> str:
    today = date.today().strftime("%B %d, %Y")
    spy = report.get("spy_price", "N/A")
    vs_150 = report.get("spy_vs_150ma")
    indices = report.get("indices", {})
    signal = report["signal"]
    buy_score = report["buy_score"]
    sell_score = report["sell_score"]
    br = report["buy_rules"]
    sr = report["sell_rules"]

    # 150MA distance string
    if vs_150 is not None:
        sign = "+" if vs_150 >= 0 else ""
        ma_str = f"_{sign}{vs_150}% vs 150MA_"
    else:
        ma_str = ""

    # Index prices
    qqq = f"QQQ `${indices.get('QQQ', 'N/A')}`"
    djia_val = indices.get("DJIA")
    djia = f"DJIA `{djia_val:,}`" if djia_val else "DJIA `N/A`"
    rut = f"RUT `${indices.get('RUT', 'N/A')}`"

    fg = br["fear_greed"]
    vix = br["vix"]
    s5fi = br["s5fi"]
    rsi = br["rsi"]
    red = br["red_days"]
    grn = sr["green_days"]

    lines = [
        f"📊 *Dip Radar — {today}*",
        f"SPY `${spy}` {ma_str}  ·  {qqq}  ·  {djia}  ·  {rut}",
        "",
        f"*{signal}*",
        f"buy {buy_score}/5  ·  sell {sell_score}/5",
        "",
        f"*F&G*  {fg['value']} ({fg.get('rating', '')})  —  B{_icon(fg['triggered'])} S{_icon(sr['fear_greed']['triggered'])}",
        f"*VIX*  {vix['value']}  —  B{_icon(vix['triggered'])} S{_icon(sr['vix']['triggered'])}",
        f"*S5FI*  {s5fi['value']}%  —  B{_icon(s5fi['triggered'])} S{_icon(sr['s5fi']['triggered'])}",
        f"*RSI(14)*  {rsi['value']}  —  B{_icon(rsi['triggered'])} S{_icon(sr['rsi']['triggered'])}",
        f"*Days*  {red['value']}↓ {grn['value']}↑  —  B{_icon(red['triggered'])} S{_icon(grn['triggered'])}",
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
