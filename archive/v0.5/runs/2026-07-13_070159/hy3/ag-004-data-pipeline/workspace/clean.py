import csv
import json
from datetime import datetime

records = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get("email") or "").strip()
        score_raw = (row.get("score") or "").strip()
        signup = (row.get("signup") or "").strip()

        # Rule 1: drop invalid rows
        if "@" not in email or email == "" or score_raw == "":
            continue

        # Rule 2: normalize email
        email = email.lower()

        # Rule 3: normalize date
        if "/" in signup:
            dt = datetime.strptime(signup, "%d/%m/%Y")
        else:
            dt = datetime.strptime(signup, "%Y-%m-%d")
        signup = dt.strftime("%Y-%m-%d")

        score = int(score_raw)

        records.append({"email": email, "signup": signup, "score": score})

# Rule 4: deduplicate by email, keep highest score
best = {}
for rec in records:
    e = rec["email"]
    if e not in best or rec["score"] > best[e]["score"]:
        best[e] = rec

# Rule 5: sort by email ascending
result = sorted(best.values(), key=lambda r: r["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
