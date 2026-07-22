import csv, json

def norm_date(s):
    if "/" in s:
        d, m, y = s.split("/")
        return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    return s

best = {}
with open("data.csv", newline="") as f:
    for row in csv.DictReader(f):
        email = row["email"].strip()
        score = row["score"].strip()
        if "@" not in email or email == "" or score == "":
            continue
        email = email.lower()
        rec = {"email": email, "signup": norm_date(row["signup"].strip()), "score": int(score)}
        if email not in best or rec["score"] > best[email]["score"]:
            best[email] = rec

out = sorted(best.values(), key=lambda r: r["email"])
with open("output.json", "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
