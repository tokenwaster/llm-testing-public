import csv
import json
import re

def normalize_date(s):
    s = s.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        dd, mm, yyyy = m.groups()
        return f"{yyyy}-{mm}-{dd}"
    raise ValueError(f"Unrecognized date format: {s!r}")

# 1. Drop invalid rows (no '@', empty email, empty score)
rows = []
with open("data.csv", newline="") as f:
    for row in csv.DictReader(f):
        email = (row["email"] or "").strip()
        score = (row["score"] or "").strip()
        if not email or "@" not in email or not score:
            continue
        # 2. Normalize emails
        email = email.lower()
        # 3. Normalize dates
        signup = normalize_date(row["signup"])
        rows.append({"email": email, "signup": signup, "score": int(score)})

# 4. Deduplicate by email, keep highest score
best = {}
for r in rows:
    if r["email"] not in best or r["score"] > best[r["email"]]["score"]:
        best[r["email"]] = r

# 5. Sort by email ascending
result = [best[k] for k in sorted(best)]

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)
    f.write("\n")

print(json.dumps(result, indent=2))
