"""Arithmetic expression evaluator built on a hand-written recursive-descent
parser (no eval / exec / ast / parsing libraries).

Grammar (lowest precedence first):

    expression := term (('+' | '-') term)*
    term       := unary (('*' | '/' | '%') unary)*
    unary      := '-' unary | power
    power      := primary ('^' unary)?          # right-associative
    primary    := NUMBER | NAME | '(' expression ')'

Unary minus therefore binds looser than '^' (so -2^2 == -4) while '^' itself
is right-associative (so 2^3^2 == 512).
"""

from __future__ import annotations

_DIGITS = frozenset("0123456789")
_NAME_START = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
_NAME_CHARS = _NAME_START | _DIGITS
_OPERATOR_CHARS = frozenset("+-*/%^()")


def _tokenize(expr: str) -> list[tuple[str, object]]:
    """Convert the input string into a list of (kind, value) tokens.

    Kinds: 'num' (float value), 'name' (identifier string), 'op' (operator
    or parenthesis character).  Whitespace separates tokens and is skipped.
    """
    tokens: list[tuple[str, object]] = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch in _DIGITS:
            j = i + 1
            while j < n and expr[j] in _DIGITS:
                j += 1
            # Optional fractional part: "4", "4.25", "4." are all numbers.
            if j < n and expr[j] == ".":
                j += 1
                while j < n and expr[j] in _DIGITS:
                    j += 1
            tokens.append(("num", float(expr[i:j])))
            i = j
        elif ch in _NAME_START:
            j = i + 1
            while j < n and expr[j] in _NAME_CHARS:
                j += 1
            tokens.append(("name", expr[i:j]))
            i = j
        elif ch in _OPERATOR_CHARS:
            tokens.append(("op", ch))
            i += 1
        else:
            raise ValueError(f"unexpected character {ch!r} at position {i}")
    return tokens


def _power(base: float, exponent: float) -> float:
    """Exponentiation that always yields a float or raises ValueError."""
    try:
        result = base ** exponent
    except ZeroDivisionError:
        raise ValueError("division by zero: zero raised to a negative power") from None
    except OverflowError:
        raise ValueError("numeric result out of range") from None
    if isinstance(result, complex):
        # e.g. (-8) ^ 0.5 -- not representable as a float.
        raise ValueError("negative number raised to a fractional power")
    return float(result)


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression and return the result as a float.

    Raises ValueError for malformed syntax, unbalanced parentheses, unknown
    variables, and division/modulo by zero.
    """
    if not isinstance(expr, str):
        raise ValueError("expression must be a string")

    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("empty expression")

    env = {} if variables is None else variables
    n_tokens = len(tokens)
    pos = 0

    def peek() -> tuple[str, object]:
        if pos < n_tokens:
            return tokens[pos]
        return ("end", None)

    def advance() -> tuple[str, object]:
        nonlocal pos
        token = tokens[pos]
        pos += 1
        return token

    # expression := term (('+' | '-') term)*
    def parse_expression() -> float:
        value = parse_term()
        while True:
            kind, op = peek()
            if kind == "op" and (op == "+" or op == "-"):
                advance()
                rhs = parse_term()
                value = value + rhs if op == "+" else value - rhs
            else:
                return value

    # term := unary (('*' | '/' | '%') unary)*
    def parse_term() -> float:
        value = parse_unary()
        while True:
            kind, op = peek()
            if kind == "op" and op in ("*", "/", "%"):
                advance()
                rhs = parse_unary()
                if op == "*":
                    value = value * rhs
                elif op == "/":
                    if rhs == 0:
                        raise ValueError("division by zero")
                    value = value / rhs
                else:  # '%'
                    if rhs == 0:
                        raise ValueError("modulo by zero")
                    value = value % rhs
            else:
                return value

    # unary := '-' unary | power   (unary minus binds looser than '^')
    def parse_unary() -> float:
        kind, op = peek()
        if kind == "op" and op == "-":
            advance()
            return -parse_unary()
        return parse_power()

    # power := primary ('^' unary)?   (right-associative)
    def parse_power() -> float:
        base = parse_primary()
        kind, op = peek()
        if kind == "op" and op == "^":
            advance()
            exponent = parse_unary()
            return _power(base, exponent)
        return base

    # primary := NUMBER | NAME | '(' expression ')'
    def parse_primary() -> float:
        nonlocal pos
        if pos >= n_tokens:
            raise ValueError("unexpected end of expression")
        kind, value = tokens[pos]
        if kind == "num":
            pos += 1
            return value
        if kind == "name":
            pos += 1
            if value not in env:
                raise ValueError(f"unknown variable: {value}")
            try:
                return float(env[value])
            except (TypeError, ValueError, OverflowError):
                raise ValueError(f"invalid value for variable {value!r}") from None
        if kind == "op" and value == "(":
            pos += 1
            inner = parse_expression()
            if pos >= n_tokens or tokens[pos] != ("op", ")"):
                raise ValueError("unbalanced parentheses: missing ')'")
            pos += 1
            return inner
        raise ValueError(f"unexpected token: {value!r}")

    result = parse_expression()
    if pos != n_tokens:
        raise ValueError(f"unexpected token: {tokens[pos][1]!r}")
    return float(result)
