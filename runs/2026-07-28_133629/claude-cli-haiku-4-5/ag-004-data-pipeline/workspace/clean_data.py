#!/usr/bin/env python3
import csv
import json
from datetime import datetime

def parse_date(date_str):
    """Parse date in YYYY-MM-DD or DD/MM/YYYY format, return YYYY-MM-DD."""
    if not date_str:
        return None
    date_str = date_str.strip()

    # Try YYYY-MM-DD format
    if len(date_str) == 10 and date_str[4] == '-':
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            pass

    # Try DD/MM/YYYY format
    if len(date_str) == 10 and date_str[2] == '/' and date_str[5] == '/':
        try:
            dt = datetime.strptime(date_str, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    return None

def clean_data(csv_path, json_path):
    records = []

    # Read CSV
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score = row.get('score', '').strip()

            # Step 1: Drop invalid rows
            if not email or '@' not in email:
                continue
            if not score:
                continue

            # Step 2: Normalize email to lowercase
            email = email.lower()

            # Step 3: Normalize date
            signup = parse_date(signup)
            if not signup:
                continue

            # Convert score to int
            try:
                score = int(score)
            except ValueError:
                continue

            records.append({
                'email': email,
                'signup': signup,
                'score': score
            })

    # Step 4: Deduplicate by email, keep highest score
    email_map = {}
    for record in records:
        email = record['email']
        if email not in email_map or record['score'] > email_map[email]['score']:
            email_map[email] = record

    # Convert back to list
    records = list(email_map.values())

    # Step 5: Sort by email ascending
    records.sort(key=lambda x: x['email'])

    # Write JSON
    with open(json_path, 'w') as f:
        json.dump(records, f, indent=2)

    return records

if __name__ == '__main__':
    clean_data('data.csv', 'output.json')
    print("Data cleaned and written to output.json")
