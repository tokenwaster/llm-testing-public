#!/usr/bin/env python3
"""
evaluate.py

A simple arithmetic expression evaluator that supports:
- integers and decimals
- binary operators + - * / % ^ (right-associative)
- unary minus (repeatedly)
- parentheses
- variables from a dictionary

No eval/exec/ast or external parsing libraries are used.
"""

import re
from typing import Dict, Optional

# Regular expressions for tokens
_NUMBER_RE = re.compile(r'\d+(?:\.\d*)?|\.\d+')
_VAR_RE = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')

class _Parser:
    def __init__(self, expr: str, variables: Optional[Dict[str, float]]):
        self.expr = expr
        self.variables = variables or {}
        self.pos = 0
        self.length = len(expr)

    # ---------- Utility ----------
    def _skip_whitespace(self):
        while self.pos < self.length and self.expr[self.pos].isspace():
            self.pos += 1

    def _match(self, pattern: re.Pattern) -> Optional[re.Match]:
        self._skip_whitespace()
        m = pattern.match(self.expr, self.pos)
        if m:
            self.pos = m.end()
        return m

    # ---------- Parsing ----------
    def parse(self) -> float:
        value = self._parse_expr()
        self._skip_whitespace()
        if self.pos != self.length:
            raise ValueError(f"Unexpected token at position {self.pos}")
        return float(value)

    # expr := term ((+|-) term)*
    def _parse_expr(self):
        left = self._parse_term()
        while True:
            self._skip_whitespace()
            if self.expr.startswith('+', self.pos):
                self.pos += 1
                right = self._parse_term()
                left = left + right
            elif self.expr.startswith('-', self.pos):
                self.pos += 1
                right = self._parse_term()
                left = left - right
            else:
                break
        return left

    # term := factor ((*|/|%) factor)*
    def _parse_term(self):
        left = self._parse_factor()
        while True:
            self._skip_whitespace()
            if self.expr.startswith('*', self.pos):
                self.pos += 1
                right = self._parse_factor()
                left = left * right
            elif self.expr.startswith('/', self.pos):
                self.pos += 1
                right = self._parse_factor()
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            elif self.expr.startswith('%', self.pos):
                self.pos += 1
                right = self._parse_factor()
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
            else:
                break
        return left

    # factor := unary ('^' factor)?
    def _parse_factor(self):
        left = self._parse_unary()
        self._skip_whitespace()
        if self.expr.startswith('^', self.pos):
            self.pos += 1
            right = self._parse_factor()   # right-associative
            left = left ** right
        return left

    # unary := ('-')* primary
    def _parse_unary(self):
        self._skip_whitespace()
        neg_count = 0
        while self.expr.startswith('-', self.pos):
            self.pos += 1
            neg_count += 1
            self._skip_whitespace()
        value = self._parse_primary()
        if neg_count % 2 == 1:
            return -value
        return value

    # primary := number | variable | '(' expr ')'
    def _parse_primary(self):
        self._skip_whitespace()
        if self.pos >= self.length:
            raise ValueError("Unexpected end of expression")

        ch = self.expr[self.pos]

        # Parentheses
        if ch == '(':
            self.pos += 1
            value = self._parse_expr()
            self._skip_whitespace()
            if self.pos >= self.length or self.expr[self.pos] != ')':
                raise ValueError("Unbalanced parentheses")
            self.pos += 1
            return value

        # Number
        m_num = _NUMBER_RE.match(self.expr, self.pos)
        if m_num:
            self.pos = m_num.end()
            return float(m_num.group())

        # Variable
        m_var = _VAR_RE.match(self.expr, self.pos)
        if m_var:
            name = m_var.group()
            self.pos = m_var.end()
            if name not in self.variables:
                raise ValueError(f"Unknown variable '{name}'")
            return float(self.variables[name])

        raise ValueError(f"Unexpected character '{ch}' at position {self.pos}")

def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression.

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
        If syntax is malformed, parentheses are unbalanced,
        a variable is unknown, or division/modulo by zero occurs.
    """
    parser = _Parser(expr, variables)
    return parser.parse()
