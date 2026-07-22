#!/usr/bin/env python3
"""
evaluate.py

A small expression evaluator that supports numbers, variables,
binary operators (+ - * / % ^), unary minus, and parentheses.
No eval/exec/ast or external parsing libraries are used.
"""

import re
from typing import Dict, Optional, Tuple, List


Token = Tuple[str, str]  # (type, value)


class Tokenizer:
    """
    Simple tokenizer for the supported grammar.
    Tokens: NUMBER, IDENT, OP, LPAREN, RPAREN, EOF
    """

    _token_specification = [
        ("NUMBER", r"\d+(?:\.\d*)?|\.\d+"),  # integer or decimal
        ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("OP", r"[\+\-\*/%\^]"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SKIP", r"[ \t\n\r]+"),
    ]

    _token_regex = re.compile("|".join(f"(?P<{name}>{pattern})"
                                       for name, pattern in _token_specification))

    def __init__(self, text: str):
        self.text = text
        self.tokens: List[Token] = []
        self._scan()

    def _scan(self) -> None:
        pos = 0
        while pos < len(self.text):
            match = self._token_regex.match(self.text, pos)
            if not match:
                raise ValueError(f"Unexpected character at position {pos}")
            kind = match.lastgroup
            value = match.group()
            if kind == "SKIP":
                pass
            else:
                self.tokens.append((kind, value))
            pos = match.end()
        self.tokens.append(("EOF", ""))

    def __iter__(self):
        return iter(self.tokens)


class Parser:
    """
    Recursive descent parser for the expression grammar.
    """

    def __init__(self, tokens: List[Token], variables: Optional[Dict[str, float]] = None):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables or {}

    def current(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected_type: str) -> Token:
        token = self.current()
        if token[0] != expected_type:
            raise ValueError(f"Expected {expected_type} but got {token}")
        self.pos += 1
        return token

    def parse(self) -> float:
        value = self.expr()
        if self.current()[0] != "EOF":
            raise ValueError("Unexpected token after end of expression")
        return value

    # Grammar rules
    # expr : addsub
    def expr(self) -> float:
        return self.add_sub()

    # add_sub : muldivmod ((+|-) muldivmod)*
    def add_sub(self) -> float:
        result = self.mul_div_mod()
        while True:
            tok_type, tok_val = self.current()
            if tok_type == "OP" and tok_val in ("+", "-"):
                self.consume("OP")
                rhs = self.mul_div_mod()
                if tok_val == "+":
                    result += rhs
                else:
                    result -= rhs
            else:
                break
        return result

    # mul_div_mod : power ((*|/|%) power)*
    def mul_div_mod(self) -> float:
        result = self.power()
        while True:
            tok_type, tok_val = self.current()
            if tok_type == "OP" and tok_val in ("*", "/", "%"):
                self.consume("OP")
                rhs = self.power()
                if tok_val == "*":
                    result *= rhs
                elif tok_val == "/":
                    if rhs == 0:
                        raise ValueError("Division by zero")
                    result /= rhs
                else:  # %
                    if rhs == 0:
                        raise ValueError("Modulo by zero")
                    result %= rhs
            else:
                break
        return result

    # power : unary ( ^ power )?
    def power(self) -> float:
        left = self.unary()
        tok_type, tok_val = self.current()
        if tok_type == "OP" and tok_val == "^":
            self.consume("OP")
            right = self.power()  # right-associative
            left = left ** right
        return left

    # unary : (-) unary | primary
    def unary(self) -> float:
        tok_type, tok_val = self.current()
        if tok_type == "OP" and tok_val == "-":
            self.consume("OP")
            return -self.unary()
        else:
            return self.primary()

    # primary : NUMBER | IDENT | '(' expr ')'
    def primary(self) -> float:
        tok_type, tok_val = self.current()
        if tok_type == "NUMBER":
            self.consume("NUMBER")
            return float(tok_val)
        elif tok_type == "IDENT":
            self.consume("IDENT")
            if tok_val not in self.variables:
                raise ValueError(f"Unknown variable '{tok_val}'")
            return float(self.variables[tok_val])
        elif tok_type == "LPAREN":
            self.consume("LPAREN")
            val = self.expr()
            if self.current()[0] != "RPAREN":
                raise ValueError("Unbalanced parentheses: missing ')'")
            self.consume("RPAREN")
            return val
        else:
            raise ValueError(f"Unexpected token {tok_val}")


def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression according to the specified grammar.

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
        Result of evaluating the expression.

    Raises
    ------
    ValueError
        For malformed syntax, unbalanced parentheses, unknown variables,
        division or modulo by zero.
    """
    tokenizer = Tokenizer(expr)
    parser = Parser(list(tokenizer), variables)
    return parser.parse()
