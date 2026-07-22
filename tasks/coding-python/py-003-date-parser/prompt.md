Write a function `normalize_date(text: str) -> str | None` that converts a date
string in any of these four formats to ISO `YYYY-MM-DD`:

1. `"2024-03-05"` — already ISO (validate it, still return it)
2. `"05/03/2024"` — day/month/year with slashes, zero-padded or not (`5/3/2024` is valid)
3. `"March 5, 2024"` — full English month name, day, comma, 4-digit year
4. `"5 Mar 2024"` — day, 3-letter English month abbreviation, 4-digit year

Rules:
- Surrounding whitespace must be tolerated.
- Month names/abbreviations are case-insensitive.
- Return `None` for anything that doesn't match one of the four formats or isn't a
  real calendar date (e.g. `"31/02/2024"` → `None`).
- Do not use any third-party libraries (stdlib only; `datetime` is allowed).
