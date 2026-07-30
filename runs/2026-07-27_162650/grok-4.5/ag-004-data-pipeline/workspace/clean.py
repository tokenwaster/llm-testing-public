import csv
import json
from datetime import datetime

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get("email") or "").strip()
        signup = (row.get("signup") or "").strip()
        score = (row.get("score") or "").strip()

        # 1. Drop invalid rows
        if not email or "@" not in email or not score:
            continue

        # 2. Normalize emails
        email = email.lower()

        # 3. Normalize dates
        if "/" in signup:
            dt = datetime.strptime(signup, "%d/%m/%Y")
            signup = dt.strftime("%Y-%m-%d")
        # else already YYYY-MM-DD

        score = int(score)
        rows.append({"email": email, "signup": signup, "score": score})

# 4. Deduplicate by email — keep highest score
best = {}
for r in rows:
    e = r["email"]
    if e not in best or r["score"] > best[e]["score"]:
        best[e] = r

# 5. Sort by email ascending
result = sorted(best.values(), key=lambda r: r["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
