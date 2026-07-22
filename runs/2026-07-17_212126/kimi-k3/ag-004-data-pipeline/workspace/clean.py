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

# 1. Drop invalid rows (email without '@', empty email, empty score)
valid = []
with open("data.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        email = (row["email"] or "").strip()
        score = (row["score"] or "").strip()
        if not email or "@" not in email or not score:
            continue
        # 2. Normalize emails to lowercase
        email = email.lower()
        # 3. Normalize dates to YYYY-MM-DD
        signup = normalize_date(row["signup"])
        valid.append({"email": email, "signup": signup, "score": int(score)})

# 4. Deduplicate by email, keeping the highest score
best = {}
for rec in valid:
    if rec["email"] not in best or rec["score"] > best[rec["email"]]["score"]:
        best[rec["email"]] = rec

# 5. Sort by email ascending
result = sorted(best.values(), key=lambda r: r["email"])

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
