#!/usr/bin/env python3
import csv
import json
from datetime import datetime
from pathlib import Path

def parse_date(date_str):
    """Parse date in YYYY-MM-DD or DD/MM/YYYY format, return YYYY-MM-DD."""
    if not date_str:
        return None

    date_str = date_str.strip()

    # Try YYYY-MM-DD first
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            pass

    # Try DD/MM/YYYY
    if len(date_str) == 10 and date_str[2] == '/' and date_str[5] == '/':
        try:
            dt = datetime.strptime(date_str, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    return None

def clean_data():
    input_file = Path(__file__).parent / 'data.csv'
    output_file = Path(__file__).parent / 'output.json'

    records = {}  # email -> (signup, score)

    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()

            # Rule 1: Drop invalid rows
            if not email or '@' not in email or not score_str:
                continue

            # Rule 2: Normalize email to lowercase
            email = email.lower()

            # Rule 3: Normalize dates
            signup_normalized = parse_date(signup)
            if not signup_normalized:
                continue

            try:
                score = int(score_str)
            except ValueError:
                continue

            # Rule 4: Deduplicate by email, keeping highest score
            if email not in records or score > records[email][1]:
                records[email] = (signup_normalized, score)

    # Rule 5: Sort by email ascending
    sorted_records = sorted(records.items())

    # Format as JSON array
    result = [
        {
            "email": email,
            "signup": signup,
            "score": score
        }
        for email, (signup, score) in sorted_records
    ]

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Cleaned {len(result)} records to {output_file}")
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    clean_data()
