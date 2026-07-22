"""Hand-written recursive-descent parser/evaluator for arithmetic expressions.

No eval/exec/ast or parsing libraries are used.
"""

from __future__ import annotations

import math


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression and return the result as a float."""
    if not isinstance(expr, str):
        raise ValueError("Expression must be a string")
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables if variables is not None else {})
    result = parser.parse_expression()
    if parser.peek()[0] != "EOF":
        raise ValueError("Malformed expression: unexpected trailing input")
    return float(result)


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def _is_digit(c: str) -> bool:
    return "0" <= c <= "9"


def _is_ident_start(c: str) -> bool:
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"


def _is_ident_part(c: str) -> bool:
    return _is_ident_start(c) or _is_digit(c)


def _tokenize(expr: str) -> list[tuple[str, object]]:
    tokens: list[tuple[str, object]] = []
    i, n = 0, len(expr)
    while i < n:
        c = expr[i]

        if c.isspace():
            i += 1
            continue

        # Number: digits with an optional fractional part.
        if _is_digit(c) or (c == "." and i + 1 < n and _is_digit(expr[i + 1])):
            j = i
            while j < n and _is_digit(expr[j]):
                j += 1
            if j < n and expr[j] == ".":
                j += 1
                while j < n and _is_digit(expr[j]):
                    j += 1
            tokens.append(("NUM", float(expr[i:j])))
            i = j
            continue

        # Identifier / variable name.
        if _is_ident_start(c):
            j = i + 1
            while j < n and _is_ident_part(expr[j]):
                j += 1
            tokens.append(("IDENT", expr[i:j]))
            i = j
            continue

        if c in "+-*/%^":
            tokens.append(("OP", c))
            i += 1
            continue

        if c == "(":
            tokens.append(("LPAREN", c))
            i += 1
            continue

        if c == ")":
            tokens.append(("RPAREN", c))
            i += 1
            continue

        raise ValueError(f"Invalid character in expression: {c!r}")

    tokens.append(("EOF", None))
    return tokens


# ---------------------------------------------------------------------------
# Recursive-descent parser
#
# Grammar (lowest to highest precedence):
#   expression := term   (("+" | "-") term)*
#   term       := unary  (("*" | "/" | "%") unary)*
#   unary      := ("-" | "+") unary | power
#   power      := primary ("^" unary)?        (right-associative)
#   primary    := NUMBER | IDENT | "(" expression ")"
#
# Because `unary` sits above `power`, unary minus binds looser than `^`,
# so -2^2 == -(2^2) == -4, while 2^-2 is still accepted.
# ---------------------------------------------------------------------------

class _Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    # expression := term (("+" | "-") term)*
    def parse_expression(self) -> float:
        value = self.parse_term()
        while self.peek()[0] == "OP" and self.peek()[1] in ("+", "-"):
            op = self.advance()[1]
            right = self.parse_term()
            value = value + right if op == "+" else value - right
        return value

    # term := unary (("*" | "/" | "%") unary)*
    def parse_term(self) -> float:
        value = self.parse_unary()
        while self.peek()[0] == "OP" and self.peek()[1] in ("*", "/", "%"):
            op = self.advance()[1]
            right = self.parse_unary()
            if op == "*":
                value = value * right
            elif op == "/":
                if right == 0:
                    raise ValueError("Division by zero")
                value = value / right
            else:  # "%"
                if right == 0:
                    raise ValueError("Modulo by zero")
                value = value % right
        return value

    # unary := ("-" | "+") unary | power
    def parse_unary(self) -> float:
        token = self.peek()
        if token == ("OP", "-"):
            self.advance()
            return -self.parse_unary()
        if token == ("OP", "+"):
            self.advance()
            return self.parse_unary()
        return self.parse_power()

    # power := primary ("^" unary)?   (right-associative)
    def parse_power(self) -> float:
        base = self.parse_primary()
        if self.peek() == ("OP", "^"):
            self.advance()
            exponent = self.parse_unary()
            # math.pow always returns a float and raises ValueError on
            # domain errors (e.g. negative base with fractional exponent).
            return math.pow(base, exponent)
        return base

    # primary := NUMBER | IDENT | "(" expression ")"
    def parse_primary(self) -> float:
        tok_type, tok_val = self.peek()

        if tok_type == "NUM":
            self.advance()
            return tok_val  # type: ignore[return-value]

        if tok_type == "IDENT":
            self.advance()
            if tok_val not in self.variables:
                raise ValueError(f"Unknown variable: {tok_val!r}")
            return float(self.variables[tok_val])

        if tok_type == "LPAREN":
            self.advance()
            value = self.parse_expression()
            if self.peek()[0] != "RPAREN":
                raise ValueError("Unbalanced parentheses: expected ')'")
            self.advance()
            return value

        if tok_type == "RPAREN":
            raise ValueError("Unbalanced parentheses: unexpected ')'")
        if tok_type == "EOF":
            raise ValueError("Malformed expression: unexpected end of input")
        raise ValueError(f"Malformed expression: unexpected token {tok_val!r}")
