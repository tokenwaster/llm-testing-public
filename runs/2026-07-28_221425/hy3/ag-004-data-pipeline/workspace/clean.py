import csv
import json
from datetime import datetime


def normalize_date(value):
    value = value.strip()
    if "/" in value:
        # DD/MM/YYYY -> YYYY-MM-DD
        d = datetime.strptime(value, "%d/%m/%Y")
        return d.strftime("%Y-%m-%d")
    # assume YYYY-MM-DD
    return value


records = {}
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get("email") or "").strip()
        score_raw = (row.get("score") or "").strip()
        signup = (row.get("signup") or "").strip()

        # Rule 1: drop invalid rows
        if "@" not in email or email == "" or score_raw == "":
            continue

        # Rule 2: normalize email lowercase
        email = email.lower()

        # Rule 3: normalize date
        signup = normalize_date(signup)

        score = int(score_raw)

        # Rule 4: dedupe by email, keep highest score
        if email not in records or score > records[email]["score"]:
            records[email] = {"email": email, "signup": signup, "score": score}

# Rule 5: sort by email ascending
result = [records[k] for k in sorted(records.keys())]

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
