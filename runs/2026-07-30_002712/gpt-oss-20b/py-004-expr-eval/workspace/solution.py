# solution.py

import re
from typing import Dict, Optional, Tuple


class _Token:
    NUMBER = "NUMBER"
    IDENT = "IDENT"
    OP = "OP"
    LPAREN = "("
    RPAREN = ")"
    EOF = None

    def __init__(self, type_: str, value: Optional[str] = None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"_Token({self.type!r}, {self.value!r})"


class _Lexer:
    token_specification = [
        ("NUMBER", r"\d+(\.\d*)?|\.\d+"),
        ("IDENT",  r"[A-Za-z_][A-Za-z0-9_]*"),
        ("OP",     r"[\+\-\*/%\^]"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SKIP",   r"[ \t\n\r]+"),
    ]

    def __init__(self, text: str):
        self.text = text
        regex_parts = []
        for name, pattern in self.token_specification:
            regex_parts.append(f"(?P<{name}>{pattern})")
        self.regex = re.compile("|".join(regex_parts))
        self.pos = 0
        self.current_token = self._next_token()

    def _next_token(self) -> _Token:
        if self.pos >= len(self.text):
            return _Token(_Token.EOF)
        match = self.regex.match(self.text, self.pos)
        if not match:
            raise ValueError(f"Invalid character at position {self.pos}")
        kind = match.lastgroup
        value = match.group(kind)
        self.pos = match.end()
        if kind == "SKIP":
            return self._next_token()
        if kind == "NUMBER":
            return _Token(_Token.NUMBER, float(value))
        if kind == "IDENT":
            return _Token(_Token.IDENT, value)
        if kind == "OP":
            return _Token(_Token.OP, value)
        if kind == "LPAREN":
            return _Token(_Token.LPAREN, value)
        if kind == "RPAREN":
            return _Token(_Token.RPAREN, value)
        raise ValueError(f"Unknown token type: {kind}")

    def peek(self) -> _Token:
        return self.current_token

    def advance(self):
        self.current_token = self._next_token()


class Parser:
    def __init__(self, lexer: _Lexer, variables: Optional[Dict[str, float]]):
        self.lexer = lexer
        self.vars = variables or {}

    def parse(self) -> float:
        result = self.expr()
        if self.lexer.peek().type != _Token.EOF:
            raise ValueError("Unexpected token after expression")
        return result

    # expr: term ((+|-) term)*
    def expr(self) -> float:
        value = self.term()
        while True:
            tok = self.lexer.peek()
            if tok.type == _Token.OP and tok.value in ("+", "-"):
                op = tok.value
                self.lexer.advance()
                right = self.term()
                if op == "+":
                    value += right
                else:
                    value -= right
            else:
                break
        return value

    # term: factor ((*|/|%) factor)*
    def term(self) -> float:
        value = self.factor()
        while True:
            tok = self.lexer.peek()
            if tok.type == _Token.OP and tok.value in ("*", "/", "%"):
                op = tok.value
                self.lexer.advance()
                right = self.factor()
                if op == "*":
                    value *= right
                elif op == "/":
                    if right == 0:
                        raise ValueError("Division by zero")
                    value /= right
                else:  # "%"
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    value %= right
            else:
                break
        return value

    # factor: unary ( ^ factor )?
    def factor(self) -> float:
        left = self.unary()
        tok = self.lexer.peek()
        if tok.type == _Token.OP and tok.value == "^":
            self.lexer.advance()
            right = self.factor()  # right-associative
            left = left ** right
        return left

    # unary: (-) unary | primary
    def unary(self) -> float:
        count_neg = 0
        while True:
            tok = self.lexer.peek()
            if tok.type == _Token.OP and tok.value == "-":
                count_neg += 1
                self.lexer.advance()
            else:
                break
        value = self.primary()
        return -value if count_neg % 2 else value

    # primary: NUMBER | IDENT | '(' expr ')'
    def primary(self) -> float:
        tok = self.lexer.peek()
        if tok.type == _Token.NUMBER:
            val = tok.value
            self.lexer.advance()
            return val
        if tok.type == _Token.IDENT:
            name = tok.value
            if name not in self.vars:
                raise ValueError(f"Unknown variable: {name}")
            val = float(self.vars[name])
            self.lexer.advance()
            return val
        if tok.type == _Token.LPAREN:
            self.lexer.advance()
            val = self.expr()
            if self.lexer.peek().type != _Token.RPAREN:
                raise ValueError("Unbalanced parentheses")
            self.lexer.advance()
            return val
        raise ValueError(f"Unexpected token: {tok}")


def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression according to the specified grammar.

    Parameters
    ----------
    expr : str
        The expression string.
    variables : dict[str, float] | None, optional
        Mapping of variable names to numeric values. Variables not present in this
        mapping will raise a ValueError.

    Returns
    -------
    float
        Result of the evaluation.

    Raises
    ------
    ValueError
        If the expression is malformed, contains unknown variables,
        unbalanced parentheses, or division/modulo by zero.
    """
    lexer = _Lexer(expr)
    parser = Parser(lexer, variables)
    return parser.parse()
