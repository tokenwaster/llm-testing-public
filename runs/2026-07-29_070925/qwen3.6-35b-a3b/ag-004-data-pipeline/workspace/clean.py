import csv
import json
from datetime import datetime

records = []

with open('data.csv', 'r', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row['email'].strip()
        signup = row['signup'].strip()
        score_str = row['score'].strip()

        # Step 1: Drop invalid rows
        if '@' not in email or email == '':
            continue
        if score_str == '':
            continue

        # Step 2: Normalize emails to lowercase
        email_lower = email.lower()

        # Step 3: Normalize dates
        try:
            dt = datetime.strptime(signup, '%Y-%m-%d')
        except ValueError:
            try:
                dt = datetime.strptime(signup, '%d/%m/%Y')
            except ValueError:
                continue  # skip if date format is unknown
        signup_normalized = dt.strftime('%Y-%m-%d')

        score = int(score_str)

        records.append({
            'email': email_lower,
            'signup': signup_normalized,
            'score': score
        })

# Step 4: Deduplicate by email, keep highest score
max_score_by_email = {}
for rec in records:
    email = rec['email']
    if email not in max_score_by_email or rec['score'] > max_score_by_email[email]['score']:
        max_score_by_email[email] = rec

# Step 5: Sort by email ascending
result = sorted(max_score_by_email.values(), key=lambda r: r['email'])

with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
