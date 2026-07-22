import csv
import json
from datetime import datetime

def parse_date(date_str):
    """Parse date from either YYYY-MM-DD or DD/MM/YYYY format."""
    try:
        # Try YYYY-MM-DD first
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        # Try DD/MM/YYYY
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

def main():
    rows = []
    
    with open("data.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row["email"].strip()
            signup = row["signup"].strip()
            score_str = row["score"].strip()
            
            # Rule 1: Drop invalid rows
            if not email or "@" not in email or not score_str:
                continue
            
            # Rule 2: Normalize email to lowercase
            email = email.lower()
            
            # Rule 3: Normalize date
            signup = parse_date(signup)
            
            # Convert score to int
            score = int(score_str)
            
            rows.append({"email": email, "signup": signup, "score": score})
    
    # Rule 4: Deduplicate by email, keep highest score
    best_by_email = {}
    for row in rows:
        email = row["email"]
        if email not in best_by_email or row["score"] > best_by_email[email]["score"]:
            best_by_email[email] = row
    
    # Rule 5: Sort by email ascending
    result = sorted(best_by_email.values(), key=lambda x: x["email"])
    
    with open("output.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()