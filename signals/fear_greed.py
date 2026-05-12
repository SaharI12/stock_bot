import requests


def get_fear_greed() -> dict:
    """Fetch CNN Fear & Greed index. Returns score and rating."""
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://edition.cnn.com/",
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        score = data["fear_and_greed"]["score"]
        rating = data["fear_and_greed"]["rating"]

        prev_score = None
        try:
            historical = data["fear_and_greed_historical"]["data"]
            if len(historical) >= 2:
                prev_score = round(historical[-2]["y"], 1)
        except Exception:
            pass

        return {"score": round(score, 1), "rating": rating, "prev_score": prev_score}
    except Exception as e:
        print(f"[fear_greed] Error: {e}")
        return {"score": None, "rating": None, "prev_score": None}


def check_fear_greed(score: float) -> bool:
    if score is None:
        return False
    return score < 10


def check_sell_fear_greed(score: float) -> bool:
    if score is None:
        return False
    return score > 80
