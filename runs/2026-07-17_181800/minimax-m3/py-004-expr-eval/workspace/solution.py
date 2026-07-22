def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # ---------------- Tokenizer ----------------
    class Token:
        __slots__ = ("kind", "value", "pos")

        def __init__(self, kind, value, pos):
            self.kind = kind
            self.value = value
            self.pos = pos

        def __repr__(self):
            return f"Token({self.kind!r}, {self.value!r})"

    tokens: list = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            if j < n and expr[j] == ".":
                j += 1
                while j < n and expr[j].isdigit():
                    j += 1
            tokens.append(Token("NUM", float(expr[i:j]), i))
            i = j
            continue
        if c.isalpha() or c == "_":
            j = i + 1
            while j < n and (expr[j].isalnum() or expr[j] == "_"):
                j += 1
            tokens.append(Token("ID", expr[i:j], i))
            i = j
            continue
        if c in "+-*/%^()":
            tokens.append(Token("OP", c, i))
            i += 1
            continue
        raise ValueError(f"Unexpected character {c!r} at position {i}")
    tokens.append(Token("EOF", None, n))

    # ---------------- Parser ----------------
    # Grammar (precedence: lowest -> highest):
    #   additive       := multiplicative (('+'|'-') multiplicative)*
    #   multiplicative := unary          (('*'|'/'|'%') unary)*
    #   unary          := ('-'|'+') unary | power
    #   power          := primary ('^' unary)?   # right-associative via unary
    #   primary        := NUM | ID | '(' additive ')'
    pos = 0

    def peek():
        return tokens[pos]

    def advance():
        nonlocal pos
        t = tokens[pos]
        pos += 1
        return t

    def expect_op(value):
        t = peek()
        if t.kind != "OP" or t.value != value:
            raise ValueError(f"Expected {value!r} at position {t.pos}, got {t}")
        advance()

    def parse_primary() -> float:
        t = peek()
        if t.kind == "NUM":
            advance()
            return t.value
        if t.kind == "ID":
            advance()
            if t.value not in variables:
                raise ValueError(
                    f"Unknown variable {t.value!r} at position {t.pos}"
                )
            return float(variables[t.value])
        if t.kind == "OP" and t.value == "(":
            advance()
            val = parse_additive()
            expect_op(")")
            return val
        raise ValueError(f"Unexpected token {t}")

    def parse_power() -> float:
        base = parse_primary()
        t = peek()
        if t.kind == "OP" and t.value == "^":
            advance()
            exp = parse_unary()  # right-assoc: parse_unary -> parse_power chains ^
            return base ** exp
        return base

    def parse_unary() -> float:
        t = peek()
        if t.kind == "OP" and t.value == "-":
            advance()
            return -parse_unary()
        if t.kind == "OP" and t.value == "+":
            advance()
            return parse_unary()
        return parse_power()

    def parse_multiplicative() -> float:
        left = parse_unary()
        while True:
            t = peek()
            if t.kind != "OP" or t.value not in ("*", "/", "%"):
                break
            op_tok = advance()
            op = op_tok.value
            right = parse_unary()
            if right == 0:
                raise ValueError(
                    f"Division or modulo by zero at position {op_tok.pos}"
                )
            if op == "*":
                left = left * right
            elif op == "/":
                left = left / right
            else:  # '%'
                left = left % right
        return left

    def parse_additive() -> float:
        left = parse_multiplicative()
        while True:
            t = peek()
            if t.kind != "OP" or t.value not in ("+", "-"):
                break
            op_tok = advance()
            op = op_tok.value
            right = parse_multiplicative()
            left = (left + right) if op == "+" else (left - right)
        return left

    result = parse_additive()
    t = peek()
    if t.kind != "EOF":
        raise ValueError(f"Unexpected trailing token {t}")
    return float(result)
