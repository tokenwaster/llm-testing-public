import csv
import json
from collections import defaultdict

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        email = (r.get("email") or "").strip()
        signup = (r.get("signup") or "").strip()
        score = (r.get("score") or "").strip()
        # Rule 1: drop invalid rows
        if email == "" or "@" not in email or score == "":
            continue
        # Rule 2: normalize email to lowercase
        email = email.lower()
        # Rule 3: normalize dates
        if "/" in signup:
            dd, mm, yyyy = signup.split("/")
            signup = f"{yyyy}-{int(mm):02d}-{int(dd):02d}"
        # score to int
        score = int(score)
        rows.append({"email": email, "signup": signup, "score": score})

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
