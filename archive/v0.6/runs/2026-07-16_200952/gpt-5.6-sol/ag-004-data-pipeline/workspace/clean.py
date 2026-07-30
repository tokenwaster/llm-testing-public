import csv
import json
from datetime import datetime

best_by_email = {}

with open("data.csv", newline="", encoding="utf-8-sig") as source:
    for row in csv.DictReader(source):
        email = row["email"].strip()
        score_text = row["score"].strip()

        # Drop invalid rows before applying any normalization.
        if not email or "@" not in email or not score_text:
            continue

        email = email.lower()
        score = int(score_text)
        signup_text = row["signup"].strip()
        if "/" in signup_text:
            signup = datetime.strptime(signup_text, "%d/%m/%Y").strftime("%Y-%m-%d")
        else:
            signup = datetime.strptime(signup_text, "%Y-%m-%d").strftime("%Y-%m-%d")

        record = {"email": email, "signup": signup, "score": score}
        if email not in best_by_email or score > best_by_email[email]["score"]:
            best_by_email[email] = record

result = [best_by_email[email] for email in sorted(best_by_email)]
with open("output.json", "w", encoding="utf-8") as destination:
    json.dump(result, destination, indent=2)
    destination.write("\n")
