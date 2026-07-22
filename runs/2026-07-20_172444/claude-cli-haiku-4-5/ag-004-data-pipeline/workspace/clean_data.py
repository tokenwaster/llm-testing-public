import csv
import json
from datetime import datetime

def parse_date(date_str):
    """Convert date from DD/MM/YYYY or YYYY-MM-DD format to YYYY-MM-DD."""
    date_str = date_str.strip()
    if not date_str:
        return None

    try:
        if '/' in date_str:
            return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        return None

def is_valid_row(email, signup, score):
    """Check if row is valid."""
    email = email.strip()
    signup = signup.strip()
    score = score.strip()

    if not email or '@' not in email:
        return False
    if not signup:
        return False
    if not score:
        return False
    return True

rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row['email'].strip()
        signup = row['signup'].strip()
        score = row['score'].strip()

        if not is_valid_row(email, signup, score):
            continue

        normalized_email = email.lower()
        normalized_date = parse_date(signup)

        if normalized_date is None:
            continue

        try:
            score_int = int(score)
        except ValueError:
            continue

        rows.append({
            'email': normalized_email,
            'signup': normalized_date,
            'score': score_int
        })

deduped = {}
for row in rows:
    email = row['email']
    if email not in deduped or row['score'] > deduped[email]['score']:
        deduped[email] = row

result = sorted(deduped.values(), key=lambda x: x['email'])

with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"Processed {len(rows)} valid rows, deduplicated to {len(result)} unique emails")
print("\nOutput:")
for row in result:
    print(f"  {row['email']}: {row['signup']} ({row['score']})")
