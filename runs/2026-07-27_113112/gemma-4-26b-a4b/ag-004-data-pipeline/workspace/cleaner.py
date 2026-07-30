import csv
import json
from datetime import datetime

def clean_data(input_file, output_file):
    rows = []
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip()
            signup_raw = row['signup'].strip()
            score_str = row['score'].strip()

            # Rule 1: Drop invalid rows (no @, empty email, or empty score)
            if not email or '@' not in email or not score_str:
                continue
            
            try:
                score = int(score_str)
            except ValueError:
                continue

            # Rule 2: Normalize emails to lowercase
            email = email.lower()

            # Rule 3: Normalize dates (YYYY-MM-DD or DD/MM/YYYY)
            signup_date = None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    signup_date = datetime.strptime(signup_raw, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            
            if signup_date is None:
                continue

            rows.append({
                "email": email,
                "signup": signup_date,
                "score": score
            })

    # Rule 4: Deduplicate by email (keep highest score)
    email_map = {}
    for row in rows:
        e = row['email']
        if e not in email_map or row['score'] > email_map[e]['score']:
            email_map[e] = row

    # Rule 5: Sort the remaining records by email, ascending
    sorted_rows = sorted(list(email_map.values()), key=lambda x: x['email'])

    # Write to output.json
    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(sorted_rows, f, indent=4)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
