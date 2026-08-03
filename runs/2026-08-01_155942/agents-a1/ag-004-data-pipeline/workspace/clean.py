import csv
import json
from datetime import datetime

# Read CSV
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Step 1: Drop invalid rows (email no @, empty email, or empty score)
valid_rows = []
for r in rows:
    email = r['email'].strip()
    if not email or '@' not in email:
        continue
    score_str = r['score'].strip()
    if not score_str:
        continue
    valid_rows.append(r)

# Step 2: Normalize emails to lowercase
for r in valid_rows:
    r['email'] = r['email'].strip().lower()

# Step 3: Normalize dates (convert DD/MM/YYYY to YYYY-MM-DD)
def normalize_date(date_str):
    date_str = date_str.strip()
    # Try parsing as YYYY-MM-DD first
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        pass
    # Must be DD/MM/YYYY
    dt = datetime.strptime(date_str, '%d/%m/%Y')
    return dt.strftime('%Y-%m-%d')

for r in valid_rows:
    r['signup'] = normalize_date(r['signup'])
    r['score_int'] = int(r['score'].strip())

# Step 4: Deduplicate by email, keep highest score per email
email_to_row = {}
for r in valid_rows:
    email = r['email']
    if email not in email_to_row or r['score_int'] > email_to_row[email]['score_int']:
        email_to_row[email] = r

# Step 5: Sort by email ascending
result = sorted(email_to_row.values(), key=lambda x: x['email'])

# Build final output with exact keys and types
output = []
for r in result:
    output.append({
        'email': r['email'],
        'signup': r['signup'],
        'score': r['score_int']
    })

with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))
