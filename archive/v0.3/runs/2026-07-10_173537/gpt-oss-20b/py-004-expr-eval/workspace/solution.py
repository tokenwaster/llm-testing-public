#!/usr/bin/env python3
"""
evaluate.py – simple arithmetic expression evaluator without eval/exec.
"""

import re
from typing import Dict, Optional, Tuple

Token = Tuple[str, str]  # (type, value)


class Lexer:
    """Simple lexer for the supported grammar."""

    token_specification = [
        ("NUMBER", r"\d+(?:\.\d*)?|\.\d+"),  # integer or decimal
        ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("OP", r"[\+\-\*/%\^]"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SKIP", r"[ \t\n]+"),
        ("MISMATCH", r"."),  # any other character
    ]

    def __init__(self, text: str):
        self.text = text
        self.regex = re.compile("|".join(f"(?P<{name}>{pattern})"
                                         for name, pattern in self.token_specification))
        self.tokens = self._tokenize()
        self.pos = 0

    def _tokenize(self):
        tokens = []
        for mo in self.regex.finditer(self.text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == "SKIP":
                continue
            elif kind == "MISMATCH":
                raise ValueError(f"Unexpected character: {value!r}")
            else:
                tokens.append((kind, value))
        return tokens

    def peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def next(self) -> Token:
        tok = self.peek()
        if not tok:
            raise ValueError("Unexpected end of input")
        self.pos += 1
        return tok


class Parser:
    """Recursive descent parser for the expression grammar."""

    def __init__(self, lexer: Lexer, variables: Optional[Dict[str, float]]):
        self.lexer = lexer
        self.vars = variables or {}

    def parse(self) -> float:
        result = self.expr()
        if self.lexer.peek() is not None:
            raise ValueError("Unexpected token after expression")
        return result

    # Grammar rules:

    def expr(self) -> float:
        """Parse addition and subtraction."""
        left = self.term()
        while True:
            tok = self.lexer.peek()
            if tok and tok[0] == "OP" and tok[1] in "+-":
                op = self.lexer.next()[1]
                right = self.term()
                left = left + right if op == "+" else left - right
            else:
                break
        return left

    def term(self) -> float:
        """Parse multiplication, division, modulo."""
        left = self.power()
        while True:
            tok = self.lexer.peek()
            if tok and tok[0] == "OP" and tok[1] in "*/%":
                op = self.lexer.next()[1]
                right = self.power()
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

    def power(self) -> float:
        """Parse exponentiation (right-associative)."""
        base = self.unary()
        tok = self.lexer.peek()
        if tok and tok[0] == "OP" and tok[1] == "^":
            self.lexer.next()  # consume '^'
            exp = self.power()  # right associative
            base = base ** exp
        return base

    def unary(self) -> float:
        """Parse unary minus."""
        tok = self.lexer.peek()
        if tok and tok[0] == "OP" and tok[1] == "-":
            self.lexer.next()
            return -self.unary()
        else:
            return self.primary()

    def primary(self) -> float:
        """Parse numbers, variables, parentheses."""
        tok = self.lexer.peek()
        if not tok:
            raise ValueError("Unexpected end of input")
        kind, value = tok
        if kind == "NUMBER":
            self.lexer.next()
            return float(value)
        elif kind == "IDENT":
            self.lexer.next()
            if value in self.vars:
                return float(self.vars[value])
            else:
                raise ValueError(f"Unknown variable: {value!r}")
        elif kind == "LPAREN":
            self.lexer.next()  # consume '('
            val = self.expr()
            if self.lexer.peek() and self.lexer.peek()[0] == "RPAREN":
                self.lexer.next()  # consume ')'
                return val
            else:
                raise ValueError("Unbalanced parentheses")
        else:
            raise ValueError(f"Unexpected token: {value!r}")


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
        For syntax errors, unknown variables, division by zero, etc.
    """
    lexer = Lexer(expr)
    parser = Parser(lexer, variables)
    return parser.parse()
