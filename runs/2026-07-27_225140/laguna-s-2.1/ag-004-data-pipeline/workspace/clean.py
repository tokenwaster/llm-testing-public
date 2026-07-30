import csv
import json
from datetime import datetime

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

# 1. Drop invalid rows: no @ in email, empty email, or empty score
valid = []
for r in rows:
    email = r["email"]
    score = r["score"]
    if not email or "@" not in email or not score:
        continue
    valid.append(r)

# 2. Normalize emails to lowercase
for r in valid:
    r["email"] = r["email"].lower()

# 3. Normalize dates: YYYY-MM-DD keep, DD/MM/YYYY convert
def normalize_date(s):
    s = s.strip()
    if "/" in s:
        dt = datetime.strptime(s, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    # assume YYYY-MM-DD
    return s

for r in valid:
    r["signup"] = normalize_date(r["signup"])

# 4. Deduplicate by email, keep highest score
best = {}
for r in valid:
    email = r["email"]
    score = int(r["score"])
    if email not in best or score > best[email]["score"]:
        best[email] = {"email": email, "signup": r["signup"], "score": score}

records = list(best.values())

# 5. Sort by email ascending
records.sort(key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(records, f, indent=2)

print(json.dumps(records, indent=2))
