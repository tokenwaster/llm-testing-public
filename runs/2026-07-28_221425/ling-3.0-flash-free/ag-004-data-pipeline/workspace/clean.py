import csv
import json
from datetime import datetime

rows = []
with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# 1. Drop invalid rows: email has no '@', email is empty, or score is empty
valid = []
for row in rows:
    email = row['email'].strip()
    signup = row['signup'].strip()
    score = row['score'].strip()
    if '@' not in email or email == '' or score == '':
        continue
    valid.append({'email': email, 'signup': signup, 'score': int(score)})

# 2. Normalize emails to lowercase
for row in valid:
    row['email'] = row['email'].lower()

# 3. Normalize dates: DD/MM/YYYY -> YYYY-MM-DD, YYYY-MM-DD stays
for row in valid:
    d = row['signup']
    if '/' in d:
        # DD/MM/YYYY
        dt = datetime.strptime(d, '%d/%m/%Y')
        row['signup'] = dt.strftime('%Y-%m-%d')
    # else already YYYY-MM-DD

# 4. Deduplicate by email, keep highest score
best = {}
for row in valid:
    email = row['email']
    if email not in best or row['score'] > best[email]['score']:
        best[email] = row

# 5. Sort by email ascending
result = sorted(best.values(), key=lambda r: r['email'])

# Output
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))