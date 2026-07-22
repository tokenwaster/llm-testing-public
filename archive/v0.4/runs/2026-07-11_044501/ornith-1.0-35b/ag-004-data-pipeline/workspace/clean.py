import csv
import json
from datetime import datetime

records = []
with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        signup_raw = row.get('signup', '').strip()
        score_raw = row.get('score', '').strip()

        # Rule 1: drop invalid rows
        if not email or '@' not in email or not score_raw:
            continue

        # Rule 2: normalize email to lowercase
        email = email.lower()

        # Rule 3: normalize dates
        if '-' in signup_raw and len(signup_raw.split('-')) == 3:
            # YYYY-MM-DD already
            signup = signup_raw
        elif '/' in signup_raw:
            # DD/MM/YYYY
            dt = datetime.strptime(signup_raw, '%d/%m/%Y')
            signup = dt.strftime('%Y-%m-%d')
        else:
            continue

        score = int(score_raw)
        records.append({'email': email, 'signup': signup, 'score': score})

# Rule 4: deduplicate by email, keep highest score
best = {}
for r in records:
    e = r['email']
    if e not in best or r['score'] > best[e]['score']:
        best[e] = r

# Rule 5: sort by email ascending
result = sorted(best.values(), key=lambda x: x['email'])

with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
