import csv, json, re
from datetime import datetime

rows = []
with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    for r in reader:
        email = (r.get('email') or '').strip()
        signup = (r.get('signup') or '').strip()
        score_s = (r.get('score') or '').strip()

        # Rule 1: drop invalid
        if not email or '@' not in email or not score_s:
            continue

        # Rule 2: normalize email lowercase
        email = email.lower()

        # Rule 3: normalize date
        if re.match(r'^\d{4}-\d{2}-\d{2}$', signup):
            pass  # already YYYY-MM-DD
        elif re.match(r'^\d{2}/\d{2}/\d{4}$', signup):
            dt = datetime.strptime(signup, '%d/%m/%Y')
            signup = dt.strftime('%Y-%m-%d')

        score = int(score_s)

        rows.append({'email': email, 'signup': signup, 'score': score})

# Rule 4: deduplicate by email keeping highest score
best = {}
for r in rows:
    e = r['email']
    if e not in best or r['score'] > best[e]['score']:
        best[e] = r

# Rule 5: sort by email ascending
result = sorted(best.values(), key=lambda x: x['email'])

with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
