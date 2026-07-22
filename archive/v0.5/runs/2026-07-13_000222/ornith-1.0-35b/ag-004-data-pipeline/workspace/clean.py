import csv
import json
from datetime import datetime

records = []
with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get('email') or '').strip()
        signup = (row.get('signup') or '').strip()
        score_str = (row.get('score') or '').strip()

        # Rule 1: drop invalid rows
        if not email or '@' not in email or not score_str:
            continue

        # Rule 2: normalize email to lowercase
        email = email.lower()

        # Rule 3: normalize dates
        if '-' in signup and len(signup.split('-')) == 3:
            # YYYY-MM-DD
            normalized_date = signup
        elif '/' in signup:
            # DD/MM/YYYY
            dt = datetime.strptime(signup, '%d/%m/%Y')
            normalized_date = dt.strftime('%Y-%m-%d')
        else:
            continue

        score = int(score_str)
        records.append({'email': email, 'signup': normalized_date, 'score': score})

# Rule 4: deduplicate by email, keep highest score
best = {}
for r in records:
    if r['email'] not in best or r['score'] > best[r['email']]['score']:
        best[r['email']] = r

# Rule 5: sort by email ascending
result = sorted(best.values(), key=lambda x: x['email'])

with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
