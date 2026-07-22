import csv
import json
from datetime import datetime

def is_valid_row(email, score):
    """Check if a row is valid based on email and score."""
    return email.strip() != '' and '@' in email and score.strip() != ''

def normalize_email(email):
    """Normalize email to lowercase."""
    return email.lower().strip()

def normalize_date(date_str):
    """Normalize date to YYYY-MM-DD format."""
    date_str = date_str.strip()
    
    # Try parsing as YYYY-MM-DD first
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    # Try parsing as DD/MM/YYYY
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}")

def clean_data(input_file, output_file):
    """Clean the data according to the specified rules."""
    records = []
    
    # Read CSV file
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email']
            signup = row['signup']
            score_str = row['score']
            
            # Rule 1: Drop invalid rows
            if not is_valid_row(email, score_str):
                continue
            
            try:
                # Normalize email (Rule 2)
                normalized_email = normalize_email(email)
                
                # Normalize date (Rule 3)
                normalized_date = normalize_date(signup)
                
                # Convert score to integer
                score = int(score_str.strip())
                
                records.append({
                    'email': normalized_email,
                    'signup': normalized_date,
                    'score': score
                })
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to error: {e}")
                continue
    
    # Rule 4: Deduplicate by email, keeping the highest score
    unique_records = {}
    for record in records:
        email = record['email']
        if email not in unique_records or record['score'] > unique_records[email]['score']:
            unique_records[email] = record
    
    # Convert back to list
    deduplicated_records = list(unique_records.values())
    
    # Rule 5: Sort by email, ascending
    sorted_records = sorted(deduplicated_records, key=lambda x: x['email'])
    
    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(sorted_records, f, indent=2)

if __name__ == '__main__':
    clean_data('data.csv', 'output.json')
    print("Data cleaning complete. Output written to output.json")
