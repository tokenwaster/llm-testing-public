#!/usr/bin/env python3
"""Clean data.csv -> output.json according to the specified rules."""

import csv
import json
import os
from datetime import datetime

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.csv")
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output.json")


def parse_date(raw):
    """Return YYYY-MM-DD from either YYYY-MM-DD or DD/MM/YYYY input."""
    s = (raw or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def main():
    with open(SRC, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    best = {}  # normalized email -> record

    for row in rows:
        email = (row.get("email") or "").strip()
        score_raw = (row.get("score") or "").strip()

        # Rule 1: drop invalid rows
        if not email or "@" not in email or not score_raw:
            continue

        # Rule 2: normalize email
        email = email.lower()

        # Rule 3: normalize date
        signup = parse_date(row.get("signup"))
        if signup is None:
            continue

        try:
            score = int(score_raw)
        except ValueError:
            continue

        # Rule 4: dedupe by email, keep highest score
        prev = best.get(email)
        if prev is None or score > prev["score"]:
            best[email] = {"email": email, "signup": signup, "score": score}

    # Rule 5: sort by email ascending
    records = [best[k] for k in sorted(best)]

    with open(DST, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2)
        fh.write("\n")

    print(f"wrote {len(records)} records to {DST}")


if __name__ == "__main__":
    main()
