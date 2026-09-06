import csv
import json
from datetime import datetime

# Read the CSV file
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# 1. Drop invalid rows: no @ in email, empty email, or empty score
valid_rows = []
for row in rows:
    email = row['email'].strip()
    score = row['score'].strip()
    
    # Check if email is empty or has no @
    if not email or '@' not in email:
        continue
    # Check if score is empty
    if not score:
        continue
    
    valid_rows.append(row)

# 2. Normalize emails to lowercase and 3. Normalize dates
def parse_date(date_str):
    date_str = date_str.strip()
    # Try DD/MM/YYYY format first
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    # Otherwise assume YYYY-MM-DD (keep as is)
    return date_str

cleaned_rows = []
for row in valid_rows:
    email = row['email'].strip().lower()
    signup = parse_date(row['signup'])
    score = int(row['score'].strip())
    cleaned_rows.append({
        'email': email,
        'signup': signup,
        'score': score
    })

# 4. Deduplicate by email, keep highest score
email_best = {}
for row in cleaned_rows:
    email = row['email']
    if email not in email_best or row['score'] > email_best[email]['score']:
        email_best[email] = row

# 5. Sort by email ascending
sorted_rows = sorted(email_best.values(), key=lambda x: x['email'])

# Write to JSON
with open('output.json', 'w') as f:
    json.dump(sorted_rows, f, indent=2)

print("Cleaning complete. Output written to output.json")
