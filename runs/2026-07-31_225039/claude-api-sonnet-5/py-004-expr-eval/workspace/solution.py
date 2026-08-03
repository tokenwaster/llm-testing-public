"""
solution.py

A hand-written recursive-descent arithmetic expression evaluator.

Supported grammar (informal):

    expr    := term (('+' | '-') term)*
    term    := unary (('*' | '/' | '%') unary)*
    unary   := ('-' | '+') unary | power
    power   := primary ('^' power)?      # right-associative
    primary := NUMBER | NAME | '(' expr ')'

Notes on precedence:
    - '^' binds tighter than unary minus, so "-2^2" == -(2^2) == -4
    - '^' is right associative, so "2^3^2" == 2^(3^2) == 512
    - unary minus can be applied repeatedly: "--3" == 3
    - '*','/','%' are left-associative and have equal precedence
    - '+','-' are left-associative and have equal precedence, lower than
      '*','/','%'
"""

from typing import Optional


def tokenize(s: str):
    """Convert the input string into a list of tokens.

    Each token is a tuple (kind, value) where kind is one of
    'NUMBER', 'NAME', 'OP', 'END'.
    """
    tokens = []
    i, n = 0, len(s)

    while i < n:
        c = s[i]

        if c.isspace():
            i += 1
            continue

        if c.isdigit() or c == '.':
            j = i
            dot_count = 0
            while j < n and (s[j].isdigit() or s[j] == '.'):
                if s[j] == '.':
                    dot_count += 1
                    if dot_count > 1:
                        raise ValueError("Invalid number literal (multiple dots)")
                j += 1
            num_str = s[i:j]

            if num_str == '.' :
                raise ValueError("Invalid number literal: '.'")
            if num_str.startswith('.') and not num_str[1:].isdigit():
                raise ValueError(f"Invalid number literal: {num_str!r}")
            if num_str.endswith('.') and not num_str[:-1].isdigit():
                raise ValueError(f"Invalid number literal: {num_str!r}")

            try:
                value = float(num_str)
            except ValueError:
                raise ValueError(f"Invalid number literal: {num_str!r}")

            tokens.append(('NUMBER', value))
            i = j

        elif c.isalpha() or c == '_':
            j = i
            while j < n and (s[j].isalnum() or s[j] == '_'):
                j += 1
            tokens.append(('NAME', s[i:j]))
            i = j

        elif c in '+-*/%^()':
            tokens.append(('OP', c))
            i += 1

        else:
            raise ValueError(f"Unexpected character {c!r} at position {i}")

    tokens.append(('END', None))
    return tokens


class _Parser:
    def __init__(self, tokens, variables: dict):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    # --- helpers -----------------------------------------------------
    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect_op(self, op: str):
        tok = self.peek()
        if tok[0] == 'OP' and tok[1] == op:
            self.advance()
            return
        raise ValueError(f"Expected '{op}' but found {tok}")

    # --- entry point ---------------------------------------------------
    def parse(self) -> float:
        result = self.expr()
        if self.peek()[0] != 'END':
            raise ValueError(f"Unexpected trailing tokens starting at {self.peek()}")
        return result

    # --- grammar rules -------------------------------------------------
    def expr(self) -> float:
        val = self.term()
        while True:
            tok = self.peek()
            if tok[0] == 'OP' and tok[1] in ('+', '-'):
                self.advance()
                rhs = self.term()
                if tok[1] == '+':
                    val = val + rhs
                else:
                    val = val - rhs
            else:
                break
        return val

    def term(self) -> float:
        val = self.unary()
        while True:
            tok = self.peek()
            if tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                self.advance()
                rhs = self.unary()
                if tok[1] == '*':
                    val = val * rhs
                elif tok[1] == '/':
                    if rhs == 0:
                        raise ValueError("Division by zero")
                    val = val / rhs
                else:  # '%'
                    if rhs == 0:
                        raise ValueError("Modulo by zero")
                    val = val % rhs
            else:
                break
        return val

    def unary(self) -> float:
        tok = self.peek()
        if tok[0] == 'OP' and tok[1] == '-':
            self.advance()
            return -self.unary()
        if tok[0] == 'OP' and tok[1] == '+':
            self.advance()
            return self.unary()
        return self.power()

    def power(self) -> float:
        val = self.primary()
        tok = self.peek()
        if tok[0] == 'OP' and tok[1] == '^':
            self.advance()
            rhs = self.power()  # right-associative recursion
            val = val ** rhs
        return val

    def primary(self) -> float:
        tok = self.peek()

        if tok[0] == 'NUMBER':
            self.advance()
            return float(tok[1])

        if tok[0] == 'NAME':
            self.advance()
            name = tok[1]
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name!r}")
            try:
                return float(self.variables[name])
            except (TypeError, ValueError):
                raise ValueError(f"Invalid value for variable {name!r}")

        if tok[0] == 'OP' and tok[1] == '(':
            self.advance()
            val = self.expr()
            self.expect_op(')')
            return val

        raise ValueError(f"Unexpected token: {tok}")


def evaluate(expr: str, variables: Optional[dict] = None) -> float:
    """
    Evaluate an arithmetic expression string and return a float result.

    Raises ValueError on malformed syntax, unbalanced parentheses,
    unknown variables, or division/modulo by zero.
    """
    if variables is None:
        variables = {}

    if not isinstance(expr, str):
        raise ValueError("Expression must be a string")

    tokens = tokenize(expr)
    parser = _Parser(tokens, variables)
    result = parser.parse()
    return float(result)
