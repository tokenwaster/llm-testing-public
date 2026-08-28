import csv
import json
from datetime import datetime

INPUT = "data.csv"
OUTPUT = "output.json"

records = []

with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get("email") or "").strip()
        signup = (row.get("signup") or "").strip()
        score = (row.get("score") or "").strip()

        # Rule 1: drop invalid rows
        if "@" not in email or email == "" or score == "":
            continue

        # Rule 2: normalize emails to lowercase
        email = email.lower()

        # Rule 3: normalize dates
        try:
            dt = datetime.strptime(signup, "%Y-%m-%d")
        except ValueError:
            dt = datetime.strptime(signup, "%d/%m/%Y")
        signup = dt.strftime("%Y-%m-%d")

        records.append({"email": email, "signup": signup, "score": int(score)})

# Rule 4: deduplicate by email, keep highest score
best = {}
for rec in records:
    e = rec["email"]
    if e not in best or rec["score"] > best[e]["score"]:
        best[e] = rec

# Rule 5: sort by email ascending
result = sorted(best.values(), key=lambda r: r["email"])

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
