import csv
import json
from datetime import datetime

def clean_data(input_file, output_file):
    records = []
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
            # Try YYYY-MM-DD first
            try:
                signup_dt = datetime.strptime(signup, '%Y-%m-%d')
            except ValueError:
                # Try DD/MM/YYYY
                try:
                    signup_dt = datetime.strptime(signup, '%d/%m/%Y')
                except ValueError:
                    continue # Should not happen based on rules but good for safety
            
            signup = signup_dt.strftime('%Y-%m-%d')

            records.append({
                'email': email,
                'signup': signup,
                'score': score
            })

    # 4. Deduplicate by email: keep highest score
    unique_records = {}
    for rec in records:
        email = rec['email']
        if email not in unique_records or rec['score'] > unique_records[email]['score']:
            unique_records[email] = rec

    # 5. Sort by email ascending
    sorted_records = sorted(unique_records.values(), key=lambda x: x['email'])

    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(sorted_records, f, indent=2)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
