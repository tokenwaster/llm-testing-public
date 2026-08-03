import csv
import json
from datetime import datetime

def parse_date(date_str):
    """Parse date in either YYYY-MM-DD or DD/MM/YYYY format"""
    if not date_str:
        return None
    
    # Try YYYY-MM-DD format first
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    # Try DD/MM/YYYY format
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    return None

def clean_data(input_file, output_file):
    rows = []
    
    # Read CSV file
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    cleaned_rows = []
    
    # Step 1: Drop invalid rows
    for row in rows:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score = row.get('score', '').strip()
        
        # Invalid if email is empty, has no @, or score is empty
        if not email or '@' not in email or not score:
            continue
        
        # Step 2: Normalize emails to lowercase
        email = email.lower()
        
        # Parse score as integer
        try:
            score_int = int(score)
        except ValueError:
            continue
        
        # Step 3: Normalize dates
        normalized_date = parse_date(signup)
        if not normalized_date:
            continue
        
        cleaned_rows.append({
            'email': email,
            'signup': normalized_date,
            'score': score_int
        })
    
    # Step 4: Deduplicate by email, keeping highest score
    email_dict = {}
    for row in cleaned_rows:
        email = row['email']
        if email not in email_dict or row['score'] > email_dict[email]['score']:
            email_dict[email] = row
    
    # Convert back to list
    deduplicated_rows = list(email_dict.values())
    
    # Step 5: Sort by email ascending
    deduplicated_rows.sort(key=lambda x: x['email'])
    
    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(deduplicated_rows, f, indent=2)

if __name__ == '__main__':
    clean_data('data.csv', 'output.json')
    print("Data cleaned successfully!")
