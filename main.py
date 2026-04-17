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
    print(f"Score:  {report['score']}/4\n")

    for name, data in report["rules"].items():
        status = "TRIGGERED" if data["triggered"] else "not triggered"
        print(f"  {name}: {data['value']} → {status}")

    print("\nSending Telegram alert...")
    send_telegram(report)


if __name__ == "__main__":
    main()
