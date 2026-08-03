#!/usr/bin/env python3
import csv
import json
from datetime import datetime

input_path = 'data.csv'
output_path = 'output.json'

rows = []
with open(input_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score_str = row.get('score', '').strip()

        # Rule 1: Drop invalid rows (no @, empty email, or empty score)
        if '@' not in email:
            continue
        if email == '':
            continue
        if score_str == '':
            continue

        try:
            score = int(score_str)
        except ValueError:
            # If score is non-integer, also invalid (though spec says empty only)
            continue

        rows.append({
            'email': email,
            'signup': signup,
            'score': score
        })

# Rule 2: Normalize emails to lowercase
for r in rows:
    r['email'] = r['email'].lower()

# Rule 3: Normalize dates
def normalize_date(date_str):
    # Try YYYY-MM-DD first (contains hyphen, no slash)
    if '-' in date_str and '/' not in date_str:
        return date_str
    # Assume DD/MM/YYYY format
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        # If parsing fails, keep original? But should not happen per spec.
        return date_str

for r in rows:
    r['signup'] = normalize_date(r['signup'])

# Rule 4: Deduplicate by email (keep highest score)
email_to_row = {}
for r in rows:
    email = r['email']
    if email not in email_to_row or r['score'] > email_to_row[email]['score']:
        email_to_row[email] = r

# Extract deduplicated list and Rule 5: sort by email ascending
final_rows = sorted(email_to_row.values(), key=lambda x: x['email'])

# Output format ensures only required keys, integer score is string to int already.
output = []
for r in final_rows:
    output.append({
        'email': r['email'],
        'signup': r['signup'],
        'score': r['score']
    })

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"Wrote {len(output)} rows to {output_path}")
