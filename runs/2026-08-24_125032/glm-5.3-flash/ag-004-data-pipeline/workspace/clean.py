import csv
import json
from datetime import datetime

rows = []
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for raw in reader:
        rows.append({(k or "").strip(): (v or "").strip() for k, v in raw.items()})

# Rule 1: drop invalid rows (no '@' in email, empty email, or empty score)
valid = []
for r in rows:
    email = r.get("email", "")
    score = r.get("score", "")
    if not email or "@" not in email or not score:
        continue
    valid.append(r)

# Rule 2: normalize emails to lowercase
for r in valid:
    r["email"] = r["email"].lower()

# Rule 3: normalize dates to YYYY-MM-DD
def norm_date(s):
    s = s.strip()
    if "/" in s:
        return datetime.strptime(s, "%d/%m/%Y").strftime("%Y-%m-%d")
    # already YYYY-MM-DD; validate/normalize
    return datetime.strptime(s, "%Y-%m-%d").strftime("%Y-%m-%d")

for r in valid:
    r["signup"] = norm_date(r["signup"])

# Rule 4: deduplicate by email keeping highest score
best = {}
for r in valid:
    e = r["email"]
    sc = int(r["score"])
    if e not in best or sc > best[e][0]:
        best[e] = (sc, r)

records = [
    {"email": e, "signup": r["signup"], "score": sc}
    for e, (sc, r) in best.items()
]

# Rule 5: sort by email ascending
records.sort(key=lambda x: x["email"])

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2)

print(json.dumps(records, indent=2))
