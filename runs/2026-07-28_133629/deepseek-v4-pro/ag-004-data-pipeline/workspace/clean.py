import csv
import json
import re
from datetime import datetime

def clean():
    rows = []
    with open('data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip()
            score_str = row['score'].strip()
            signup = row['signup'].strip()

            # Rule 1: Drop invalid rows - email no @, email empty, score empty
            if not email or '@' not in email or not score_str:
                continue

            # Rule 2: Normalize email to lowercase
            email = email.lower()

            # Rule 3: Normalize dates
            # If DD/MM/YYYY, convert to YYYY-MM-DD. Else assume YYYY-MM-DD.
            if '/' in signup:
                dt = datetime.strptime(signup, '%d/%m/%Y')
                signup = dt.strftime('%Y-%m-%d')

            score = int(score_str)
            rows.append({'email': email, 'signup': signup, 'score': score})

    # Rule 4: Deduplicate by email, keep highest score
    best = {}
    for r in rows:
        e = r['email']
        if e not in best or r['score'] > best[e]['score']:
            best[e] = r

    # Rule 5: Sort by email ascending
    result = sorted(best.values(), key=lambda r: r['email'])

    with open('output.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("Done. Output:")
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    clean()