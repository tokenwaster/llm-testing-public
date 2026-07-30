import csv
import json
import re
from datetime import datetime

def parse_date(date_str):
    """Convert DD/MM/YYYY to YYYY-MM-DD format."""
    # Check if it's already in YYYY-MM-DD format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    # Convert DD/MM/YYYY to YYYY-MM-DD
    match = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', date_str)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"
    return None

def clean_data():
    # Read the CSV file
    rows = []
    with open('data.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    # Step 1: Drop invalid rows (email contains no @, email is empty, or score is empty)
    valid_rows = []
    for row in rows:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score = row.get('score', '').strip()
        
        # Check if email is empty
        if not email:
            continue
        
        # Check if email contains @
        if '@' not in email:
            continue
        
        # Check if score is empty
        if not score:
            continue
        
        valid_rows.append({
            'email': email,
            'signup': signup,
            'score': score
        })
    
    # Step 2: Normalize emails to lowercase
    for row in valid_rows:
        row['email'] = row['email'].lower()
    
    # Step 3: Normalize dates
    for row in valid_rows:
        parsed_date = parse_date(row['signup'])
        if parsed_date:
            row['signup'] = parsed_date
    
    # Step 4: Deduplicate by email - keep the row with highest score
    email_dict = {}
    for row in valid_rows:
        email = row['email']
        score = int(row['score'])
        
        if email not in email_dict:
            email_dict[email] = row
        else:
            # Compare scores and keep the higher one
            existing_score = int(email_dict[email]['score'])
            if score > existing_score:
                email_dict[email] = row
    
    # Step 5: Sort by email ascending
    sorted_rows = sorted(email_dict.values(), key=lambda x: x['email'])
    
    # Convert to output format with correct types
    output = []
    for row in sorted_rows:
        output.append({
            'email': row['email'],
            'signup': row['signup'],
            'score': int(row['score'])
        })
    
    return output

if __name__ == '__main__':
    result = clean_data()
    
    # Write to output.json
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print("Output written to output.json")
    print(json.dumps(result, indent=2))
