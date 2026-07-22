# solution.py

import re
from typing import Dict, Optional, Tuple

Token = Tuple[str, str]  # (type, value)


def _tokenize(expr: str) -> list[Token]:
    token_specification = [
        ("NUMBER", r"\d+(?:\.\d*)?|\.\d+"),   # integer or decimal
        ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("OP", r"[\+\-\*/%\^]"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SKIP", r"[ \t\n\r]+"),
    ]
    tok_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specification)
    get_token = re.compile(tok_regex).match
    pos = 0
    tokens: list[Token] = []
    while pos < len(expr):
        m = get_token(expr, pos)
        if not m:
            raise ValueError(f"Unexpected character at position {pos}: '{expr[pos]}'")
        typ = m.lastgroup
        val = m.group(typ)
        if typ != "SKIP":
            tokens.append((typ, val))
        pos = m.end()
    return tokens


class Parser:
    def __init__(self, tokens: list[Token], variables: Optional[Dict[str, float]]):
        self.tokens = tokens
        self.variables = variables or {}
        self.pos = 0

    def _current(self) -> Token | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self, expected_type: str | None = None) -> Token:
        token = self._current()
        if token is None:
            raise ValueError("Unexpected end of input")
        if expected_type and token[0] != expected_type:
            raise ValueError(f"Expected {expected_type} but got {token}")
        self.pos += 1
        return token

    def parse(self) -> float:
        value = self.expr()
        if self._current() is not None:
            raise ValueError("Unexpected token after end of expression")
        return value

    # Grammar implementation
    def expr(self) -> float:
        left = self.term()
        while True:
            tok = self._current()
            if tok and tok[0] == "OP" and tok[1] in "+-":
                op = self._consume()[1]
                right = self.term()
                left = left + right if op == "+" else left - right
            else:
                break
        return left

    def term(self) -> float:
        left = self.factor()
        while True:
            tok = self._current()
            if tok and tok[0] == "OP" and tok[1] in "*/%":
                op = self._consume()[1]
                right = self.factor()
                if op == "*":
                    left *= right
                elif op == "/":
                    if right == 0:
                        raise ValueError("Division by zero")
                    left /= right
                else:  # "%"
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left %= right
            else:
                break
        return left

    def factor(self) -> float:
        return self.power()

    def power(self) -> float:
        base = self.unary()
        tok = self._current()
        if tok and tok[0] == "OP" and tok[1] == "^":
            self._consume()
            exponent = self.power()  # right-associative
            base = base ** exponent
        return base

    def unary(self) -> float:
        tok = self._current()
        if tok and tok[0] == "OP" and tok[1] == "-":
            self._consume()
            return -self.unary()
        else:
            return self.primary()

    def primary(self) -> float:
        tok = self._current()
        if not tok:
            raise ValueError("Unexpected end of input")
        typ, val = tok
        if typ == "NUMBER":
            self._consume()
            return float(val)
        elif typ == "IDENT":
            self._consume()
            if val not in self.variables:
                raise ValueError(f"Unknown variable: {val}")
            return float(self.variables[val])
        elif typ == "LPAREN":
            self._consume("LPAREN")
            value = self.expr()
            if self._current() and self._current()[0] == "RPAREN":
                self._consume("RPAREN")
                return value
            else:
                raise ValueError("Unbalanced parentheses: missing ')'")
        else:
            raise ValueError(f"Unexpected token: {tok}")


def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression with optional variable substitution.

    Parameters
    ----------
    expr : str
        The expression string.
    variables : dict[str, float] | None
        Mapping of variable names to numeric values.

    Returns
    -------
    float
        Result of the evaluation.

    Raises
    ------
    ValueError
        For syntax errors, unbalanced parentheses, unknown variables,
        or division/modulo by zero.
    """
    tokens = _tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
