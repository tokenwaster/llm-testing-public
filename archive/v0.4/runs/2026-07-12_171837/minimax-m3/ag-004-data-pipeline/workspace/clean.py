import csv
import json
from datetime import datetime

rows_in = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows_in.append(row)

# 1. Drop invalid rows
def is_valid(row):
    email = (row.get("email") or "").strip()
    if not email or "@" not in email:
        return False
    score = (row.get("score") or "").strip()
    if not score:
        return False
    return True

rows = [r for r in rows_in if is_valid(r)]

# 2. Normalize emails to lowercase
for r in rows:
    r["email"] = r["email"].strip().lower()

# 3. Normalize dates
def normalize_date(s):
    s = s.strip()
    # Try YYYY-MM-DD first
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date: {s}")

for r in rows:
    r["signup"] = normalize_date(r["signup"])
    r["score"] = int(r["score"])

# 4. Deduplicate by email, keep highest score
by_email = {}
for r in rows:
    e = r["email"]
    if e not in by_email or r["score"] > by_email[e]["score"]:
        by_email[e] = r

deduped = list(by_email.values())

# 5. Sort by email ascending
deduped.sort(key=lambda r: r["email"])

# Build output with only the required keys
output = [{"email": r["email"], "signup": r["signup"], "score": r["score"]} for r in deduped]

with open("output.json", "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))
