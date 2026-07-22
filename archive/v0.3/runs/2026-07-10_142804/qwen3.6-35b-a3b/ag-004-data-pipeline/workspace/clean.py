import csv
import json
from datetime import datetime

# Read CSV
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Step 1: Drop invalid rows
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

# Step 3: Normalize dates
def normalize_date(date_str):
    date_str = date_str.strip()
    # Try YYYY-MM-DD first
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    # Try DD/MM/YYYY
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    return date_str

for row in valid_rows:
    row['signup'] = normalize_date(row['signup'])

# Step 4: Deduplicate by email, keep highest score
email_map = {}
for row in valid_rows:
    email = row['email']
    score = int(row['score'])
    if email not in email_map or score > email_map[email][1]:
        email_map[email] = (row, score)

# Step 5: Sort by email ascending
sorted_emails = sorted(email_map.keys())
result = []
for email in sorted_emails:
    row, _ = email_map[email]
    result.append({
        'email': row['email'],
        'signup': row['signup'],
        'score': int(row['score'])
    })

# Write output
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
