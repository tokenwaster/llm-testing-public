Write a function `evaluate(expr: str, variables: dict[str, float] | None = None) -> float`
that evaluates arithmetic expressions **without using `eval`, `exec`, `ast`, or any
parsing library** — implement the parser yourself.

Supported grammar:
- Numbers: integers and decimals (`3`, `4.5`, `.5` is NOT required)
- Binary operators with standard precedence: `+  -  *  /  %  ^`
  where `^` is exponentiation and is **right-associative** (`2^3^2` = 512);
  all others are left-associative
- Unary minus, applicable repeatedly (`--3` = 3, `-2^2` = -4, i.e. unary minus
  binds looser than `^`)
- Parentheses, arbitrarily nested
- Variable names (`[a-zA-Z_][a-zA-Z0-9_]*`) resolved from the `variables` dict
- Whitespace anywhere between tokens

Errors — raise `ValueError` for: malformed syntax, unbalanced parentheses,
unknown variables, division (or modulo) by zero.

Return a `float` in all cases.
