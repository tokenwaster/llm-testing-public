import csv
import json
from datetime import datetime

rows = []

with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get("email", "").strip()
        signup_raw = row.get("signup", "").strip()
        score_raw = row.get("score", "").strip()

        # 1. Drop invalid rows
        if not email or "@" not in email or not score_raw:
            continue

        # Normalize email to lowercase
        email = email.lower()

        # 3. Normalize dates
        signup = ""
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                dt = datetime.strptime(signup_raw, fmt)
                signup = dt.strftime("%Y-%m-%d")
                break
            except ValueError:
                continue

        # If date couldn't be parsed, skip (invalid row)
        if not signup:
            continue

        score = int(score_raw)

        rows.append({"email": email, "signup": signup, "score": score})

# 4. Deduplicate by email — keep highest score
best = {}
for r in rows:
    if r["email"] not in best or r["score"] > best[r["email"]]["score"]:
        best[r["email"]] = r

# 5. Sort by email ascending
result = sorted(best.values(), key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
