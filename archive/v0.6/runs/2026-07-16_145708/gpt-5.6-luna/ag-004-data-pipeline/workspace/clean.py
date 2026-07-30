import csv
import json
from datetime import datetime

best = {}
with open('data.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        email = row['email'].strip()
        score_text = row['score'].strip()
        if not email or '@' not in email or not score_text:
            continue
        email = email.lower()
        signup = row['signup'].strip()
        if '-' in signup:
            normalized_signup = datetime.strptime(signup, '%Y-%m-%d').strftime('%Y-%m-%d')
        else:
            normalized_signup = datetime.strptime(signup, '%d/%m/%Y').strftime('%Y-%m-%d')
        record = {
            'email': email,
            'signup': normalized_signup,
            'score': int(score_text),
        }
        if email not in best or record['score'] > best[email]['score']:
            best[email] = record

result = [best[email] for email in sorted(best)]
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
