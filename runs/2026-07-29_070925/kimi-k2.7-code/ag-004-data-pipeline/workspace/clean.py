import csv
import json
from collections import defaultdict

records = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row["email"].strip()
        signup = row["signup"].strip()
        score = row["score"].strip()

        # Rule 1: Drop invalid rows
        if not email or "@" not in email or not score:
            continue

        # Rule 2: Normalize email
        email = email.lower()

        # Rule 3: Normalize dates
        if "/" in signup:
            dd, mm, yyyy = signup.split("/")
            signup = f"{yyyy}-{mm}-{dd}"

        records.append({"email": email, "signup": signup, "score": int(score)})

# Rule 4: Deduplicate by email, keep highest score
best = {}
for rec in records:
    email = rec["email"]
    if email not in best or rec["score"] > best[email]["score"]:
        best[email] = rec

# Rule 5: Sort by email ascending
output = sorted(best.values(), key=lambda r: r["email"])

with open("output.json", "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))
