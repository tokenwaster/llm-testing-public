import csv
import json
import re

ISO_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
DMY_DATE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")


def normalize_date(value):
    value = value.strip()
    m = ISO_DATE.match(value)
    if m:
        return value
    m = DMY_DATE.match(value)
    if m:
        dd, mm, yyyy = m.groups()
        return f"{yyyy}-{mm}-{dd}"
    raise ValueError(f"Unrecognized date format: {value!r}")


def main():
    records = []
    with open("data.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = (row.get("email") or "").strip()
            signup = (row.get("signup") or "").strip()
            score = (row.get("score") or "").strip()

            # Rule 1: drop invalid rows
            if "@" not in email or email == "" or score == "":
                continue

            # Rule 2: normalize email to lowercase
            email = email.lower()

            # Rule 3: normalize dates to YYYY-MM-DD
            signup = normalize_date(signup)

            records.append({"email": email, "signup": signup, "score": int(score)})

    # Rule 4: deduplicate by email, keeping highest score
    best = {}
    for rec in records:
        cur = best.get(rec["email"])
        if cur is None or rec["score"] > cur["score"]:
            best[rec["email"]] = rec

    # Rule 5: sort by email ascending
    result = sorted(best.values(), key=lambda r: r["email"])

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
