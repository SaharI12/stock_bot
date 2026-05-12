import sys
import os
import io
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from signals.engine import run_engine
from bot.telegram_alert import send_telegram


def main():
    print("=" * 40)
    print("DIP RADAR — Running signal check")
    print("=" * 40)

    report = run_engine()

    print(f"\nSignal: {report['signal']}")
    print(f"Buy score:  {report['buy_score']}/5")
    print(f"Sell score: {report['sell_score']}/5")
    print(f"SPY vs 150MA: {report.get('spy_vs_150ma')}%")
    print(f"Indices: {report.get('indices')}\n")

    print(f"{'Indicator':<12} {'Value':<20} {'Buy':<10} Sell")
    for name in report["buy_rules"]:
        bdata = report["buy_rules"][name]
        sell_name = name if name != "red_days" else "green_days"
        sdata = report["sell_rules"].get(sell_name, {})
        b = "TRIGGERED" if bdata["triggered"] else "-"
        s = "TRIGGERED" if sdata.get("triggered") else "-"
        print(f"  {name:<12} {str(bdata['value']):<20} {b:<10} {s}")

    print("\nSending Telegram alert...")
    send_telegram(report)


if __name__ == "__main__":
    main()
