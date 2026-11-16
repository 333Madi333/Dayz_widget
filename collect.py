#!/usr/bin/env python3
"""Polls the DZSA Launcher API once and appends the player count to data/history.json.

Run on a schedule (the GitHub Actions workflow runs it every 10 minutes).
Only the Python standard library is used.
"""
import json
import os
import sys
import time
import urllib.request

SERVER_IP = os.environ.get("SERVER_IP", "109.248.4.73")
QUERY_PORT = os.environ.get("QUERY_PORT", "2309")  # DZSA query port, not the 2308 game port
KEEP_DAYS = int(os.environ.get("KEEP_DAYS", "45"))
HISTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "history.json")

URL = f"https://dayzsalauncher.com/api/v1/query/{SERVER_IP}/{QUERY_PORT}"


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "dayz-player-widget/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("status") != 0 or "result" not in body:
        raise RuntimeError(f"DZSA error: {body.get('error', body)}")
    return body["result"]


def main():
    try:
        with open(HISTORY, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"points": []}
    now = int(time.time())
    res = None
    for attempt in range(3):
        try:
            res = fetch()
            break
        except Exception as e:  # noqa: BLE001
            print(f"attempt {attempt + 1} failed: {e}", file=sys.stderr)
            time.sleep(10)
    if res is None:
        print("server unreachable; nothing recorded", file=sys.stderr)
        return 0
    data["server"] = {
        "name": res.get("name"),
        "map": res.get("map"),
        "ip": SERVER_IP,
        "gamePort": res.get("gamePort"),
        "queryPort": int(QUERY_PORT),
        "maxPlayers": res.get("maxPlayers"),
    }
    # The first real reading replaces any example dataset.
    if data.pop("isExample", False):
        data["points"] = []
    data["points"].append([now, int(res.get("players", 0))])

    cutoff = now - KEEP_DAYS * 86400
    data["points"] = [p for p in data["points"] if p[0] >= cutoff]
    data["updated"] = now
    os.makedirs(os.path.dirname(HISTORY), exist_ok=True)
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"recorded {data['points'][-1]} ({len(data['points'])} points)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
