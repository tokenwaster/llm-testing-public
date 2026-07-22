import csv
import json
from datetime import datetime

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row["email"].strip() if row.get("email") else ""
        signup_raw = (row.get("signup") or "").strip()
        score_raw = (row.get("score") or "").strip()

        # 1. Drop invalid rows
        if not email or "@" not in email:
            continue
        if not score_raw:
            continue

        # 2. Normalize email to lowercase
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

        if not signup:
            continue  # invalid date, drop row

        score = int(score_raw)

        rows.append({"email": email, "signup": signup, "score": score})

# 4. Deduplicate by email (keep highest score)
best = {}
for r in rows:
    if r["email"] not in best or r["score"] > best[r["email"]]["score"]:
        best[r["email"]] = r

# 5. Sort by email ascending
result = sorted(best.values(), key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
