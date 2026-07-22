"""Hand-written arithmetic expression evaluator (no eval/exec/ast)."""


def _tokenize(expr: str):
    """Convert the input string into a list of tokens."""
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            if j < n and expr[j] == ".":
                j += 1
                if j >= n or not expr[j].isdigit():
                    raise ValueError("malformed number")
                while j < n and expr[j].isdigit():
                    j += 1
            tokens.append(("num", float(expr[i:j])))
            i = j
        elif c == ".":
            raise ValueError("malformed number")
        elif c.isalpha() or c == "_":
            j = i + 1
            while j < n and (expr[j].isalnum() or expr[j] == "_"):
                j += 1
            tokens.append(("name", expr[i:j]))
            i = j
        elif c in "+-*/%^":
            tokens.append(("op", c))
            i += 1
        elif c == "(":
            tokens.append(("lparen", c))
            i += 1
        elif c == ")":
            tokens.append(("rparen", c))
            i += 1
        else:
            raise ValueError(f"unexpected character: {c!r}")
    return tokens


class _Parser:
    """Recursive-descent parser for the expression grammar.

    Grammar (precedence from lowest to highest):
        expr   := term  (('+' | '-') term)*
        term   := unary (('*' | '/' | '%') unary)*
        unary  := ('-' | '+') unary | power      (unary binds looser than ^)
        power  := atom ('^' unary)?              (right-associative)
        atom   := number | name | '(' expr ')'
    """

    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse_expr(self):
        value = self.parse_term()
        while True:
            tok = self.peek()
            if tok is not None and tok[0] == "op" and tok[1] in "+-":
                self.advance()
                rhs = self.parse_term()
                value = value + rhs if tok[1] == "+" else value - rhs
            else:
                return value

    def parse_term(self):
        value = self.parse_unary()
        while True:
            tok = self.peek()
            if tok is not None and tok[0] == "op" and tok[1] in "*/%":
                self.advance()
                rhs = self.parse_unary()
                if tok[1] == "*":
                    value = value * rhs
                elif tok[1] == "/":
                    if rhs == 0:
                        raise ValueError("division by zero")
                    value = value / rhs
                else:
                    if rhs == 0:
                        raise ValueError("modulo by zero")
                    value = value % rhs
            else:
                return value

    def parse_unary(self):
        tok = self.peek()
        if tok is not None and tok[0] == "op" and tok[1] == "-":
            self.advance()
            return -self.parse_unary()
        if tok is not None and tok[0] == "op" and tok[1] == "+":
            self.advance()
            return self.parse_unary()
        return self.parse_power()

    def parse_power(self):
        base = self.parse_atom()
        tok = self.peek()
        if tok is not None and tok[0] == "op" and tok[1] == "^":
            self.advance()
            exponent = self.parse_unary()
            try:
                result = base ** exponent
            except ZeroDivisionError:
                raise ValueError(
                    "zero cannot be raised to a negative power"
                ) from None
            if isinstance(result, complex):
                raise ValueError("expression result is not a real number")
            return result
        return base

    def parse_atom(self):
        tok = self.peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        kind, value = tok
        if kind == "num":
            self.advance()
            return value
        if kind == "name":
            self.advance()
            if value not in self.variables:
                raise ValueError(f"unknown variable: {value!r}")
            return float(self.variables[value])
        if kind == "lparen":
            self.advance()
            result = self.parse_expr()
            closing = self.peek()
            if closing is None or closing[0] != "rparen":
                raise ValueError("unbalanced parentheses")
            self.advance()
            return result
        raise ValueError(f"unexpected token: {value!r}")


def evaluate(expr: str, variables: "dict[str, float] | None" = None) -> float:
    """Evaluate an arithmetic expression and return the result as a float."""
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables if variables is not None else {})
    result = parser.parse_expr()
    if parser.pos != len(parser.tokens):
        raise ValueError("unexpected trailing input")
    return float(result)
