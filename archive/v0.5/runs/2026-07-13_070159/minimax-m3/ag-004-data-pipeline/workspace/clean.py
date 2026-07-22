import csv
import json
import re
from datetime import datetime

INPUT = "data.csv"
OUTPUT = "output.json"


def parse_date(s):
    s = s.strip()
    # Try YYYY-MM-DD
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s
    # Try DD/MM/YYYY
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        d, mo, y = m.groups()
        # Validate
        datetime(int(y), int(mo), int(d))
        return f"{y}-{mo}-{d}"
    raise ValueError(f"Unrecognized date: {s!r}")


rows = []
with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        email = r["email"].strip()
        signup_raw = r["signup"].strip()
        score_raw = r["score"].strip()

        # Rule 1: drop invalid rows
        if not email or "@" not in email:
            continue
        if not score_raw:
            continue

        # Rule 2: normalize emails
        email = email.lower()

        # Rule 3: normalize dates
        try:
            signup = parse_date(signup_raw)
        except ValueError:
            continue

        # Parse score
        try:
            score = int(score_raw)
        except ValueError:
            continue

        rows.append({"email": email, "signup": signup, "score": score})

# Rule 4: dedupe by email, keep highest score
by_email = {}
for r in rows:
    e = r["email"]
    if e not in by_email or r["score"] > by_email[e]["score"]:
        by_email[e] = r

deduped = list(by_email.values())

# Rule 5: sort by email ascending
deduped.sort(key=lambda r: r["email"])

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(deduped, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(json.dumps(deduped, indent=2))
