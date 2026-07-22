Write a Python module with two functions implementing run-length encoding:

- `encode(text: str) -> str` — compress runs of repeated characters into `<count><char>`.
  Example: `encode("aaabcc")` returns `"3a1b2c"`. Single characters still get a count of 1.
  `encode("")` returns `""`. Input contains only letters (a-z, A-Z); encoding is case-sensitive.
- `decode(encoded: str) -> str` — the exact inverse. Counts may be multi-digit
  (e.g. `"12a"` decodes to 12 copies of `"a"`). `decode("")` returns `""`.

For any valid input, `decode(encode(s)) == s` must hold.
