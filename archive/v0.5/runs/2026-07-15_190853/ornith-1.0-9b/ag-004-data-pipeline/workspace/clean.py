import csv
import json
from datetime import datetime

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row["email"].strip()
        signup_raw = row["signup"].strip()
        score_raw = row["score"].strip()

        # 1. Drop invalid rows
        if not email or "@" not in email or not score_raw:
            continue

        # Normalize email to lowercase (rule 2)
        email = email.lower()

        # 3. Normalize dates
        signup_raw = signup_raw.strip()
        if "/" in signup_raw:
            # DD/MM/YYYY
            parts = signup_raw.split("/")
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            signup = f"{year}-{month:02d}-{day:02d}"
        else:
            # YYYY-MM-DD - keep as is (already validated format)
            signup = signup_raw

        score = int(score_raw)
        rows.append({"email": email, "signup": signup, "score": score})

# 4. Deduplicate by email, keep highest score
best = {}
for r in rows:
    if r["email"] not in best or r["score"] > best[r["email"]]["score"]:
        best[r["email"]] = r

# 5. Sort by email ascending
result = sorted(best.values(), key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
