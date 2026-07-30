import csv
import json
from datetime import datetime

rows = []
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row["email"].strip()
        signup = row["signup"].strip()
        score = row["score"].strip()

        # Rule 1: drop if email empty, no @, or score empty
        if not email or "@" not in email or not score:
            continue

        # Rule 2: normalize email to lowercase
        email = email.lower()

        # Rule 3: normalize date
        if "/" in signup:
            signup = datetime.strptime(signup, "%d/%m/%Y").strftime("%Y-%m-%d")

        rows.append({"email": email, "signup": signup, "score": int(score)})

# Rule 4: deduplicate by email, keep highest score
by_email = {}
for row in rows:
    e = row["email"]
    if e not in by_email or row["score"] > by_email[e]["score"]:
        by_email[e] = row

# Rule 5: sort by email ascending
result = sorted(by_email.values(), key=lambda r: r["email"])

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
