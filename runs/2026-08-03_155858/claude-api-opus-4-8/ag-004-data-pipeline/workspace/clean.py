import csv, json

records = {}
with open("data.csv", newline="") as f:
    for row in csv.DictReader(f):
        email = (row["email"] or "").strip()
        signup = (row["signup"] or "").strip()
        score = (row["score"] or "").strip()

        # Rule 1: drop invalid
        if "@" not in email or email == "" or score == "":
            continue

        # Rule 2: normalize email
        email = email.lower()

        # Rule 3: normalize date
        if "/" in signup:
            d, m, y = signup.split("/")
            signup = f"{y}-{m}-{d}"

        score = int(score)

        # Rule 4: dedup by email, keep highest score
        if email not in records or score > records[email]["score"]:
            records[email] = {"email": email, "signup": signup, "score": score}

# Rule 5: sort by email
result = sorted(records.values(), key=lambda r: r["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
