import csv
import json
from datetime import datetime

def is_valid_row(email, signup, score):
    """Check if a row is valid"""
    if not email or '@' not in email:
        return False
    if not score:
        return False
    return True

def normalize_email(email):
    """Normalize email to lowercase"""
    return email.lower()

def normalize_date(date_str):
    """Normalize date to YYYY-MM-DD format"""
    # Try YYYY-MM-DD format
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

    return date_str

def clean_data(input_file, output_file):
    """Clean the CSV data and output to JSON"""
    data = []

    # Read and validate
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip()
            signup = row['signup'].strip()
            score = row['score'].strip()

            if not is_valid_row(email, signup, score):
                continue

            email = normalize_email(email)
            signup = normalize_date(signup)
            score = int(score)

            data.append({
                'email': email,
                'signup': signup,
                'score': score
            })

    # Deduplicate by email, keeping highest score
    email_dict = {}
    for record in data:
        email = record['email']
        if email not in email_dict or record['score'] > email_dict[email]['score']:
            email_dict[email] = record

    # Convert back to list and sort by email
    data = sorted(email_dict.values(), key=lambda x: x['email'])

    # Write to JSON
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    return data

if __name__ == '__main__':
    result = clean_data('data.csv', 'output.json')
    print(f"Cleaned {len(result)} records")
    for record in result:
        print(record)
