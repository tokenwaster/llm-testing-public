import csv
import json
from datetime import datetime

records = {}
with open('data.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        email = row['email'].strip()
        score_text = row['score'].strip()
        if not email or '@' not in email or not score_text:
            continue
        email = email.lower()
        signup = row['signup'].strip()
        if '/' in signup:
            signup = datetime.strptime(signup, '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            signup = datetime.strptime(signup, '%Y-%m-%d').strftime('%Y-%m-%d')
        score = int(score_text)
        record = {'email': email, 'signup': signup, 'score': score}
        if email not in records or score > records[email]['score']:
            records[email] = record

result = [records[email] for email in sorted(records)]
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
