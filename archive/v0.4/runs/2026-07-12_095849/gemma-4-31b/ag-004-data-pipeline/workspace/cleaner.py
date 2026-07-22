import csv
import json
from datetime import datetime

def clean_data():
    input_file = 'data.csv'
    output_file = 'output.json'
    
    rows = []
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()
            
            # Rule 1: Drop invalid rows
            if not email or '@' not in email or not score_str:
                continue
            
            try:
                score = int(score_str)
            except ValueError:
                continue # Treat non-integer scores as empty/invalid for this purpose

            # Rule 2: Normalize emails to lowercase
            email = email.lower()
            
            # Rule 3: Normalize dates
            if '-' in signup:
                # YYYY-MM-DD (keep as is)
                date_val = signup
            elif '/' in signup:
                # DD/MM/YYYY -> YYYY-MM-DD
                try:
                    dt = datetime.strptime(signup, '%d/%m/%Y')
                    date_val = dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue # Invalid date format
            else:
                continue # Unknown date format

            rows.append({
                'email': email,
                'signup': date_val,
                'score': score
            })

    # Rule 4: Deduplicate by email (keep highest score)
    unique_users = {}
    for row in rows:
        email = row['email']
        if email not in unique_users or row['score'] > unique_users[email]['score']:
            unique_users[email] = row

    # Rule 5: Sort by email ascending
    sorted_rows = sorted(unique_users.values(), key=lambda x: x['email'])

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_rows, f, indent=2)

if __name__ == "__main__":
    clean_data()
