import csv
import json
from datetime import datetime

input_path = "data.csv"
output_path = "output.json"

records = {}  # email -> {email, signup, score}

with open(input_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email_raw = (row.get("email") or "").strip()
        signup_raw = (row.get("signup") or "").strip()
        score_raw = (row.get("score") or "").strip()

        # 1. Drop invalid rows
        if not email_raw or "@" not in email_raw or not score_raw:
            continue

        # 2. Normalize email
        email = email_raw.lower()

        # score to int (strip; if fails, treat as invalid? spec says only empty is invalid, but be safe)
        try:
            score = int(score_raw)
        except ValueError:
            try:
                score = int(float(score_raw))
            except ValueError:
                continue

        # 3. Normalize dates
        signup = signup_raw
        if "/" in signup:
            # DD/MM/YYYY -> YYYY-MM-DD
            dt = datetime.strptime(signup, "%d/%m/%Y")
            signup = dt.strftime("%Y-%m-%d")
        else:
            # Validate YYYY-MM-DD (keep as is)
            dt = datetime.strptime(signup, "%Y-%m-%d")
            signup = dt.strftime("%Y-%m-%d")

        # 4. Deduplicate: keep highest score
        if email not in records or score > records[email]["score"]:
            records[email] = {"email": email, "signup": signup, "score": score}

# 5. Sort by email ascending
sorted_records = sorted(records.values(), key=lambda r: r["email"])

with open(output_path, "w", encoding="utf-8") as out:
    json.dump(sorted_records, out, indent=2)

print(f"Wrote {len(sorted_records)} records to {output_path}")
for r in sorted_records:
    print(r)
