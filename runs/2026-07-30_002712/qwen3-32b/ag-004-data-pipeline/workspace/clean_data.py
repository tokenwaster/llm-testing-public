import csv
import json
from datetime import datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return datetime.strptime(date_str, "%d/%m/%Y")

valid_rows = []

with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        score_str = row.get('score', '').strip()
        signup_date_str = row.get('signup', '').strip()

        is_valid = True

        if not email or '@' not in email:
            is_valid = False

        if not score_str:
            is_valid = False

        try:
            score = int(score_str)
        except ValueError:
            is_valid = False

        if is_valid:
            normalized_email = email.lower()
            signup_date = parse_date(signup_date_str)
            normalized_date = signup_date.strftime("%Y-%m-%d")

            valid_rows.append({
                'email': normalized_email,
                'signup': normalized_date,
                'score': score
            })

# Deduplicate by email, keeping highest score per email
deduplicated = {}
for row in valid_rows:
    email = row['email']
    if email not in deduplicated or row['score'] > deduplicated[email]['score']:
        deduplicated[email] = {
            'email': email,
            'signup': row['signup'],
            'score': row['score']
        }

# Sort by email
sorted_list = sorted(deduplicated.values(), key=lambda x: x['email'])

# Write to output.json
with open('output.json', 'w') as f:
    json.dump(sorted_list, f)
