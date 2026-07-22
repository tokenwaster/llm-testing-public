#!/usr/bin/env python3
"""
evaluate.py

A simple arithmetic expression evaluator that supports variables,
standard operators (+-*/%^) with correct precedence and associativity,
unary minus, and parentheses.
"""

import re
from typing import Dict, Optional, Tuple


# Token types
NUMBER = "NUMBER"
IDENT = "IDENT"
OP = "OP"
LPAREN = "("
RPAREN = ")"
EOF = "EOF"

# Regular expressions for tokenization
_token_specification = [
    ("NUMBER", r"\d+(\.\d*)?|\.\d+"),  # Integer or decimal number
    ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("OP", r"[\+\-\*/%\^]"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("SKIP", r"[ \t\n]+"),  # Skip whitespace
    ("MISMATCH", r"."),     # Any other character
]
_token_re = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in _token_specification))


class Token:
    def __init__(self, typ: str, value: Optional[str] = None):
        self.type = typ
        self.value = value

    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r})"


def _tokenize(expr: str):
    """Yield Token objects from the input expression."""
    for mo in _token_re.finditer(expr):
        kind = mo.lastgroup
        val = mo.group()
        if kind == "NUMBER":
            yield Token(NUMBER, float(val))
        elif kind == "IDENT":
            yield Token(IDENT, val)
        elif kind == "OP":
            yield Token(OP, val)
        elif kind == "LPAREN":
            yield Token(LPAREN, val)
        elif kind == "RPAREN":
            yield Token(RPAREN, val)
        elif kind == "SKIP":
            continue
        else:  # MISMATCH
            raise ValueError(f"Unexpected character {val!r}")
    yield Token(EOF)


class Parser:
    def __init__(self, tokens, variables: Optional[Dict[str, float]] = None):
        self.tokens = iter(tokens)
        self.current_token = next(self.tokens)
        self.variables = variables or {}

    def _eat(self, token_type: str):
        if self.current_token.type == token_type:
            self.current_token = next(self.tokens)
        else:
            raise ValueError(f"Expected {token_type} but got {self.current_token}")

    def parse(self) -> float:
        result = self.expr()
        if self.current_token.type != EOF:
            raise ValueError("Unexpected token after end of expression")
        return result

    # Grammar:
    # expr   : term ((+|-) term)*
    # term   : factor ((*|/|%) factor)*
    # factor : unary ( ^ factor )?
    # unary  : (-) unary | primary
    # primary: NUMBER | IDENT | '(' expr ')'

    def expr(self) -> float:
        result = self.term()
        while self.current_token.type == OP and self.current_token.value in ("+", "-"):
            op = self.current_token.value
            self._eat(OP)
            rhs = self.term()
            if op == "+":
                result += rhs
            else:
                result -= rhs
        return result

    def term(self) -> float:
        result = self.factor()
        while self.current_token.type == OP and self.current_token.value in ("*", "/", "%"):
            op = self.current_token.value
            self._eat(OP)
            rhs = self.factor()
            if op == "*":
                result *= rhs
            elif op == "/":
                if rhs == 0:
                    raise ValueError("Division by zero")
                result /= rhs
            else:  # "%"
                if rhs == 0:
                    raise ValueError("Modulo by zero")
                result %= rhs
        return result

    def factor(self) -> float:
        left = self.unary()
        if self.current_token.type == OP and self.current_token.value == "^":
            self._eat(OP)
            right = self.factor()  # Right-associative
            left = left ** right
        return left

    def unary(self) -> float:
        if self.current_token.type == OP and self.current_token.value == "-":
            self._eat(OP)
            return -self.unary()
        return self.primary()

    def primary(self) -> float:
        token = self.current_token
        if token.type == NUMBER:
            value = token.value
            self._eat(NUMBER)
            return float(value)
        elif token.type == IDENT:
            name = token.value
            self._eat(IDENT)
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        elif token.type == LPAREN:
            self._eat(LPAREN)
            value = self.expr()
            if self.current_token.type != RPAREN:
                raise ValueError("Unbalanced parentheses")
            self._eat(RPAREN)
            return value
        else:
            raise ValueError(f"Unexpected token: {token}")


def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression with optional variable substitution.

    Parameters
    ----------
    expr : str
        The expression to evaluate.
    variables : dict[str, float] | None
        Mapping of variable names to numeric values. If omitted or a variable is not found,
        a ValueError is raised.

    Returns
    -------
    float
        The result of the evaluation.

    Raises
    ------
    ValueError
        For malformed syntax, unbalanced parentheses, unknown variables,
        division or modulo by zero.
    """
    tokens = _tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
