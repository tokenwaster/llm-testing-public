import csv
import json
from datetime import datetime
from pathlib import Path

def parse_date(date_str):
    """Parse date in YYYY-MM-DD or DD/MM/YYYY format."""
    if not date_str:
        return None

    # Try YYYY-MM-DD first
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        pass

    # Try DD/MM/YYYY
    try:
        return datetime.strptime(date_str.strip(), '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        pass

    return None

def clean_data():
    rows = []

    # Read CSV
    with open('data.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip() if row['email'] else ''
            signup = row['signup'].strip() if row['signup'] else ''
            score = row['score'].strip() if row['score'] else ''

            # Drop invalid rows
            if not email or '@' not in email or not score:
                continue

            # Normalize email to lowercase
            email = email.lower()

            # Normalize date
            signup = parse_date(signup)
            if not signup:
                continue

            # Parse score
            try:
                score = int(score)
            except ValueError:
                continue

            rows.append({
                'email': email,
                'signup': signup,
                'score': score
            })

    # Deduplicate by email - keep highest score
    email_map = {}
    for row in rows:
        email = row['email']
        if email not in email_map or row['score'] > email_map[email]['score']:
            email_map[email] = row

    # Sort by email ascending
    result = sorted(email_map.values(), key=lambda x: x['email'])

    # Write to JSON
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print(f"Cleaned data: {len(result)} records")
    for record in result:
        print(f"  {record['email']}: {record['signup']} (score: {record['score']})")

if __name__ == '__main__':
    clean_data()
