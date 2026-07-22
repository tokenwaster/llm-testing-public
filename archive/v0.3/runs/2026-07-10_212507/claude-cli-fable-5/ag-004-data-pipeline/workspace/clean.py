import csv, json, re

rows = []
with open("data.csv", newline="") as f:
    for r in csv.DictReader(f):
        email = (r["email"] or "").strip()
        score = (r["score"] or "").strip()
        if "@" not in email or not email or not score:
            continue
        email = email.lower()
        signup = r["signup"].strip()
        m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", signup)
        if m:
            signup = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        rows.append({"email": email, "signup": signup, "score": int(score)})

best = {}
for r in rows:
    if r["email"] not in best or r["score"] > best[r["email"]]["score"]:
        best[r["email"]] = r

out = sorted(best.values(), key=lambda r: r["email"])
with open("output.json", "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
