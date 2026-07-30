import csv
import json
from datetime import datetime

def clean_csv():
    valid_rows = []
    
    with open('data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip()
            signup = row['signup'].strip()
            score_str = row['score'].strip()
            
            # Rule 1: Drop invalid rows
            if not email or '@' not in email or not score_str:
                continue
            
            # Rule 2: Normalize email to lowercase
            email = email.lower()
            
            # Rule 3: Normalize date
            if '/' in signup:
                # DD/MM/YYYY format
                day, month, year = signup.split('/')
                signup = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            # else already YYYY-MM-DD
            
            score = int(score_str)
            
            valid_rows.append({
                'email': email,
                'signup': signup,
                'score': score
            })
    
    # Rule 4: Deduplicate by email, keep highest score
    email_to_row = {}
    for row in valid_rows:
        email = row['email']
        if email not in email_to_row or row['score'] > email_to_row[email]['score']:
            email_to_row[email] = row
    
    # Rule 5: Sort by email ascending
    sorted_rows = sorted(email_to_row.values(), key=lambda x: x['email'])
    
    # Write output
    with open('output.json', 'w') as f:
        json.dump(sorted_rows, f, indent=2)

if __name__ == '__main__':
    clean_csv()
    print("Done!")