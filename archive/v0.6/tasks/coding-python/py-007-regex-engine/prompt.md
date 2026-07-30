Write a function `match(pattern: str, text: str) -> bool` that reports whether
`pattern` matches the ENTIRE `text` (not a substring), supporting exactly this
regex subset:

- literal characters (match themselves)
- `.` — any single character
- `*` — zero or more of the preceding element
- `+` — one or more of the preceding element
- `?` — zero or one of the preceding element
- character classes `[abc]`, ranges `[a-z0-9]`, and negation `[^abc]`
  (`*`/`+`/`?` may follow a class)

Rules:
- Do not use the `re` module or any other regex library — build the matcher
  yourself (recursive backtracking is the expected approach).
- Malformed patterns (e.g. an unclosed `[`, or `*` with nothing before it)
  should raise `ValueError`.
- An empty pattern matches only the empty text.
