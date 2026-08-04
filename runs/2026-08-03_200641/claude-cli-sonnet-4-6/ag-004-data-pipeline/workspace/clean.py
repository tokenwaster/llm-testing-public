import csv, json, re
from datetime import datetime

rows = []
with open("data.csv", newline="") as f:
    for row in csv.DictReader(f):
        email = row["email"].strip()
        signup = row["signup"].strip()
        score = row["score"].strip()

        # 1. Drop invalid rows
        if not email or "@" not in email or not score:
            continue

        # 2. Normalize email
        email = email.lower()

        # 3. Normalize date
        if re.match(r"\d{2}/\d{2}/\d{4}", signup):
            signup = datetime.strptime(signup, "%d/%m/%Y").strftime("%Y-%m-%d")

        rows.append({"email": email, "signup": signup, "score": int(score)})

# 4. Deduplicate by email, keep highest score
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
