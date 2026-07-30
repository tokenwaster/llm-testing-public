import csv
import json
import sys
from datetime import datetime

INPUT_CSV = 'data.csv'
OUTPUT_JSON = 'output.json'

def parse_date(date_str: str) -> str:
    """Convert date to YYYY-MM-DD. Accepts YYYY-MM-DD or DD/MM/YYYY."""
    date_str = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    # If format unknown, return original (should not happen per spec)
    return date_str

def main():
    records = {}
    with open(INPUT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()
            # Rule 1: drop invalid rows
            if not email or '@' not in email:
                continue
            if not score_str:
                continue
            # Normalize email
            email_norm = email.lower()
            # Normalize date
            signup_norm = parse_date(signup)
            # Parse score as int
            try:
                score = int(score_str)
            except ValueError:
                continue
            # Rule 4: deduplicate, keep highest score
            existing = records.get(email_norm)
            if existing is None or score > existing['score']:
                records[email_norm] = {
                    'email': email_norm,
                    'signup': signup_norm,
                    'score': score
                }
    # Rule 5: sort by email
    sorted_records = [records[email] for email in sorted(records)]
    # Write output JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as out_f:
        json.dump(sorted_records, out_f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
