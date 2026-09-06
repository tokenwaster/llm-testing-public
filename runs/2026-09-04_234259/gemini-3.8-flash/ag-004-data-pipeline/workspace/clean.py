import csv
import json
import re
from datetime import datetime

def parse_date(date_str):
    date_str = date_str.strip()
    # Check if YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    # Check if DD/MM/YYYY
    if re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    raise ValueError(f"Unknown date format: {date_str}")

def clean_data(input_path, output_path):
    valid_rows = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            score_str = row.get('score', '').strip()
            signup_str = row.get('signup', '').strip()

            # Rule 1: Drop invalid rows:
            # "a row is invalid if its email contains no @, its email is empty, or its score is empty."
            if not email or '@' not in email or not score_str:
                continue

            try:
                score = int(score_str)
            except ValueError:
                continue

            # Rule 2: Normalize emails to lowercase
            email = email.lower()

            # Rule 3: Normalize dates
            signup = parse_date(signup_str)

            valid_rows.append({
                'email': email,
                'signup': signup,
                'score': score
            })

    # Rule 4: Deduplicate by email: keep only the row with the highest score
    best_by_email = {}
    for r in valid_rows:
        em = r['email']
        if em not in best_by_email or r['score'] > best_by_email[em]['score']:
            best_by_email[em] = r

    # Rule 5: Sort the remaining records by email, ascending
    sorted_records = sorted(best_by_email.values(), key=lambda x: x['email'])

    with open(output_path, mode='w', encoding='utf-8') as f:
        json.dump(sorted_records, f, indent=2)

if __name__ == '__main__':
    clean_data('data.csv', 'output.json')
    print("Done. Output:")
    with open('output.json', 'r', encoding='utf-8') as f:
        print(f.read())
