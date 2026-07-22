# solution.py
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

class Token:
    __slots__ = ("type", "value")
    def __init__(self, typ: str, value: Any = None):
        self.type = typ   # e.g., "NUMBER", "IDENT", "OP", "LPAREN", "RPAREN", "EOF"
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type!r}, {self.value!r})"


def _tokenize(expr: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        # skip whitespace
        if ch.isspace():
            i += 1
            continue

        # number (int or float)
        if ch.isdigit() or (ch == '.' and i + 1 < n and expr[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.':
                    if has_dot:
                        break  # second dot ends number
                    has_dot = True
                i += 1
            num_str = expr[start:i]
            try:
                num_val = float(num_str)
            except ValueError:
                raise ValueError(f"Invalid number literal: {num_str}")
            tokens.append(Token("NUMBER", num_val))
            continue

        # identifier / variable
        if ch.isalpha() or ch == '_':
            start = i
            i += 1
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            ident = expr[start:i]
            tokens.append(Token("IDENT", ident))
            continue

        # operators and parentheses
        if ch in "+-*/%^()":
            if ch == '(':
                tokens.append(Token("LPAREN"))
            elif ch == ')':
                tokens.append(Token("RPAREN"))
            else:
                tokens.append(Token("OP", ch))
            i += 1
            continue

        raise ValueError(f"Unexpected character: {ch}")

    tokens.append(Token("EOF"))
    return tokens


class Parser:
    def __init__(self, tokens: List[Token], variables: Optional[Dict[str, float]]):
        self.tokens = tokens
        self.pos = 0
        self.vars = variables if variables is not None else {}

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        cur = self.tokens[self.pos]
        self.pos += 1
        return cur

    def expect(self, typ: str, value: Any = None) -> Token:
        tok = self.peek()
        if tok.type != typ or (value is not None and tok.value != value):
            raise ValueError(f"Expected token {typ} {value!r}, got {tok.type} {tok.value!r}")
        return self.advance()

    # Grammar entry point
    def parse(self) -> float:
        result = self.expr()
        if self.peek().type != "EOF":
            raise ValueError("Unexpected token after end of expression")
        return result

    # expr -> term ((+|-) term)*
    def expr(self) -> float:
        left = self.term()
        while True:
            tok = self.peek()
            if tok.type == "OP" and tok.value in ('+', '-'):
                op = self.advance().value
                right = self.term()
                if op == '+':
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left

    # term -> unary (( * | / | % ) unary)*
    def term(self) -> float:
        left = self.unary()
        while True:
            tok = self.peek()
            if tok.type == "OP" and tok.value in ('*', '/', '%'):
                op = self.advance().value
                right = self.unary()
                if op == '*':
                    left = left * right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    left = left / right
                else:  # '%'
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            else:
                break
        return left

    # unary -> '-' unary | power
    def unary(self) -> float:
        tok = self.peek()
        if tok.type == "OP" and tok.value == '-':
            self.advance()
            val = self.unary()
            return -val
        return self.power()

    # power -> primary ('^' power)?
    def power(self) -> float:
        left = self.primary()
        tok = self.peek()
        if tok.type == "OP" and tok.value == '^':
            self.advance()
            right = self.power()   # right-associative
            left = left ** right
        return left

    # primary -> NUMBER | IDENT | '(' expr ')'
    def primary(self) -> float:
        tok = self.peek()
        if tok.type == "NUMBER":
            self.advance()
            return float(tok.value)
        if tok.type == "IDENT":
            self.advance()
            name = tok.value
            if name not in self.vars:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.vars[name])
        if tok.type == "LPAREN":
            self.advance()
            val = self.expr()
            if self.peek().type != "RPAREN":
                raise ValueError("Unbalanced parentheses")
            self.advance()  # consume ')'
            return val
        raise ValueError(f"Unexpected token: {tok.type} {tok.value!r}")


def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression.

    Parameters
    ----------
    expr : str
        The expression to evaluate.
    variables : dict[str, float] | None, optional
        Mapping of variable names to their numeric values.

    Returns
    -------
    float
        The result of the evaluation.

    Raises
    ------
    ValueError
        If the expression is malformed, contains unknown variables,
        has unbalanced parentheses, or attempts division/modulo by zero.
    """
    tokens = _tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
