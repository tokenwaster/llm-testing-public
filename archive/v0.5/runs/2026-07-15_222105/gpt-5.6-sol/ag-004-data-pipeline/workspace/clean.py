import csv
import json
from datetime import datetime

best = {}
with open("data.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        email = row["email"]
        score_text = row["score"]
        if not email or "@" not in email or not score_text:
            continue

        email = email.lower()
        signup = row["signup"]
        if "/" in signup:
            signup = datetime.strptime(signup, "%d/%m/%Y").strftime("%Y-%m-%d")
        score = int(score_text)

        record = {"email": email, "signup": signup, "score": score}
        if email not in best or score > best[email]["score"]:
            best[email] = record

result = [best[email] for email in sorted(best)]
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
