import csv
import json
import re

def clean_data():
    input_file = 'data.csv'
    output_file = 'output.json'
    
    cleaned_records = {} # email -> {email, signup, score}
    
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()
            
            # Rule 1: Drop invalid rows
            # - email contains no '@'
            # - email is empty
            # - score is empty
            if not email or '@' not in email:
                continue
            if not score_str:
                continue
                
            # Rule 2: Normalize emails to lowercase
            email_normalized = email.lower()
            
            # Rule 3: Normalize dates
            # signup values are either YYYY-MM-DD or DD/MM/YYYY. Output format is always YYYY-MM-DD.
            if re.match(r'^\d{4}-\d{2}-\d{2}$', signup):
                signup_normalized = signup
            elif re.match(r'^\d{2}/\d{2}/\d{4}$', signup):
                parts = signup.split('/')
                signup_normalized = f"{parts[2]}-{parts[1]}-{parts[0]}"
            else:
                # If there's any other format, we can handle it or keep as is, but let's assume standard
                signup_normalized = signup
                
            # Convert score to integer
            try:
                score = int(score_str)
            except ValueError:
                continue # Skip if score is not a valid integer
                
            # Rule 4: Deduplicate by email
            # Keep only the row with the highest score
            if email_normalized in cleaned_records:
                if score > cleaned_records[email_normalized]['score']:
                    cleaned_records[email_normalized] = {
                        "email": email_normalized,
                        "signup": signup_normalized,
                        "score": score
                    }
            else:
                cleaned_records[email_normalized] = {
                    "email": email_normalized,
                    "signup": signup_normalized,
                    "score": score
                }
                
    # Rule 5: Sort the remaining records by email, ascending
    sorted_emails = sorted(cleaned_records.keys())
    output_data = [cleaned_records[email] for email in sorted_emails]
    
    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
        
    print("Cleaned data written to output.json:")
    print(json.dumps(output_data, indent=2))

if __name__ == '__main__':
    clean_data()
