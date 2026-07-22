Write a function `parse_csv(text: str) -> list[list[str]]` implementing an
RFC-4180-style CSV parser **from scratch** — the `csv` module (and any other
parsing library) is forbidden.

Rules:
- Fields are separated by commas; records by `\n` or `\r\n` (handle both).
- A field wrapped in double quotes may contain commas, newlines (`\n` or
  `\r\n`), and doubled double-quotes (`""` decodes to one `"`).
- Quotes only have special meaning if the field **starts** with a quote;
  `ab"cd` is the literal field `ab"cd`.
- An empty field decodes to `""`; the line `a,,b` has three fields.
- A trailing newline at the end of the input does not create an extra record,
  but an empty line in the middle is one record containing a single empty field.
- `parse_csv("")` returns `[]`.
- Malformed input — an opening quote that is never closed, or characters after
  a closing quote that aren't a comma/newline/EOF (e.g. `"ab"x`) — raises
  `ValueError`.
