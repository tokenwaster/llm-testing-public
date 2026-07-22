import csv, json

rows = {}
with open("data.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        email = (r.get("email") or "").strip()
        score = (r.get("score") or "").strip()
        if not email or "@" not in email or not score:
            continue
        email = email.lower()
        signup = (r.get("signup") or "").strip()
        if "/" in signup:
            d, m, y = signup.split("/")
            signup = f"{y}-{m}-{d}"
        score = int(score)
        if email not in rows or score > rows[email]["score"]:
            rows[email] = {"email": email, "signup": signup, "score": score}

out = sorted(rows.values(), key=lambda x: x["email"])
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
