import csv
import json
from datetime import datetime

records_by_email = {}
with open('data.csv', newline='', encoding='utf-8') as source:
    for row in csv.DictReader(source):
        email = row['email']
        score_text = row['score']
        if not email or '@' not in email or not score_text:
            continue

        email = email.lower()
        signup = row['signup']
        if '/' in signup:
            signup = datetime.strptime(signup, '%d/%m/%Y').strftime('%Y-%m-%d')
        score = int(score_text)
        record = {'email': email, 'signup': signup, 'score': score}
        if email not in records_by_email or score > records_by_email[email]['score']:
            records_by_email[email] = record

output = sorted(records_by_email.values(), key=lambda record: record['email'])
with open('output.json', 'w', encoding='utf-8') as target:
    json.dump(output, target, separators=(',', ':'))
