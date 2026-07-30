import csv
import json
import re

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get("email") or "").strip()
        signup = (row.get("signup") or "").strip()
        score = (row.get("score") or "").strip()

        # Rule 1: drop invalid rows
        if not email or "@" not in email or not score:
            continue

        # Rule 2: normalize email
        email = email.lower()

        # Rule 3: normalize date
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", signup):
            date = signup
        else:
            m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", signup)
            if not m:
                continue  # unparseable date; cannot produce required output format
            dd, mm, yyyy = m.groups()
            date = f"{yyyy}-{mm}-{dd}"

        rows.append({"email": email, "signup": date, "score": int(score)})

# Rule 4: deduplicate by email, keeping highest score
best = {}
for r in rows:
    if r["email"] not in best or r["score"] > best[r["email"]]["score"]:
        best[r["email"]] = r

# Rule 5: sort by email ascending
result = [best[e] for e in sorted(best)]

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
