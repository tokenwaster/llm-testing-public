#!/usr/bin/env python3
"""
Arithmetic expression evaluator without using eval/exec/ast or parsing libraries.
"""

import re
from typing import Dict, Optional

# Token types
NUMBER = 'NUMBER'
IDENT  = 'IDENT'
OP     = 'OP'
LPAREN = '('
RPAREN = ')'

OPERATORS = set('+-*/%^')

class _Token:
    def __init__(self, typ: str, val: str):
        self.typ = typ
        self.val = val

    def __repr__(self):
        return f"_Token({self.typ!r}, {self.val!r})"

def _tokenize(expr: str) -> list[_Token]:
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit() or (ch == '.' and i+1 < n and expr[i+1].isdigit()):
            # number: integer or decimal
            start = i
            has_dot = False
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.':
                    if has_dot:
                        raise ValueError(f"Invalid number format at position {i}")
                    has_dot = True
                i += 1
            tokens.append(_Token(NUMBER, expr[start:i]))
        elif ch.isalpha() or ch == '_':
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(_Token(IDENT, expr[start:i]))
        elif ch in OPERATORS:
            tokens.append(_Token(OP, ch))
            i += 1
        elif ch == '(':
            tokens.append(_Token(LPAREN, ch))
            i += 1
        elif ch == ')':
            tokens.append(_Token(RPAREN, ch))
            i += 1
        else:
            raise ValueError(f"Unknown character '{ch}' at position {i}")
    return tokens

class _Parser:
    def __init__(self, tokens: list[_Token], variables: Optional[Dict[str, float]]):
        self.tokens = tokens
        self.vars   = variables or {}
        self.pos    = 0
        self.len    = len(tokens)

    def current(self) -> Optional[_Token]:
        return self.tokens[self.pos] if self.pos < self.len else None

    def consume(self, typ: str = None, val: str = None) -> _Token:
        tok = self.current()
        if not tok or (typ and tok.typ != typ) or (val and tok.val != val):
            expected = f"{typ}" if typ else ""
            raise ValueError(f"Unexpected token {tok} at position {self.pos}")
        self.pos += 1
        return tok

    def parse(self) -> float:
        result = self.expr()
        if self.current() is not None:
            raise ValueError("Extra tokens after parsing complete")
        return result

    # Grammar implementation
    def expr(self) -> float:
        value = self.term()
        while True:
            tok = self.current()
            if tok and tok.typ == OP and tok.val in '+-':
                op = self.consume(OP).val
                rhs = self.term()
                if op == '+':
                    value += rhs
                else:
                    value -= rhs
            else:
                break
        return value

    def term(self) -> float:
        value = self.power()
        while True:
            tok = self.current()
            if tok and tok.typ == OP and tok.val in '*/%':
                op = self.consume(OP).val
                rhs = self.power()
                if op == '*':
                    value *= rhs
                elif op == '/':
                    if rhs == 0.0:
                        raise ValueError("Division by zero")
                    value /= rhs
                else:  # '%'
                    if rhs == 0.0:
                        raise ValueValueError("Modulo by zero")
                    value %= rhs
            else:
                break
        return value

    def power(self) -> float:
        base = self.unary()
        tok = self.current()
        if tok and tok.typ == OP and tok.val == '^':
            self.consume(OP)
            exponent = self.power()  # right-associative
            base = base ** exponent
        return base

    def unary(self) -> float:
        tok = self.current()
        if tok and tok.typ == OP and tok.val == '-':
            self.consume(OP)
            return -self.unary()
        else:
            return self.primary()

    def primary(self) -> float:
        tok = self.current()
        if not tok:
            raise ValueError("Unexpected end of input")
        if tok.typ == NUMBER:
            self.consume(NUMBER)
            return float(tok.val)
        elif tok.typ == IDENT:
            name = self.consume(IDENT).val
            if name not in self.vars:
                raise ValueError(f"Unknown variable '{name}'")
            return float(self.vars[name])
        elif tok.typ == LPAREN:
            self.consume(LPAREN)
            val = self.expr()
            if not self.current() or self.current().typ != RPAREN:
                raise ValueError("Unbalanced parentheses")
            self.consume(RPAREN)
            return val
        else:
            raise ValueError(f"Unexpected token {tok} at position {self.pos}")

def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression according to the specified grammar.
    Raises ValueError on syntax errors or runtime errors (division by zero,
    unknown variable, etc.).
    Returns a float result.
    """
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables)
    return parser.parse()
