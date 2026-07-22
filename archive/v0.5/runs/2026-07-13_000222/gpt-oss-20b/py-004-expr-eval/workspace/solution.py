#!/usr/bin/env python3
"""
evaluate(expr: str, variables: dict[str, float] | None = None) -> float

Evaluates arithmetic expressions without using eval/exec/ast or parsing libraries.
"""

import re
from typing import Dict, Optional, Tuple


# Token types
NUMBER = "NUMBER"
IDENT = "IDENT"
OP = "OP"
LPAREN = "("
RPAREN = ")"

Token = Tuple[str, str]  # (type, value)


def tokenize(expr: str) -> list[Token]:
    """Convert expression string into a list of tokens."""
    token_specification = [
        ("NUMBER", r"\d+(?:\.\d*)?|\.\d+"),  # integer or decimal
        ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("OP", r"[\+\-\*/%\^]"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SKIP", r"\s+"),
    ]
    tok_regex = "|".join(f"(?P<{name}>{pattern})"
                         for name, pattern in token_specification)
    get_token = re.compile(tok_regex).match
    pos = 0
    tokens: list[Token] = []
    while pos < len(expr):
        m = get_token(expr, pos)
        if not m:
            raise ValueError(f"Unexpected character at position {pos}: '{expr[pos]}'")
        typ = m.lastgroup
        if typ == "SKIP":
            pass
        else:
            val = m.group(typ)
            tokens.append((typ, val))
        pos = m.end()
    return tokens


class Parser:
    def __init__(self, tokens: list[Token], variables: Optional[Dict[str, float]]):
        self.tokens = tokens
        self.variables = variables or {}
        self.pos = 0

    def current(self) -> Token | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type: str | None = None,
                expected_value: str | None = None) -> Token:
        token = self.current()
        if not token:
            raise ValueError("Unexpected end of input")
        typ, val = token
        if expected_type and typ != expected_type:
            raise ValueError(f"Expected token type {expected_type} but got {typ}")
        if expected_value and val != expected_value:
            raise ValueError(f"Expected token value '{expected_value}' but got '{val}'")
        self.pos += 1
        return token

    # Grammar rules
    def parse(self) -> float:
        result = self.expr()
        if self.current() is not None:
            raise ValueError("Unexpected token after end of expression")
        return result

    def expr(self) -> float:
        """expr : term ((+|-) term)*"""
        value = self.term()
        while True:
            tok = self.current()
            if tok and tok[0] == "OP" and tok[1] in "+-":
                op = self.consume()[1]
                rhs = self.term()
                if op == "+":
                    value += rhs
                else:
                    value -= rhs
            else:
                break
        return value

    def term(self) -> float:
        """term : power ((*|/|%) power)*"""
        value = self.power()
        while True:
            tok = self.current()
            if tok and tok[0] == "OP" and tok[1] in "*/%":
                op = self.consume()[1]
                rhs = self.power()
                if op == "*":
                    value *= rhs
                elif op == "/":
                    if rhs == 0:
                        raise ValueError("Division by zero")
                    value /= rhs
                else:  # %
                    if rhs == 0:
                        raise ValueError("Modulo by zero")
                    value %= rhs
            else:
                break
        return value

    def power(self) -> float:
        """power : unary ('^' power)?"""
        left = self.unary()
        tok = self.current()
        if tok and tok[0] == "OP" and tok[1] == "^":
            self.consume()
            right = self.power()  # right-associative
            left = left ** right
        return left

    def unary(self) -> float:
        """unary : ('-')* primary"""
        neg_count = 0
        while True:
            tok = self.current()
            if tok and tok[0] == "OP" and tok[1] == "-":
                self.consume()
                neg_count += 1
            else:
                break
        value = self.primary()
        return -value if neg_count % 2 else value

    def primary(self) -> float:
        """primary : NUMBER | IDENT | '(' expr ')'"""
        tok = self.current()
        if not tok:
            raise ValueError("Unexpected end of input")
        typ, val = tok
        if typ == "NUMBER":
            self.consume()
            return float(val)
        elif typ == "IDENT":
            self.consume()
            if val in self.variables:
                return float(self.variables[val])
            else:
                raise ValueError(f"Unknown variable '{val}'")
        elif typ == LPAREN:
            self.consume(LPAREN)
            value = self.expr()
            if not self.current() or self.current()[0] != RPAREN:
                raise ValueError("Unbalanced parentheses")
            self.consume(RPAREN)
            return value
        else:
            raise ValueError(f"Unexpected token: {tok}")


def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression with optional variable substitution.

    Parameters
    ----------
    expr : str
        The expression to evaluate.
    variables : dict[str, float] | None
        Mapping of variable names to numeric values.

    Returns
    -------
    float
        Result of the evaluation.

    Raises
    ------
    ValueError
        If syntax is malformed, parentheses are unbalanced,
        a variable is unknown, or division/modulo by zero occurs.
    """
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
