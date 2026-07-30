import csv
import json

with open("data.csv", newline="") as f:
    rows = list(csv.DictReader(f))

# 1. Drop invalid rows
clean = []
for r in rows:
    email = r["email"].strip()
    score = r["score"].strip()
    if not email or "@" not in email or not score:
        continue
    clean.append(r)

# 2. Normalize emails to lowercase
for r in clean:
    r["email"] = r["email"].strip().lower()

# 3. Normalize dates
def norm_date(d):
    d = d.strip()
    if "/" in d:
        dd, mm, yyyy = d.split("/")
        return f"{yyyy}-{int(mm):02d}-{int(dd):02d}"
    return d

for r in clean:
    r["signup"] = norm_date(r["signup"])

# 4. Deduplicate by email, keep highest score
best = {}
for r in clean:
    e = r["email"]
    s = int(r["score"].strip())
    if e not in best or s > best[e]["score"]:
        best[e] = {"email": e, "signup": r["signup"], "score": s}

records = list(best.values())

# 5. Sort by email ascending
records.sort(key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(records, f, indent=2)

print(json.dumps(records, indent=2))
