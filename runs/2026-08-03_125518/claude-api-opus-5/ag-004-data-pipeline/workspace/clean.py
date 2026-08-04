import csv, json

def norm_date(s):
    s = s.strip()
    if "/" in s:
        d, m, y = s.split("/")
        return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    return s

best = {}
with open("data.csv", newline="") as f:
    for row in csv.DictReader(f):
        email = (row["email"] or "").strip()
        score = (row["score"] or "").strip()
        if not email or "@" not in email or not score:
            continue
        email = email.lower()
        rec = {"email": email, "signup": norm_date(row["signup"]), "score": int(score)}
        if email not in best or rec["score"] > best[email]["score"]:
            best[email] = rec

out = sorted(best.values(), key=lambda r: r["email"])
with open("output.json", "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
