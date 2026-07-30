def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression string without using eval/exec/ast."""
    if variables is None:
        variables = {}

    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables)
    result = parser.parse_expr()
    if parser.pos < len(parser.tokens):
        raise ValueError("Unexpected token after expression")
    return float(result)


def _tokenize(expr: str) -> list[tuple[str, str]]:
    """Tokenize an arithmetic expression into (type, value) tuples."""
    tokens: list[tuple[str, str]] = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]

        # Skip whitespace
        if c.isspace():
            i += 1
            continue

        # Numbers: integers and decimals (e.g., "3", "4.5"; optionally leading dot like ".5")
        if c.isdigit() or (c == '.' and i + 1 < n and expr[i + 1].isdigit()):
            j = i
            has_dot = False
            while j < n and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUM', expr[i:j]))
            i = j
            continue

        # Identifiers: variable names matching [a-zA-Z_][a-zA-Z0-9_]*
        if c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
            continue

        # Operators and parentheses
        if c in '+-*/%^()':
            tokens.append((c, c))
            i += 1
            continue

        raise ValueError(f"Unexpected character: {c!r}")

    return tokens


class _Parser:
    """Recursive descent parser for the arithmetic expression grammar.

    Grammar (precedence lowest to highest):
        expr      := term (('+' | '-') term)*
        term      := factor (('*' | '/' | '%') factor)*
        factor    := ('-')? factor | power
        power     := primary ('^' factor)?          # right-associative
        primary   := NUMBER | VARIABLE | '(' expr ')'

    Note: unary minus at the `factor` level binds looser than `^`,
    so `-2^2` parses as -(2^2) = -4, not (-2)^2 = 4.
    """

    def __init__(self, tokens: list[tuple[str, str]], variables: dict[str, float]):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    # ---- helpers ----------------------------------------------------------

    def peek(self) -> tuple[str, str] | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type: str | None = None) -> tuple[str, str]:
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if expected_type is not None and tok[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {tok[1]!r}")
        self.pos += 1
        return tok

    # ---- grammar rules ----------------------------------------------------

    def parse_expr(self) -> float:
        """expr := term (('+' | '-') term)*"""
        left = self.parse_term()
        while True:
            tok = self.peek()
            if tok and tok[0] in ('+', '-'):
                op = self.consume()[1]
                right = self.parse_term()
                left = left + right if op == '+' else left - right
            else:
                break
        return left

    def parse_term(self) -> float:
        """term := factor (('*' | '/' | '%') factor)*"""
        left = self.parse_factor()
        while True:
            tok = self.peek()
            if tok and tok[0] in ('*', '/', '%'):
                op = self.consume()[1]
                right = self.parse_factor()
                if op == '*':
                    left *= right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    left /= right
                else:  # '%'
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left %= right
            else:
                break
        return left

    def parse_factor(self) -> float:
        """factor := ('-')? factor | power"""
        tok = self.peek()
        if tok and tok[0] == '-':
            self.consume('-')
            operand = self.parse_factor()
            return -operand
        else:
            return self.parse_power()

    def parse_power(self) -> float:
        """power := primary ('^' factor)?   # right-associative"""
        base = self.parse_primary()
        tok = self.peek()
        if tok and tok[0] == '^':
            self.consume('^')
            exponent = self.parse_factor()  # recurse on right side for right-assoc
            return base ** exponent
        return base

    def parse_primary(self) -> float:
        """primary := NUMBER | VARIABLE | '(' expr ')'"""
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")

        if tok[0] == 'NUM':
            self.consume('NUM')
            return float(tok[1])

        if tok[0] == 'VAR':
            self.consume('VAR')
            name = tok[1]
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            try:
                return float(self.variables[name])
            except (TypeError, ValueError):
                raise ValueError(f"Variable {name!r} is not a number")

        if tok[0] == '(':
            self.consume('(')
            result = self.parse_expr()
            closing = self.peek()
            if closing is None or closing[0] != ')':
                raise ValueError("Unbalanced parentheses: missing ')'")
            self.consume(')')
            return result

        raise ValueError(f"Unexpected token: {tok[1]!r}")
