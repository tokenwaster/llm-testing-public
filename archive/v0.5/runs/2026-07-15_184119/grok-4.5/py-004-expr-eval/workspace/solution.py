from typing import Any, List, Optional, Tuple


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables)
    result = parser.parse_expression()
    if parser.pos < len(tokens):
        raise ValueError("Malformed expression: unexpected tokens")
    return float(result)


def _tokenize(s: str) -> List[Tuple[str, Any]]:
    tokens: List[Tuple[str, Any]] = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit() or (c == "." and i + 1 < n and s[i + 1].isdigit()):
            j = i
            has_dot = False
            if c == ".":
                has_dot = True
                j += 1
            while j < n and s[j].isdigit():
                j += 1
            if j < n and s[j] == "." and not has_dot:
                has_dot = True
                j += 1
                while j < n and s[j].isdigit():
                    j += 1
            num_str = s[i:j]
            try:
                tokens.append(("NUM", float(num_str)))
            except ValueError:
                raise ValueError("Invalid number") from None
            i = j
            continue
        if c.isalpha() or c == "_":
            j = i + 1
            while j < n and (s[j].isalnum() or s[j] == "_"):
                j += 1
            tokens.append(("ID", s[i:j]))
            i = j
            continue
        if c in "+-*/%^()":
            tokens.append(("OP", c))
            i += 1
            continue
        raise ValueError(f"Invalid character: {c!r}")
    return tokens


class _Parser:
    def __init__(self, tokens: List[Tuple[str, Any]], variables: dict[str, float]):
        self.tokens = tokens
        self.variables = variables
        self.pos = 0

    def peek(self) -> Optional[Tuple[str, Any]]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self) -> Tuple[str, Any]:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, typ: str, val: Any = None) -> Tuple[str, Any]:
        tok = self.peek()
        if tok is None or tok[0] != typ or (val is not None and tok[1] != val):
            raise ValueError("Malformed expression")
        return self.consume()

    def parse_expression(self) -> float:
        if not self.tokens:
            raise ValueError("Empty expression")
        return self.parse_additive()

    def parse_additive(self) -> float:
        left = self.parse_multiplicative()
        while True:
            tok = self.peek()
            if tok is None or tok[0] != "OP" or tok[1] not in "+-":
                break
            op = self.consume()[1]
            right = self.parse_multiplicative()
            if op == "+":
                left = left + right
            else:
                left = left - right
        return left

    def parse_multiplicative(self) -> float:
        left = self.parse_unary()
        while True:
            tok = self.peek()
            if tok is None or tok[0] != "OP" or tok[1] not in "*/%":
                break
            op = self.consume()[1]
            right = self.parse_unary()
            if op == "*":
                left = left * right
            elif op == "/":
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_unary(self) -> float:
        tok = self.peek()
        if tok is not None and tok[0] == "OP" and tok[1] == "-":
            self.consume()
            return -self.parse_unary()
        return self.parse_power()

    def parse_power(self) -> float:
        left = self.parse_primary()
        tok = self.peek()
        if tok is not None and tok[0] == "OP" and tok[1] == "^":
            self.consume()
            right = self.parse_unary()
            try:
                return left ** right
            except ZeroDivisionError:
                raise ValueError("Division by zero") from None
        return left

    def parse_primary(self) -> float:
        tok = self.peek()
        if tok is None:
            raise ValueError("Malformed expression")
        if tok[0] == "NUM":
            self.consume()
            return float(tok[1])
        if tok[0] == "ID":
            self.consume()
            name = tok[1]
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        if tok[0] == "OP" and tok[1] == "(":
            self.consume()
            val = self.parse_additive()
            self.expect("OP", ")")
            return val
        raise ValueError("Malformed expression")
