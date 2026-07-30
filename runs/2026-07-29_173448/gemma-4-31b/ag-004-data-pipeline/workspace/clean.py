import csv
import json
from datetime import datetime

def clean_data(input_file, output_file):
    rows = []
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email']
            signup = row['signup']
            score = row['score']

            # 1. Drop invalid rows
            if not email or '@' not in email or not score:
                continue
            
            try:
                score_int = int(score)
            except ValueError:
                continue # Or treat as empty/invalid

            # 2. Normalize emails to lowercase
            email = email.lower()

            # 3. Normalize dates
            if '/' in signup:
                # DD/MM/YYYY -> YYYY-MM-DD
                try:
                    date_obj = datetime.strptime(signup, '%d/%m/%Y')
                    signup = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    pass # Or handle error
            elif '-' in signup:
                # YYYY-MM-DD (already correct format)
                pass

            rows.append({
                'email': email,
                'signup': signup,
                'score': score_int
            })

    # 4. Deduplicate by email: keep only the row with the highest score
    unique_users = {}
    for row in rows:
        email = row['email']
        if email not in unique_users or row['score'] > unique_users[email]['score']:
            unique_users[email] = row

    # 5. Sort by email, ascending
    sorted_users = sorted(unique_users.values(), key=lambda x: x['email'])

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_users, f, indent=2)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
