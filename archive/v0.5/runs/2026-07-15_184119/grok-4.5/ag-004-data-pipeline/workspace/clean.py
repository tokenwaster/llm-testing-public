import csv
import json
from datetime import datetime

rows = []
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get("email") or "").strip()
        signup = (row.get("signup") or "").strip()
        score_raw = (row.get("score") or "").strip()

        # 1. Drop invalid rows
        if not email or "@" not in email or not score_raw:
            continue

        try:
            score = int(score_raw)
        except ValueError:
            continue

        # 2. Normalize emails
        email = email.lower()

        # 3. Normalize dates
        if "/" in signup:
            # DD/MM/YYYY
            dt = datetime.strptime(signup, "%d/%m/%Y")
            signup = dt.strftime("%Y-%m-%d")
        else:
            # Already YYYY-MM-DD — validate
            datetime.strptime(signup, "%Y-%m-%d")

        rows.append({"email": email, "signup": signup, "score": score})

# 4. Deduplicate by email — keep highest score
best = {}
for r in rows:
    e = r["email"]
    if e not in best or r["score"] > best[e]["score"]:
        best[e] = r

# 5. Sort by email ascending
result = sorted(best.values(), key=lambda x: x["email"])

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
