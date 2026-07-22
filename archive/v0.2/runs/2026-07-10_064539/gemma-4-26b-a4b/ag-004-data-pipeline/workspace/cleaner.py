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
            # YYYY-MM-DD or DD/MM/YYYY
            if '-' in signup:
                # Check if it's YYYY-MM-DD
                try:
                    datetime.strptime(signup, '%Y-%m-%d')
                    normalized_signup = signup
                except ValueError:
                    continue # Or handle other formats? The prompt says only these two.
            elif '/' in signup:
                # Check if it's DD/MM/YYYY
                try:
                    dt = datetime.strptime(signup, '%d/%m/%Y')
                    normalized_signup = dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            else:
                continue # Invalid date format

            rows.append({
                'email': email,
                'signup': normalized_signup,
                'score': score
            })

    # 4. Deduplicate by email (keep highest score)
    email_map = {}
    for row in rows:
        email = row['email']
        if email not in email_map or row['score'] > email_map[email]['score']:
            email_map[email] = row

    # 5. Sort by email ascending
    sorted_rows = sorted(email_map.values(), key=lambda x: x['email'])

    # Write to output.json
    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(sorted_rows, f, indent=4)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
