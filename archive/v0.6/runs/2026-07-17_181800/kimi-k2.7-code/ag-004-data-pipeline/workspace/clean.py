import csv
import json
from datetime import datetime

records = []
with open('data.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score_str = row.get('score', '').strip()

        # Rule 1: Drop invalid rows
        if not email or '@' not in email or not score_str:
            continue

        # Rule 2: Normalize emails to lowercase
        email = email.lower()

        # Rule 3: Normalize dates
        if '/' in signup:
            # DD/MM/YYYY
            dt = datetime.strptime(signup, '%d/%m/%Y')
            signup = dt.strftime('%Y-%m-%d')
        # else assume YYYY-MM-DD, keep as is

        score = int(score_str)
        records.append({'email': email, 'signup': signup, 'score': score})

# Rule 4: Deduplicate by email, keep highest score
best_by_email = {}
for rec in records:
    email = rec['email']
    if email not in best_by_email or rec['score'] > best_by_email[email]['score']:
        best_by_email[email] = rec

# Rule 5: Sort by email ascending
output = sorted(best_by_email.values(), key=lambda r: r['email'])

with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))
