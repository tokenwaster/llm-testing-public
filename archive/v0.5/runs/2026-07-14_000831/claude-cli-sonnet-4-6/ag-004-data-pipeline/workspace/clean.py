import csv
import json
from datetime import datetime

workspace = r"E:\Programming\LLM Testing\runs\2026-07-14_000831\claude-cli-sonnet\ag-004-data-pipeline\workspace"

rows = []
with open(f"{workspace}/data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row["email"].strip()
        signup = row["signup"].strip()
        score = row["score"].strip()

        # Rule 1: drop invalid rows
        if not email or "@" not in email or not score:
            continue

        # Rule 2: normalize email
        email = email.lower()

        # Rule 3: normalize date
        if "/" in signup:
            signup = datetime.strptime(signup, "%d/%m/%Y").strftime("%Y-%m-%d")

        rows.append({"email": email, "signup": signup, "score": int(score)})

# Rule 4: deduplicate by email, keep highest score
best = {}
for r in rows:
    e = r["email"]
    if e not in best or r["score"] > best[e]["score"]:
        best[e] = r

# Rule 5: sort by email ascending
result = sorted(best.values(), key=lambda x: x["email"])

with open(f"{workspace}/output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
