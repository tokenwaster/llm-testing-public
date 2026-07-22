import csv
from datetime import datetime
import json

def normalize_email(email):
    return email.lower()

def normalize_date(date_str):
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None  # Should not happen per problem constraints

records = []

with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email, signup, score = row['email'], row['signup'], row['score']

        # Step 1: Drop invalid rows
        if not email or '@' not in email or not score:
            continue

        try:
            score = int(score)
        except ValueError:
            continue

        # Steps 2-3: Normalize email and date
        normalized_email = normalize_email(email)
        signup_date = normalize_date(signup) or signup  # Fallback in case parsing fails

        records.append({
            'email': normalized_email,
            'signup': signup_date,
            'score': score
        })

# Step 4: Deduplicate by email (keep highest score)
unique_records = {}
for r in records:
    key = r['email']
    if key not in unique_records or r['score'] > unique_records[key]['score']:
        unique_records[key] = r

# Step 5: Sort by email
sorted_records = sorted(unique_records.values(), key=lambda x: x['email'])

with open('output.json', 'w') as f:
    json.dump(sorted_records, f)