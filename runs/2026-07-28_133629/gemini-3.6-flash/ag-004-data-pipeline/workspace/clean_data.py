import csv
import json
from datetime import datetime

def parse_date(date_str):
    date_str = date_str.strip()
    if '/' in date_str:
        # DD/MM/YYYY
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    else:
        # YYYY-MM-DD
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")

def clean_data(input_csv_path, output_json_path):
    valid_rows = []
    
    with open(input_csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip() if row['email'] else ''
            signup = row['signup'].strip() if row['signup'] else ''
            score_str = row['score'].strip() if row['score'] else ''
            
            # Step 1: Drop invalid rows
            # email contains no '@', email is empty, score is empty
            if not email or '@' not in email or not score_str:
                continue
            
            try:
                score = int(score_str)
            except ValueError:
                continue
                
            # Step 2: Normalize emails to lowercase
            email_norm = email.lower()
            
            # Step 3: Normalize dates
            date_norm = parse_date(signup)
            
            valid_rows.append({
                "email": email_norm,
                "signup": date_norm,
                "score": score
            })

    # Step 4: Deduplicate by email (keep row with highest score)
    best_by_email = {}
    for item in valid_rows:
        e = item["email"]
        if e not in best_by_email or item["score"] > best_by_email[e]["score"]:
            best_by_email[e] = item

    # Step 5: Sort remaining records by email ascending
    result = list(best_by_email.values())
    result.sort(key=lambda x: x["email"])

    with open(output_json_path, mode='w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    clean_data("data.csv", "output.json")
