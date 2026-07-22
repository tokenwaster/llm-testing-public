import csv
import json
from datetime import datetime

# Read the CSV file
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Step 1: Drop invalid rows (email contains no '@', email empty, or score empty)
valid_rows = []
for row in rows:
    email = row['email'].strip()
    score = row['score'].strip()
    if not email or '@' not in email or not score:
        continue
    valid_rows.append(row)

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].strip().lower()

# Step 3: Normalize dates (YYYY-MM-DD or DD/MM/YYYY -> YYYY-MM-DD)
def normalize_date(date_str):
    date_str = date_str.strip()
    if '-' in date_str:
        return date_str  # already YYYY-MM-DD
    else:
        # Assume DD/MM/YYYY format
        parts = date_str.split('/')
        if len(parts) == 3:
            day, month, year = parts
            return f"{year}-{month}-{day}"
        return date_str

for row in valid_rows:
    row['signup'] = normalize_date(row['signup'])

# Step 4: Deduplicate by email, keeping highest score per email
email_to_row = {}
for row in valid_rows:
    email = row['email']
    score = int(row['score'].strip())
    if email not in email_to_row or score > email_to_row[email]['score']:
        email_to_row[email] = {
            'email': email,
            'signup': row['signup'],
            'score': score
        }

# Step 5: Sort by email ascending
result = sorted(email_to_row.values(), key=lambda x: x['email'])

# Write to output.json
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Done! Output written to output.json")
