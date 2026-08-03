import csv
import json
from datetime import datetime

# Read raw CSV
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Step 1: Drop invalid rows
# - email is empty or contains no '@'
# - score is empty
def is_valid(row):
    email = row.get("email", "").strip()
    score = row.get("score", "").strip()
    if not email or "@" not in email:
        return False
    if not score:
        return False
    return True

rows = [r for r in rows if is_valid(r)]

# Step 2: Normalize emails to lowercase
for r in rows:
    r["email"] = r["email"].strip().lower()

# Step 3: Normalize dates
def normalize_date(date_str):
    date_str = date_str.strip()
    # Try YYYY-MM-DD first
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    # Try DD/MM/YYYY
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    raise ValueError(f"Unrecognized date format: {date_str!r}")

for r in rows:
    r["signup"] = normalize_date(r["signup"])

# Convert score to int
for r in rows:
    r["score"] = int(r["score"].strip())

# Step 4: Deduplicate by email — keep highest score
best = {}
for r in rows:
    email = r["email"]
    if email not in best or r["score"] > best[email]["score"]:
        best[email] = r

rows = list(best.values())

# Step 5: Sort by email ascending
rows.sort(key=lambda r: r["email"])

# Build output as list of dicts with exact keys
output = [{"email": r["email"], "signup": r["signup"], "score": r["score"]} for r in rows]

# Write output.json
with open("output.json", "w") as f:
    json.dump(output, f, indent=2)

print("Done! output.json contents:")
print(json.dumps(output, indent=2))
