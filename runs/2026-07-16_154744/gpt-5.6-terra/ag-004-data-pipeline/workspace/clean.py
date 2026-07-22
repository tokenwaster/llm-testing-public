import csv
import json
from datetime import datetime

best = {}
with open('data.csv', newline='', encoding='utf-8') as source:
    for row in csv.DictReader(source):
        email = row['email']
        score = row['score']
        if not email or '@' not in email or not score:
            continue
        email = email.lower()
        signup = row['signup']
        if '/' in signup:
            signup = datetime.strptime(signup, '%d/%m/%Y').strftime('%Y-%m-%d')
        record = {'email': email, 'signup': signup, 'score': int(score)}
        if email not in best or record['score'] > best[email]['score']:
            best[email] = record

result = [best[email] for email in sorted(best)]
with open('output.json', 'w', encoding='utf-8') as target:
    json.dump(result, target, indent=2)
    target.write('\n')
