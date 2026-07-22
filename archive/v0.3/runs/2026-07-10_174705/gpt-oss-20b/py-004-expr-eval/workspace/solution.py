#!/usr/bin/env python3
"""
evaluate.py

A simple arithmetic expression evaluator that supports:
- integers and decimals
- binary operators + - * / % ^ (right associative)
- unary minus (multiple times)
- parentheses
- variables from a dictionary

No eval/exec/ast or external parsing libraries are used.
"""

from __future__ import annotations
import re
from typing import Dict, Optional, Tuple


class ParserError(ValueError):
    """Custom error for parser failures."""


def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression.

    Parameters
    ----------
    expr : str
        The expression to evaluate.
    variables : dict[str, float] | None
        Mapping of variable names to numeric values. If None,
        no variables are allowed.

    Returns
    -------
    float
        Result of the evaluation.

    Raises
    ------
    ValueError
        For malformed syntax, unbalanced parentheses,
        unknown variables, division or modulo by zero.
    """
    if variables is None:
        variables = {}

    # Tokenizer: we will parse directly from string using index pointer
    class Parser:
        def __init__(self, text: str):
            self.text = text
            self.pos = 0
            self.length = len(text)

        def _skip_ws(self) -> None:
            while self.pos < self.length and self.text[self.pos].isspace():
                self.pos += 1

        def _peek(self) -> Optional[str]:
            self._skip_ws()
            if self.pos >= self.length:
                return None
            return self.text[self.pos]

        def _consume(self, char: str) -> bool:
            self._skip_ws()
            if self.pos < self.length and self.text[self.pos] == char:
                self.pos += 1
                return True
            return False

        def parse_expr(self) -> float:
            value = self.parse_term()
            while True:
                op = self._peek()
                if op in ('+', '-'):
                    self.pos += 1
                    rhs = self.parse_term()
                    if op == '+':
                        value += rhs
                    else:
                        value -= rhs
                else:
                    break
            return float(value)

        def parse_term(self) -> float:
            value = self.parse_factor()
            while True:
                op = self._peek()
                if op in ('*', '/', '%'):
                    self.pos += 1
                    rhs = self.parse_factor()
                    if op == '*':
                        value *= rhs
                    elif op == '/':
                        if rhs == 0.0:
                            raise ParserError("division by zero")
                        value /= rhs
                    else:  # %
                        if rhs == 0.0:
                            raise ParserError("modulo by zero")
                        value %= rhs
                else:
                    break
            return float(value)

        def parse_factor(self) -> float:
            # Handle exponentiation (right associative)
            left = self.parse_unary()
            if self._peek() == '^':
                self.pos += 1
                right = self.parse_factor()  # recurse for right associativity
                left = left ** right
            return float(left)

        def parse_unary(self) -> float:
            neg_count = 0
            while self._peek() == '-':
                self.pos += 1
                neg_count += 1
            value = self.parse_primary()
            if neg_count % 2 == 1:
                value = -value
            return float(value)

        def parse_primary(self) -> float:
            token = self._peek()
            if token is None:
                raise ParserError("unexpected end of input")

            # Number
            if token.isdigit() or (token == '.' and self.pos + 1 < self.length and self.text[self.pos + 1].isdigit()):
                return self.parse_number()

            # Variable
            if token.isalpha() or token == '_':
                return self.parse_variable()

            # Parentheses
            if token == '(':
                self.pos += 1
                value = self.parse_expr()
                if not self._consume(')'):
                    raise ParserError("unbalanced parentheses")
                return float(value)

            raise ParserError(f"unexpected character '{token}'")

        def parse_number(self) -> float:
            start = self.pos
            has_dot = False
            while self.pos < self.length and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
                if self.text[self.pos] == '.':
                    if has_dot:
                        break  # second dot stops number
                    has_dot = True
                self.pos += 1
            num_str = self.text[start:self.pos]
            try:
                return float(num_str)
            except ValueError:
                raise ParserError(f"invalid number '{num_str}'")

        def parse_variable(self) -> float:
            start = self.pos
            while self.pos < self.length and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                self.pos += 1
            var_name = self.text[start:self.pos]
            if var_name not in variables:
                raise ParserError(f"unknown variable '{var_name}'")
            return float(variables[var_name])

    parser = Parser(expr)
    result = parser.parse_expr()
    # Ensure all input consumed
    if parser._peek() is not None:
        raise ParserError("unexpected trailing characters")
    return result


# Example usage (uncomment to test):
# if __name__ == "__main__":
#     print(evaluate("2^3^2"))  # 512.0
#     print(evaluate("-2^2"))   # -4.0
#     print(evaluate("--3 + 5 * (x-1)", {"x": 4}))  # 22.0
