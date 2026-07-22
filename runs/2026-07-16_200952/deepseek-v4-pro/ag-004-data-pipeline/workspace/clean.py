import csv
import json
import re
from datetime import datetime

def parse_date(s):
    """Parse date, return YYYY-MM-DD string."""
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return s  # already YYYY-MM-DD
    # DD/MM/YYYY
    dt = datetime.strptime(s, '%d/%m/%Y')
    return dt.strftime('%Y-%m-%d')

def main():
    with open('data.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    cleaned = []

    for row in rows:
        email = row.get('email', '').strip()
        score_str = row.get('score', '').strip()
        signup = row.get('signup', '').strip()

        # Rule 1: Drop invalid rows
        if not email or '@' not in email:
            continue
        if not score_str:
            continue

        # Rule 2: Normalize email to lowercase
        email = email.lower()

        # Rule 3: Normalize date
        signup = parse_date(signup)

        score = int(score_str)

        cleaned.append({'email': email, 'signup': signup, 'score': score})

    # Rule 4: Deduplicate by email, keep highest score
    best = {}
    for rec in cleaned:
        e = rec['email']
        if e not in best or rec['score'] > best[e]['score']:
            best[e] = rec

    # Rule 5: Sort by email ascending
    result = sorted(best.values(), key=lambda r: r['email'])

    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print("Done. Output records:")
    for r in result:
        print(r)

if __name__ == '__main__':
    main()