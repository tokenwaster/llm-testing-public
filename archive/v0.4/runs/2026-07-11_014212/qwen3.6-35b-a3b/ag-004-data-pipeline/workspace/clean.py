import csv
import json
from datetime import datetime

rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score_str = row.get('score', '').strip()

        # Rule 1: Drop invalid rows
        if not email or '@' not in email or not score_str:
            continue

        # Rule 2: Normalize email to lowercase
        email = email.lower()

        # Rule 3: Normalize date
        try:
            # Try YYYY-MM-DD first
            dt = datetime.strptime(signup, '%Y-%m-%d')
        except ValueError:
            # Try DD/MM/YYYY
            dt = datetime.strptime(signup, '%d/%m/%Y')
        signup_normalized = dt.strftime('%Y-%m-%d')

        score = int(score_str)

        rows.append({'email': email, 'signup': signup_normalized, 'score': score})

# Rule 4: Deduplicate by email, keep highest score
email_map = {}
for row in rows:
    email = row['email']
    if email not in email_map or row['score'] > email_map[email]['score']:
        email_map[email] = row

# Rule 5: Sort by email ascending
result = sorted(email_map.values(), key=lambda x: x['email'])

with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
