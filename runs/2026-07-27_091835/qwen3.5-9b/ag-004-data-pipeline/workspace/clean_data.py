import csv
import json
import re
from datetime import datetime

def parse_date(date_str):
    """Parse date string and return YYYY-MM-DD format."""
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        # Already YYYY-MM-DD
        return date_str
    elif re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
        # DD/MM/YYYY format
        day, month, year = date_str.split('/')
        return f"{year}-{month:02d}-{day:02d}"
    else:
        raise ValueError(f"Invalid date format: {date_str}")

def clean_data(input_file, output_file):
    valid_rows = []
    
    with open(input_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip() if row['email'] else ''
            signup = row['signup'].strip() if row['signup'] else ''
            score_str = row['score'].strip() if row['score'] else ''
            
            # Rule 1: Drop invalid rows
            # - email contains no @
            # - email is empty
            # - score is empty
            if '@' not in email:
                continue
            if email == '':
                continue
            if score_str == '':
                continue
            
            # Parse score as integer
            score = int(score_str)
            
            # Rule 3: Normalize dates
            signup = parse_date(signup)
            
            # Rule 2: Normalize emails to lowercase
            email_lower = email.lower()
            
            valid_rows.append({
                'email': email_lower,
                'signup': signup,
                'score': score
            })
    
    # Rule 4: Deduplicate by email (keep highest score)
    unique_rows = {}
    for row in valid_rows:
        email = row['email']
        if email not in unique_rows:
            unique_rows[email] = row
        else:
            # Keep the one with higher score
            if row['score'] > unique_rows[email]['score']:
                unique_rows[email] = row
    
    # Rule 5: Sort by email ascending
    sorted_rows = sorted(unique_rows.values(), key=lambda x: x['email'])
    
    # Write output JSON
    with open(output_file, 'w') as f:
        json.dump(sorted_rows, f, indent=2)

if __name__ == '__main__':
    clean_data('data.csv', 'output.json')
    print("Cleaning complete!")
