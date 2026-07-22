import csv
import json
from datetime import datetime
from pathlib import Path

# Read CSV
csv_path = Path("data.csv")
data = []

with open(csv_path, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

# Step 1: Drop invalid rows
valid_data = []
for row in data:
    email = row.get("email", "").strip()
    score = row.get("score", "").strip()

    # Invalid if: email contains no @, email is empty, or score is empty
    if not email or "@" not in email or not score:
        continue

    valid_data.append(row)

# Step 2: Normalize emails to lowercase
for row in valid_data:
    row["email"] = row["email"].lower()

# Step 3: Normalize dates
for row in valid_data:
    signup = row["signup"].strip()
    # Check if format is DD/MM/YYYY
    if "/" in signup:
        try:
            dt = datetime.strptime(signup, "%d/%m/%Y")
            row["signup"] = dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    # Otherwise assume it's already YYYY-MM-DD

# Step 4: Deduplicate by email, keep highest score
email_to_row = {}
for row in valid_data:
    email = row["email"]
    score = int(row["score"])

    if email not in email_to_row or score > int(email_to_row[email]["score"]):
        email_to_row[email] = row

deduped_data = list(email_to_row.values())

# Step 5: Sort by email ascending
deduped_data.sort(key=lambda row: row["email"])

# Convert to output format
output = []
for row in deduped_data:
    output.append({
        "email": row["email"],
        "signup": row["signup"].strip(),
        "score": int(row["score"])
    })

# Write to output.json
output_path = Path("output.json")
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"Cleaned data written to {output_path}")
print(f"Total records: {len(output)}")
for record in output:
    print(record)
