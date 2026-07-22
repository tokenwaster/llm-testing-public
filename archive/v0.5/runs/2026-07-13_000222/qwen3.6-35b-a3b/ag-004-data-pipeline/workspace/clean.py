import csv
import json
from datetime import datetime

# Read CSV
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Step 1: Drop invalid rows (email has no @, email is empty, or score is empty)
valid_rows = []
for row in rows:
    email = row.get('email', '').strip()
    score = row.get('score', '').strip()
    if not email or '@' not in email or not score:
        continue
    valid_rows.append(row)

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].strip().lower()

# Step 3: Normalize dates - convert DD/MM/YYYY to YYYY-MM-DD
def normalize_date(date_str):
    date_str = date_str.strip()
    # Try DD/MM/YYYY format
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return date_str  # Already YYYY-MM-DD

for row in valid_rows:
    row['signup'] = normalize_date(row['signup'])

# Step 4: Deduplicate by email, keep highest score
email_map = {}
for row in valid_rows:
    email = row['email']
    score = int(row['score'])
    if email not in email_map or score > int(email_map[email]['score']):
        email_map[email] = row

# Step 5: Sort by email ascending
sorted_emails = sorted(email_map.keys())

# Build output
output = []
for email in sorted_emails:
    row = email_map[email]
    output.append({
        "email": row['email'],
        "signup": row['signup'],
        "score": int(row['score'])
    })

# Write output
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Done. Output:")
print(json.dumps(output, indent=2))
