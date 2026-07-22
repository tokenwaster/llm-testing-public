import csv
import json
from datetime import datetime

# Read CSV
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Rule 1: Drop invalid rows
valid_rows = []
for row in rows:
    email = row.get('email', '').strip()
    score = row.get('score', '').strip()

    # Check for invalid conditions
    if not email or '@' not in email or not score:
        continue

    valid_rows.append(row)

# Rule 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].lower()

# Rule 3: Normalize dates
for row in valid_rows:
    signup = row['signup'].strip()
    if '/' in signup:
        # DD/MM/YYYY format
        date_obj = datetime.strptime(signup, '%d/%m/%Y')
        row['signup'] = date_obj.strftime('%Y-%m-%d')
    # else: already YYYY-MM-DD format, keep as is

# Rule 4: Deduplicate by email, keeping highest score
email_best = {}
for row in valid_rows:
    email = row['email']
    score = int(row['score'])

    if email not in email_best or score > email_best[email]['score']:
        email_best[email] = {
            'email': email,
            'signup': row['signup'],
            'score': score
        }

# Rule 5: Sort by email ascending
sorted_rows = sorted(email_best.values(), key=lambda x: x['email'])

# Write JSON
with open('output.json', 'w') as f:
    json.dump(sorted_rows, f, indent=2)

print(f"Cleaned {len(sorted_rows)} records")
for row in sorted_rows:
    print(row)
