import csv
import json
from datetime import datetime
from pathlib import Path


def normalize_date(value: str) -> str:
    if len(value) == 10 and value[4] == "-":
        datetime.strptime(value, "%Y-%m-%d")
        return value
    return datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")


rows_by_email = {}
with Path("data.csv").open(newline="", encoding="utf-8") as source:
    for row in csv.DictReader(source):
        email = row["email"].strip()
        score_text = row["score"].strip()
        if "@" not in email or not score_text:
            continue
        email = email.lower()
        record = {
            "email": email,
            "signup": normalize_date(row["signup"].strip()),
            "score": int(score_text),
        }
        if email not in rows_by_email or record["score"] > rows_by_email[email]["score"]:
            rows_by_email[email] = record

output = sorted(rows_by_email.values(), key=lambda record: record["email"])
Path("output.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
