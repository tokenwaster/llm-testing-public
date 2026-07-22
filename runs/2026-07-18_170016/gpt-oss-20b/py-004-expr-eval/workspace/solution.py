#!/usr/bin/env python3
"""
evaluate.py

A simple arithmetic expression evaluator that supports numbers, variables,
parentheses, and the operators + - * / % ^ with correct precedence.
"""

from __future__ import annotations
import sys
import math
from typing import Dict, List, Tuple, Union

Token = Tuple[str, Union[float, str]]  # ('NUMBER', value) | ('VAR', name) | ('OP', op)

def tokenize(expr: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit() or (ch == '.' and i + 1 < n and expr[i+1].isdigit()):
            # number: integer or decimal
            start = i
            has_dot = False
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.':
                    if has_dot:
                        raise ValueError(f"Invalid number format at position {i}")
                    has_dot = True
                i += 1
            num_str = expr[start:i]
            try:
                value = float(num_str)
            except ValueError:
                raise ValueError(f"Invalid number '{num_str}'")
            tokens.append(('NUMBER', value))
        elif ch.isalpha() or ch == '_':
            # variable name
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            var_name = expr[start:i]
            tokens.append(('VAR', var_name))
        elif ch in '+-*/%^()':
            tokens.append(('OP', ch))
            i += 1
        else:
            raise ValueError(f"Unknown character '{ch}' at position {i}")
    return tokens

class Parser:
    def __init__(self, tokens: List[Token], variables: Dict[str, float] | None):
        self.tokens = tokens
        self.variables = variables or {}
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else ('EOF', '')

    def consume(self) -> None:
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = ('EOF', '')

    def expect_op(self, op: str) -> bool:
        return self.current_token[0] == 'OP' and self.current_token[1] == op

    def parse(self) -> float:
        if not self.tokens:
            raise ValueError("Empty expression")
        value = self.parse_expr()
        if self.current_token[0] != 'EOF':
            raise ValueError(f"Unexpected token {self.current_token}")
        return float(value)

    # Grammar:
    # expr   : term ((+|-) term)*
    # term   : factor ((*|/|%) factor)*
    # factor : unary (^ power)?
    # power  : unary
    # unary  : ('-')* primary
    # primary: NUMBER | VAR | '(' expr ')'

    def parse_expr(self) -> float:
        value = self.parse_term()
        while self.expect_op('+') or self.expect_op('-'):
            op = self.current_token[1]
            self.consume()
            rhs = self.parse_term()
            if op == '+':
                value += rhs
            else:
                value -= rhs
        return value

    def parse_term(self) -> float:
        value = self.parse_factor()
        while self.expect_op('*') or self.expect_op('/') or self.expect_op('%'):
            op = self.current_token[1]
            self.consume()
            rhs = self.parse_factor()
            if op == '*':
                value *= rhs
            elif op == '/':
                if rhs == 0:
                    raise ValueError("division by zero")
                value /= rhs
            else:  # '%'
                if rhs == 0:
                    raise ValueError("modulo by zero")
                value %= rhs
        return value

    def parse_factor(self) -> float:
        value = self.parse_unary()
        if self.expect_op('^'):
            self.consume()
            exponent = self.parse_factor()  # right-associative
            value = math.pow(value, exponent)
        return value

    def parse_unary(self) -> float:
        neg_count = 0
        while self.expect_op('-'):
            neg_count += 1
            self.consume()
        value = self.parse_primary()
        if neg_count % 2 == 1:
            value = -value
        return value

    def parse_primary(self) -> float:
        token_type, token_value = self.current_token
        if token_type == 'NUMBER':
            self.consume()
            return token_value
        elif token_type == 'VAR':
            var_name = token_value
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable '{var_name}'")
            val = self.variables[var_name]
            self.consume()
            return float(val)
        elif self.expect_op('('):
            self.consume()
            value = self.parse_expr()
            if not self.expect_op(')'):
                raise ValueError("unbalanced parentheses")
            self.consume()
            return value
        else:
            raise ValueError(f"Unexpected token {self.current_token}")

def evaluate(expr: str, variables: Dict[str, float] | None = None) -> float:
    """
    Evaluate an arithmetic expression.

    Parameters
    ----------
    expr : str
        The expression string.
    variables : dict[str, float] or None
        Mapping of variable names to numeric values. If None, no variables are allowed.

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

# Example usage (uncomment to test):
if __name__ == "__main__":
    tests = [
        ("2+3*4", None),
        ("(1 + 2) * 3", None),
        ("-2^2", None),          # should be -4
        ("--3", None),           # should be 3
        ("a + b * c", {"a": 1, "b": 2, "c": 3}),
        ("2 ^ 3 ^ 2", None),     # 512
    ]
    for expr_str, vars_dict in tests:
        try:
            result = evaluate(expr_str, vars_dict)
            print(f"{expr_str} => {result}")
        except ValueError as e:
            print(f"Error evaluating '{expr_str}': {e}", file=sys.stderr)
