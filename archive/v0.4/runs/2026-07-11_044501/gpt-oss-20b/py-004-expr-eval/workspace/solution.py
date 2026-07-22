#!/usr/bin/env python3
"""
evaluate.py

A small arithmetic expression evaluator that supports:
  * integers and decimal numbers
  * binary operators: + - * / % ^ (exponent, right associative)
  * unary minus (repeatedly)
  * parentheses
  * variables from a supplied dictionary

No eval/exec/ast or external parsing libraries are used.
"""

import re
from typing import Dict, Optional, Tuple


# --------------------------------------------------------------------------- #
# Tokenisation
# --------------------------------------------------------------------------- #

Token = Tuple[str, str]  # (type, value)

TOKEN_SPECIFICATION = [
    ("NUMBER",   r"\d+(?:\.\d*)?|\.\d+"),  # integer or decimal
    ("ID",       r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("OP",       r"[\+\-\*/%\^]"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    ("SKIP",     r"[ \t\n\r]+"),
    ("MISMATCH", r"."),  # any other character
]

TOKEN_REGEX = re.compile("|".join(f"(?P<{name}>{pattern})"
                                  for name, pattern in TOKEN_SPECIFICATION))


def tokenize(expr: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    while pos < len(expr):
        match = TOKEN_REGEX.match(expr, pos)
        if not match:
            raise ValueError(f"Unexpected character at position {pos}")
        kind = match.lastgroup
        value = match.group()
        if kind == "SKIP":
            pass
        elif kind == "MISMATCH":
            raise ValueError(f"Invalid token '{value}' at position {pos}")
        else:
            tokens.append((kind, value))
        pos = match.end()
    return tokens


# --------------------------------------------------------------------------- #
# Parser / Evaluator
# --------------------------------------------------------------------------- #

class Parser:
    def __init__(self, tokens: list[Token], variables: Optional[Dict[str, float]]):
        self.tokens = tokens
        self.variables = variables or {}
        self.pos = 0

    def current(self) -> Token | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type: str | None = None) -> Token:
        token = self.current()
        if token is None:
            raise ValueError("Unexpected end of input")
        if expected_type and token[0] != expected_type:
            raise ValueError(f"Expected {expected_type} but got {token}")
        self.pos += 1
        return token

    # Grammar:
    # expr   : term ((+|-) term)*
    # term   : factor ((*|/|%) factor)*
    # factor : power
    # power  : unary ('^' power)?
    # unary  : '-' unary | primary
    # primary: NUMBER | ID | '(' expr ')'

    def parse(self) -> float:
        value = self.parse_expr()
        if self.current() is not None:
            raise ValueError("Unexpected token after end of expression")
        return float(value)

    def parse_expr(self) -> float:
        left = self.parse_term()
        while True:
            tok = self.current()
            if tok and tok[0] == "OP" and tok[1] in "+-":
                op = self.consume()[1]
                right = self.parse_term()
                if op == "+":
                    left += right
                else:
                    left -= right
            else:
                break
        return left

    def parse_term(self) -> float:
        left = self.parse_factor()
        while True:
            tok = self.current()
            if tok and tok[0] == "OP" and tok[1] in "*/%":
                op = self.consume()[1]
                right = self.parse_factor()
                if op == "*":
                    left *= right
                elif op == "/":
                    if right == 0:
                        raise ValueError("Division by zero")
                    left /= right
                else:  # %
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left %= right
            else:
                break
        return left

    def parse_factor(self) -> float:
        return self.parse_power()

    def parse_power(self) -> float:
        left = self.parse_unary()
        tok = self.current()
        if tok and tok[0] == "OP" and tok[1] == "^":
            self.consume()  # consume '^'
            right = self.parse_power()  # right associative
            left = left ** right
        return left

    def parse_unary(self) -> float:
        tok = self.current()
        if tok and tok[0] == "OP" and tok[1] == "-":
            self.consume()
            return -self.parse_unary()
        else:
            return self.parse_primary()

    def parse_primary(self) -> float:
        tok = self.current()
        if not tok:
            raise ValueError("Unexpected end of input")
        kind, value = tok
        if kind == "NUMBER":
            self.consume()
            return float(value)
        elif kind == "ID":
            self.consume()
            if value not in self.variables:
                raise ValueError(f"Unknown variable '{value}'")
            return float(self.variables[value])
        elif kind == "LPAREN":
            self.consume()
            val = self.parse_expr()
            if self.current() and self.current()[0] == "RPAREN":
                self.consume()
                return val
            else:
                raise ValueError("Unbalanced parentheses: missing ')'")
        else:
            raise ValueError(f"Unexpected token {tok}")


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression.

    Parameters
    ----------
    expr : str
        The expression string.
    variables : dict[str, float] | None
        Mapping of variable names to numeric values. If a variable is not found,
        ValueError is raised.

    Returns
    -------
    float
        Result of the evaluation.

    Raises
    ------
    ValueError
        For malformed syntax, unbalanced parentheses, unknown variables,
        division or modulo by zero.
    """
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()


# --------------------------------------------------------------------------- #
# Example usage (uncomment to test)
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    tests = [
        ("2+3*4", None),
        ("(1 + 2) * 3", None),
        ("-2^2", None),          # should be -4
        ("--3", None),           # should be 3
        ("2^3^2", None),         # should be 512
        ("x + y*2", {"x": 1, "y": 5}),
    ]
    for expr, vars_ in tests:
        try:
            print(f"{expr} => {evaluate(expr, vars_)}")
        except ValueError as e:
            print(f"{expr} => Error: {e}")
