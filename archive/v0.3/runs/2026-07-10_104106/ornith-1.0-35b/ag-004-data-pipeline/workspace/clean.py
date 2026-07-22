import csv
import json
from datetime import datetime

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        email = r.get("email", "").strip()
        signup = r.get("signup", "").strip()
        score_str = r.get("score", "").strip()

        # Rule 1: drop invalid rows
        if not email or "@" not in email or not score_str:
            continue

        # Rule 2: normalize email to lowercase
        email = email.lower()

        # Rule 3: normalize date
        try:
            dt = datetime.strptime(signup, "%Y-%m-%d")
        except ValueError:
            dt = datetime.strptime(signup, "%d/%m/%Y")
        signup_norm = dt.strftime("%Y-%m-%d")

        score = int(score_str)
        rows.append({"email": email, "signup": signup_norm, "score": score})

# Rule 4: deduplicate by email, keep highest score
best = {}
for r in rows:
    e = r["email"]
    if e not in best or r["score"] > best[e]["score"]:
        best[e] = r

# Rule 5: sort by email ascending
result = sorted(best.values(), key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
