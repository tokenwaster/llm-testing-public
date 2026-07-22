Write a function `parse(text: str)` that parses a JSON document and returns
the equivalent Python object (`dict` / `list` / `str` / `int` / `float` /
`True` / `False` / `None`), or returns `None` if the input is not valid JSON.

Requirements:
- Do NOT use the `json` module (or any other JSON library) — write the parser
  yourself.
- Support the full JSON grammar: nested objects and arrays, strings with the
  standard escapes (`\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`) and
  unicode escapes (`\u00e9` -> é), integers, negative numbers, fractions, and
  exponents (`-1.5e-3`), `true`, `false`, `null`, and arbitrary whitespace
  between tokens.
- Integers must come back as `int`, non-integers as `float`.
- Anything malformed returns `None`: trailing garbage after the document,
  unterminated strings or containers, missing commas or colons, bare words,
  leading zeros like `007`, single quotes, trailing commas.
- Note the ambiguity: valid JSON `null` also parses to Python `None`. That is
  acceptable — the tests distinguish via valid/invalid inputs, not that value.
