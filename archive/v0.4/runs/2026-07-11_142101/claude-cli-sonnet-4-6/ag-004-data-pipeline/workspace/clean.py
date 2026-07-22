import csv
import json
import re

def parse_date(value):
    if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        return value
    if re.match(r'^\d{2}/\d{2}/\d{4}$', value):
        day, month, year = value.split('/')
        return f'{year}-{month}-{day}'
    return None

rows = []
with open('data.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score_str = row.get('score', '').strip()

        if not email or '@' not in email or not score_str:
            continue

        email = email.lower()
        date = parse_date(signup)
        score = int(score_str)
        rows.append({'email': email, 'signup': date, 'score': score})

# Deduplicate: keep highest score per email
best = {}
for r in rows:
    e = r['email']
    if e not in best or r['score'] > best[e]['score']:
        best[e] = r

result = sorted(best.values(), key=lambda x: x['email'])

with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
