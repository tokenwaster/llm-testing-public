#!/usr/bin/env python3
"""
A simple arithmetic expression evaluator without using eval/exec or parsing libraries.
"""

import re
from typing import Dict, Optional

# Token specification
_TOKEN_SPEC = [
    ('NUMBER',   r'\d+(?:\.\d*)?'),          # Integer or decimal number
    ('IDENT',    r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Variable names
    ('OP',       r'[\+\-\*/%\^]'),           # Operators
    ('LPAREN',   r'\('),                     # Left parenthesis
    ('RPAREN',   r'\)'),                     # Right parenthesis
    ('SKIP',     r'[ \t\n]+'),               # Skip over spaces and tabs
    ('MISMATCH', r'.'),                      # Any other character
]

_TOKEN_RE = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in _TOKEN_SPEC))

class Token:
    def __init__(self, type_: str, value: str):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f'Token({self.type!r}, {self.value!r})'

def tokenize(expr: str):
    """Yield tokens from the expression string."""
    for mo in _TOKEN_RE.finditer(expr):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise ValueError(f'Unexpected character {value!r}')
        else:
            yield Token(kind, value)

class Parser:
    def __init__(self, tokens, variables: Optional[Dict[str, float]] = None):
        self.tokens = list(tokens)
        self.pos = 0
        self.variables = variables or {}

    def current(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type: str = None) -> Token:
        token = self.current()
        if token is None:
            raise ValueError('Unexpected end of input')
        if expected_type and token.type != expected_type:
            raise ValueError(f'Expected {expected_type} but got {token.type}')
        self.pos += 1
        return token

    def parse(self) -> float:
        result = self.expr()
        if self.current() is not None:
            raise ValueError('Unexpected token after end of expression')
        return result

    # Grammar methods
    def expr(self) -> float:
        """expr : term ((+|-) term)*"""
        value = self.term()
        while True:
            tok = self.current()
            if tok and tok.type == 'OP' and tok.value in ('+', '-'):
                op = self.consume().value
                rhs = self.term()
                if op == '+':
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
            if tok and tok.type == 'OP' and tok.value in ('*', '/', '%'):
                op = self.consume().value
                rhs = self.power()
                if op == '*':
                    value *= rhs
                elif op == '/':
                    if rhs == 0.0:
                        raise ValueError('Division by zero')
                    value /= rhs
                else:  # '%'
                    if rhs == 0.0:
                        raise ValueError('Modulo by zero')
                    value %= rhs
            else:
                break
        return value

    def power(self) -> float:
        """power : unary ( ^ power )?"""
        value = self.unary()
        tok = self.current()
        if tok and tok.type == 'OP' and tok.value == '^':
            self.consume()  # consume '^'
            rhs = self.power()  # right-associative
            value = value ** rhs
        return value

    def unary(self) -> float:
        """unary : '-' unary | primary"""
        tok = self.current()
        if tok and tok.type == 'OP' and tok.value == '-':
            self.consume()
            return -self.unary()
        else:
            return self.primary()

    def primary(self) -> float:
        """primary : NUMBER | IDENT | '(' expr ')'"""
        tok = self.current()
        if not tok:
            raise ValueError('Unexpected end of input')
        if tok.type == 'NUMBER':
            self.consume()
            return float(tok.value)
        elif tok.type == 'IDENT':
            self.consume()
            if tok.value in self.variables:
                return float(self.variables[tok.value])
            else:
                raise ValueError(f'Unknown variable {tok.value!r}')
        elif tok.type == 'LPAREN':
            self.consume()  # '('
            value = self.expr()
            if self.current() and self.current().type == 'RPAREN':
                self.consume()  # ')'
                return value
            else:
                raise ValueError('Unbalanced parentheses')
        else:
            raise ValueError(f'Unexpected token {tok}')

def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression and return a float.

    Parameters
    ----------
    expr : str
        The expression to evaluate.
    variables : dict[str, float] | None
        Mapping of variable names to numeric values. If None, no variables are allowed.

    Returns
    -------
    float

    Raises
    ------
    ValueError
        For malformed syntax, unbalanced parentheses,
        unknown variables, division or modulo by zero.
    """
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
