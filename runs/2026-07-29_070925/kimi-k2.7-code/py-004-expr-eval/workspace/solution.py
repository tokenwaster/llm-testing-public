import math


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression manually (no eval/exec/ast)."""

    var_map = variables if variables is not None else {}

    class Token:
        __slots__ = ("type", "value")

        def __init__(self, type_: str, value: str | float | None = None):
            self.type = type_
            self.value = value

        def __repr__(self) -> str:  # pragma: no cover
            return f"Token({self.type!r}, {self.value!r})"

    def tokenize(s: str) -> list[Token]:
        tokens: list[Token] = []
        i = 0
        n = len(s)
        while i < n:
            c = s[i]
            if c.isspace():
                i += 1
                continue

            if c.isdigit():
                start = i
                while i < n and s[i].isdigit():
                    i += 1
                if i < n and s[i] == ".":
                    i += 1
                    while i < n and s[i].isdigit():
                        i += 1
                num_str = s[start:i]
                try:
                    tokens.append(Token("NUM", float(num_str)))
                except ValueError:
                    raise ValueError(f"Invalid number: {num_str}")
                continue

            if c.isalpha() or c == "_":
                start = i
                while i < n and (s[i].isalnum() or s[i] == "_"):
                    i += 1
                tokens.append(Token("VAR", s[start:i]))
                continue

            if c in "+-*/%^":
                tokens.append(Token("OP", c))
                i += 1
                continue

            if c == "(":
                tokens.append(Token("LPAREN"))
                i += 1
                continue

            if c == ")":
                tokens.append(Token("RPAREN"))
                i += 1
                continue

            raise ValueError(f"Invalid character: {c}")

        tokens.append(Token("EOF"))
        return tokens

    class Parser:
        def __init__(self, tokens: list[Token], vars_: dict[str, float]):
            self.tokens = tokens
            self.pos = 0
            self.vars = vars_
            self.current = tokens[0]

        def advance(self) -> None:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current = self.tokens[self.pos]
            else:
                self.current = Token("EOF")

        def parse(self) -> float:
            value = self.expr()
            if self.current.type != "EOF":
                raise ValueError("Unexpected token after complete expression")
            return value

        def expr(self) -> float:
            return self.add()

        def add(self) -> float:
            value = self.mul()
            while self.current.type == "OP" and self.current.value in ("+", "-"):
                op = self.current.value
                self.advance()
                right = self.mul()
                if op == "+":
                    value += right
                else:
                    value -= right
            return value

        def mul(self) -> float:
            value = self.unary()
            while self.current.type == "OP" and self.current.value in ("*", "/", "%"):
                op = self.current.value
                self.advance()
                right = self.unary()
                if op == "*":
                    value *= right
                elif op == "/":
                    if right == 0.0:
                        raise ValueError("Division by zero")
                    value /= right
                else:  # '%'
                    if right == 0.0:
                        raise ValueError("Modulo by zero")
                    value %= right
            return value

        def unary(self) -> float:
            # Unary minus binds looser than '^'.
            if self.current.type == "OP" and self.current.value == "-":
                self.advance()
                return -self.unary()
            if self.current.type == "OP" and self.current.value == "+":
                self.advance()
                return self.unary()
            return self.power()

        def power(self) -> float:
            left = self.atom()
            if self.current.type == "OP" and self.current.value == "^":
                self.advance()
                right = self.unary()  # right-associative
                try:
                    return math.pow(left, right)
                except ValueError as exc:
                    raise ValueError("Math domain error") from exc
                except OverflowError as exc:
                    raise ValueError("Numeric overflow") from exc
            return left

        def atom(self) -> float:
            tok = self.current
            if tok.type == "NUM":
                self.advance()
                return float(tok.value)
            if tok.type == "VAR":
                self.advance()
                name = tok.value
                if name not in self.vars:
                    raise ValueError(f"Unknown variable: {name}")
                return float(self.vars[name])
            if tok.type == "LPAREN":
                self.advance()
                value = self.expr()
                if self.current.type != "RPAREN":
                    raise ValueError("Unbalanced parentheses")
                self.advance()
                return value
            raise ValueError("Unexpected token")

    tokens = tokenize(expr)
    parser = Parser(tokens, var_map)
    return parser.parse()
