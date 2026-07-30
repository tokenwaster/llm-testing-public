import csv
import json
from pathlib import Path

HERE = Path(__file__).parent


def normalize_date(value):
    value = value.strip()
    if "/" in value:
        day, month, year = value.split("/")
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return value


def main():
    best = {}
    with open(HERE / "data.csv", newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            email = (row.get("email") or "").strip()
            score = (row.get("score") or "").strip()
            if not email or "@" not in email or not score:
                continue
            email = email.lower()
            record = {
                "email": email,
                "signup": normalize_date(row.get("signup") or ""),
                "score": int(score),
            }
            if email not in best or record["score"] > best[email]["score"]:
                best[email] = record

    records = sorted(best.values(), key=lambda r: r["email"])
    (HERE / "output.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
