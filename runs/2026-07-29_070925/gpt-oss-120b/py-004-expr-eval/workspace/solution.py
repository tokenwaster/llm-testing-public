# solution.py
import re
from typing import Dict, Optional

Token = tuple[str, Optional[str]]  # (type, value)


class Lexer:
    _token_spec = [
        ("NUMBER",   r"\d+(?:\.\d*)?"),          # 123, 123. , 123.45
        ("NUMBER",   r"\.\d+"),                  # .5 (optional, but accepted)
        ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"),
        ("OP",       r"[\+\-\*/%\^]"),
        ("LPAREN",   r"\("),
        ("RPAREN",   r"\)"),
        ("SKIP",     r"[ \t\r\n]+"),
        ("MISMATCH", r"."),                      # any other character
    ]
    _master_pat = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in _token_spec))

    def __init__(self, text: str):
        self.text = text
        self.tokens: list[Token] = []
        self.pos = 0
        self._tokenize()

    def _tokenize(self) -> None:
        for mo in self._master_pat.finditer(self.text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == "NUMBER":
                self.tokens.append(("NUMBER", value))
            elif kind == "ID":
                self.tokens.append(("ID", value))
            elif kind == "OP":
                self.tokens.append(("OP", value))
            elif kind == "LPAREN":
                self.tokens.append(("LPAREN", value))
            elif kind == "RPAREN":
                self.tokens.append(("RPAREN", value))
            elif kind == "SKIP":
                continue
            else:
                raise ValueError(f"Unexpected character {value!r}")
        self.tokens.append(("EOF", None))

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def next(self) -> Token:
        cur = self.tokens[self.pos]
        self.pos += 1
        return cur

    def expect(self, typ: str) -> str:
        token_type, value = self.next()
        if token_type != typ:
            raise ValueError(f"Expected {typ} but got {token_type}")
        return value  # type: ignore


class Parser:
    def __init__(self, lexer: Lexer, variables: Dict[str, float]):
        self.lexer = lexer
        self.vars = variables

    def parse(self) -> float:
        result = self.expr()
        if self.lexer.peek()[0] != "EOF":
            raise ValueError("Unexpected token after end of expression")
        return result

    # expr -> term (('+'|'-') term)*
    def expr(self) -> float:
        left = self.term()
        while True:
            token_type, value = self.lexer.peek()
            if token_type == "OP" and value in ("+", "-"):
                self.lexer.next()
                right = self.term()
                if value == "+":
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left

    # term -> power (('*'|'/'|'%') power)*
    def term(self) -> float:
        left = self.power()
        while True:
            token_type, value = self.lexer.peek()
            if token_type == "OP" and value in ("*", "/", "%"):
                self.lexer.next()
                right = self.power()
                if value == "*":
                    left = left * right
                elif value == "/":
                    if right == 0.0:
                        raise ValueError("Division by zero")
                    left = left / right
                else:  # %
                    if right == 0.0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            else:
                break
        return left

    # power -> unary ('^' power)?
    def power(self) -> float:
        left = self.unary()
        token_type, value = self.lexer.peek()
        if token_type == "OP" and value == "^":
            self.lexer.next()
            right = self.power()          # right‑associative
            left = left ** right
        return left

    # unary -> ('-')* primary
    def unary(self) -> float:
        minus_count = 0
        while True:
            token_type, value = self.lexer.peek()
            if token_type == "OP" and value == "-":
                self.lexer.next()
                minus_count += 1
            else:
                break
        value = self.primary()
        if minus_count % 2 == 1:
            value = -value
        return value

    # primary -> NUMBER | ID | '(' expr ')'
    def primary(self) -> float:
        token_type, value = self.lexer.peek()
        if token_type == "NUMBER":
            self.lexer.next()
            return float(value)
        elif token_type == "ID":
            self.lexer.next()
            if value not in self.vars:
                raise ValueError(f"Unknown variable {value!r}")
            return float(self.vars[value])
        elif token_type == "LPAREN":
            self.lexer.next()
            inner = self.expr()
            if self.lexer.peek()[0] != "RPAREN":
                raise ValueError("Unbalanced parentheses")
            self.lexer.next()  # consume ')'
            return inner
        else:
            raise ValueError(f"Unexpected token {token_type}")

def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluate an arithmetic expression with the given variables.

    Parameters
    ----------
    expr : str
        The expression to evaluate.
    variables : dict[str, float] | None, optional
        Mapping of variable names to numeric values. Missing variables raise
        ValueError.

    Returns
    -------
    float
        Result of evaluating the expression.

    Raises
    ------
    ValueError
        For syntax errors, unknown variables, unbalanced parentheses,
        division or modulo by zero.
    """
    if variables is None:
        variables = {}
    lexer = Lexer(expr)
    parser = Parser(lexer, variables)
    return parser.parse()
