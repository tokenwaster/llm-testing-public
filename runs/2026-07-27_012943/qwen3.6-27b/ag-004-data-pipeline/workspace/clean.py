import csv
import json
import re

def convert_date(date_str):
    """Convert DD/MM/YYYY to YYYY-MM-DD if needed."""
    if not date_str:
        return None
    # Already YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    # Try DD/MM/YYYY
    m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', date_str)
    if m:
        day, month, year = m.groups()
        return f"{year}-{month}-{day}"
    return date_str

def main():
    rows = []
    with open('data.csv', 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score = row.get('score', '').strip()

            # Rule 1: Drop invalid rows
            if not email:
                continue
            if '@' not in email:
                continue
            if not score:
                continue

            # Rule 2: Normalize email to lowercase
            email = email.lower()

            # Rule 3: Normalize dates
            signup = convert_date(signup)

            rows.append({
                'email': email,
                'signup': signup,
                'score': int(score)
            })

    # Rule 4: Deduplicate by email, keep highest score
    best = {}
    for r in rows:
        email = r['email']
        if email not in best or r['score'] > best[email]['score']:
            best[email] = r

    # Rule 5: Sort by email ascending
    result = sorted(best.values(), key=lambda x: x['email'])

    with open('output.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Wrote {len(result)} records to output.json")

if __name__ == '__main__':
    main()
