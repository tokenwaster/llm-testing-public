import csv
import json
from datetime import datetime

records = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get("email") or "").strip()
        signup = (row.get("signup") or "").strip()
        score = (row.get("score") or "").strip()

        # Rule 1: drop invalid rows
        if "@" not in email or email == "" or score == "":
            continue

        # Rule 2: normalize email
        email = email.lower()

        # Rule 3: normalize dates
        if "/" in signup:
            dt = datetime.strptime(signup, "%d/%m/%Y")
        else:
            dt = datetime.strptime(signup, "%Y-%m-%d")
        signup = dt.strftime("%Y-%m-%d")

        score = int(score)

        records.append({"email": email, "signup": signup, "score": score})

# Rule 4: deduplicate by email, keep highest score
best = {}
for r in records:
    if r["email"] not in best or r["score"] > best[r["email"]]["score"]:
        best[r["email"]] = r

# Rule 5: sort by email ascending
result = sorted(best.values(), key=lambda r: r["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
