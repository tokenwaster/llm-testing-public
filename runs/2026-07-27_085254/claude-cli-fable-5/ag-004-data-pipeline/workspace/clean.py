import csv, json

rows = {}
with open("data.csv", newline="") as f:
    for r in csv.DictReader(f):
        email = (r["email"] or "").strip()
        score = (r["score"] or "").strip()
        if "@" not in email or not score:
            continue
        email = email.lower()
        signup = r["signup"].strip()
        if "/" in signup:
            d, m, y = signup.split("/")
            signup = f"{y}-{m}-{d}"
        score = int(score)
        if email not in rows or score > rows[email]["score"]:
            rows[email] = {"email": email, "signup": signup, "score": score}

out = sorted(rows.values(), key=lambda r: r["email"])
with open("output.json", "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
