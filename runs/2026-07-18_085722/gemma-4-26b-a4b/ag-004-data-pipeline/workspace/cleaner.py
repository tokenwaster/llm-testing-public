import csv
import json
from datetime import datetime

def clean_data(input_file, output_file):
    rows = []
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip()
            signup = row['signup'].strip()
            score_str = row['score'].strip()

            # 1. Drop invalid rows
            if not email or '@' not in email or not score_str:
                continue
            
            try:
                score = int(score_str)
            except ValueError:
                continue

            # 2. Normalize emails to lowercase
            email = email.lower()

            # 3. Normalize dates
            # signup values are either YYYY-MM-DD or DD/MM/YYYY
            try:
                if '-' in signup:
                    # Check if it's YYYY-MM-DD
                    datetime.strptime(signup, '%Y-%m-%d')
                    normalized_date = signup
                elif '/' in signup:
                    # Convert DD/MM/YYYY to YYYY-MM-DD
                    dt = datetime.strptime(signup, '%d/%m/%Y')
                    normalized_date = dt.strftime('%Y-%m-%d')
                else:
                    # If it doesn't match either format, we might want to skip or handle it.
                    # The prompt says "are either YYYY-MM-DD ... or DD/MM/YYYY".
                    # Let's assume if it doesn't fit, it's invalid for our purposes.
                    continue
            except ValueError:
                continue

            rows.append({
                'email': email,
                'signup': normalized_date,
                'score': score
            })

    # 4. Deduplicate by email: keep the row with the highest score
    email_map = {}
    for row in rows:
        email = row['email']
        if email not in email_map or row['score'] > email_map[email]['score']:
            email_map[email] = row

    # 5. Sort the remaining records by email, ascending
    sorted_rows = sorted(email_map.values(), key=lambda x: x['email'])

    # Write to output.json
    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(sorted_rows, f, indent=4)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
