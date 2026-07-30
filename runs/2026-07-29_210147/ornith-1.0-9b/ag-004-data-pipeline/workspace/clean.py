import csv, json, re
from datetime import datetime

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        email = r["email"]
        signup = r["signup"].strip()
        score_str = (r["score"] or "").strip()

        # 1. Drop invalid rows
        if not email:
            continue
        if "@" not in email:
            continue
        if not score_str:
            continue

        # Normalize email to lowercase
        email = email.lower()

        # Parse and normalize date
        signup_normalized = None
        try:
            # Try YYYY-MM-DD first
            d = datetime.strptime(signup, "%Y-%m-%d")
            signup_normalized = d.strftime("%Y-%m-%d")
        except ValueError:
            # Try DD/MM/YYYY
            d = datetime.strptime(signup, "%d/%m/%Y")
            signup_normalized = d.strftime("%Y-%m-%d")

        score = int(score_str)
        rows.append({"email": email, "signup": signup_normalized, "score": score})

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
