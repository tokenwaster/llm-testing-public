import csv
import json
from datetime import datetime

# Read the CSV file
data = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

# Step 1: Drop invalid rows (email contains no '@', email is empty, or score is empty)
valid_rows = []
for row in data:
    email = row.get('email', '').strip()
    signup = row.get('signup', '').strip()
    score = row.get('score', '').strip()

    if not email or '@' not in email or not score:
        continue
    valid_rows.append({
        'email': email,
        'signup': signup,
        'score': score
    })

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].lower()

# Step 3: Normalize dates - convert DD/MM/YYYY to YYYY-MM-DD
def normalize_date(date_str):
    # Try parsing as DD/MM/YYYY first (if it contains slashes and is not already YYYY-MM-DD)
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    # Already in YYYY-MM-DD format or can't parse - keep as is (but validate it looks right?)
    # The spec says "YYYY-MM-DD (keep as is) or DD/MM/YYYY (convert)"
    return date_str

for row in valid_rows:
    row['signup'] = normalize_date(row['signup'])

# Step 4: Deduplicate by email - keep highest score per normalized email
email_to_row = {}
for row in valid_rows:
    email = row['email']
    score = int(row['score'])
    if email not in email_to_row or score > int(email_to_row[email]['score']):
        email_to_row[email] = row

deduplicated = list(email_to_row.values())

# Step 5: Sort by email ascending
sorted_rows = sorted(deduplicated, key=lambda r: r['email'])

# Convert to final format (ensure integer score)
output = []
for row in sorted_rows:
    output.append({
        'email': row['email'],
        'signup': row['signup'],
        'score': int(row['score'])
    })

# Write to JSON file
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Processing complete. Output written to output.json")
print(f"Processed {len(output)} valid records.")
