"""Arithmetic expression evaluator with a hand-written tokenizer + recursive
descent parser (no eval/exec/ast/parsing libraries).

Grammar
-------
expr   := term (('+' | '-') term)*
term   := unary (('*' | '/' | '%') unary)*
unary  := ('-' | '+') unary | power
power  := atom ('^' unary)?          # right-associative, binds tighter than unary minus
atom   := NUMBER | NAME | '(' expr ')'
"""

from __future__ import annotations


# --------------------------------------------------------------------------- #
# Tokenizer
# --------------------------------------------------------------------------- #

_OPERATORS = {'+', '-', '*', '/', '%', '^'}
_PARENS = {'(', ')'}

_DIGITS = '0123456789'


class _Token:
    __slots__ = ('kind', 'value', 'pos')

    def __init__(self, kind: str, value, pos: int):
        self.kind = kind      # 'num' | 'name' | 'op' | 'lparen' | 'rparen'
        self.value = value
        self.pos = pos

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"_Token({self.kind!r}, {self.value!r}, {self.pos})"


def _is_name_start(ch: str) -> bool:
    return ch == '_' or ('a' <= ch <= 'z') or ('A' <= ch <= 'Z')


def _is_name_char(ch: str) -> bool:
    return _is_name_start(ch) or ch in _DIGITS


def _tokenize(expr: str) -> list[_Token]:
    if not isinstance(expr, str):
        raise ValueError("expression must be a string")

    tokens: list[_Token] = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        # whitespace
        if ch.isspace():
            i += 1
            continue

        # numbers: digits [ '.' digits ]
        if ch in _DIGITS or (ch == '.' and i + 1 < n and expr[i + 1] in _DIGITS):
            start = i
            seen_dot = False
            seen_digit = False
            while i < n:
                c = expr[i]
                if c in _DIGITS:
                    seen_digit = True
                    i += 1
                elif c == '.' and not seen_dot:
                    seen_dot = True
                    i += 1
                else:
                    break
            text = expr[start:i]
            if not seen_digit:
                raise ValueError(f"malformed number at position {start}: {text!r}")
            # optional exponent part (e.g. 1e3, 2.5E-4)
            if i < n and expr[i] in 'eE':
                j = i + 1
                if j < n and expr[j] in '+-':
                    j += 1
                if j < n and expr[j] in _DIGITS:
                    while j < n and expr[j] in _DIGITS:
                        j += 1
                    text = expr[start:j]
                    i = j
            try:
                value = float(text)
            except (ValueError, OverflowError):
                raise ValueError(f"malformed number at position {start}: {text!r}")
            tokens.append(_Token('num', value, start))
            continue

        # identifiers
        if _is_name_start(ch):
            start = i
            while i < n and _is_name_char(expr[i]):
                i += 1
            tokens.append(_Token('name', expr[start:i], start))
            continue

        # operators / parentheses
        if ch in _OPERATORS:
            tokens.append(_Token('op', ch, i))
            i += 1
            continue

        if ch == '(':
            tokens.append(_Token('lparen', ch, i))
            i += 1
            continue

        if ch == ')':
            tokens.append(_Token('rparen', ch, i))
            i += 1
            continue

        raise ValueError(f"unexpected character {ch!r} at position {i}")

    return tokens


# --------------------------------------------------------------------------- #
# Parser / evaluator
# --------------------------------------------------------------------------- #

class _Parser:
    def __init__(self, tokens: list[_Token], variables: dict):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    # -- token helpers ----------------------------------------------------- #
    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _next(self):
        tok = self._peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        self.pos += 1
        return tok

    def _at_op(self, *ops) -> bool:
        tok = self._peek()
        return tok is not None and tok.kind == 'op' and tok.value in ops

    # -- grammar rules ----------------------------------------------------- #
    def parse(self) -> float:
        if not self.tokens:
            raise ValueError("empty expression")
        value = self.parse_expr()
        tok = self._peek()
        if tok is not None:
            if tok.kind == 'rparen':
                raise ValueError(f"unbalanced parenthesis at position {tok.pos}")
            raise ValueError(
                f"unexpected token {tok.value!r} at position {tok.pos}")
        return value

    def parse_expr(self) -> float:
        value = self.parse_term()
        while self._at_op('+', '-'):
            op = self._next().value
            rhs = self.parse_term()
            value = value + rhs if op == '+' else value - rhs
        return value

    def parse_term(self) -> float:
        value = self.parse_unary()
        while self._at_op('*', '/', '%'):
            tok = self._next()
            op = tok.value
            rhs = self.parse_unary()
            if op == '*':
                value = value * rhs
            elif op == '/':
                if rhs == 0:
                    raise ValueError("division by zero")
                value = value / rhs
            else:  # '%'
                if rhs == 0:
                    raise ValueError("modulo by zero")
                try:
                    value = value % rhs
                except (ZeroDivisionError, ValueError):
                    raise ValueError("modulo by zero")
        return value

    def parse_unary(self) -> float:
        if self._at_op('-'):
            self._next()
            return -self.parse_unary()
        if self._at_op('+'):
            self._next()
            return self.parse_unary()
        return self.parse_power()

    def parse_power(self) -> float:
        base = self.parse_atom()
        if self._at_op('^'):
            self._next()
            # right-associative; unary minus allowed in the exponent
            exponent = self.parse_unary()
            return self._pow(base, exponent)
        return base

    @staticmethod
    def _pow(base: float, exponent: float) -> float:
        try:
            result = base ** exponent
        except OverflowError:
            raise ValueError("numeric overflow in exponentiation")
        except ZeroDivisionError:
            raise ValueError("division by zero")
        except ValueError:
            raise ValueError("invalid exponentiation")
        if isinstance(result, complex):
            raise ValueError("complex result in exponentiation")
        return float(result)

    def parse_atom(self) -> float:
        tok = self._peek()
        if tok is None:
            raise ValueError("unexpected end of expression")

        if tok.kind == 'num':
            self._next()
            return float(tok.value)

        if tok.kind == 'name':
            self._next()
            name = tok.value
            if not self.variables or name not in self.variables:
                raise ValueError(f"unknown variable: {name!r}")
            raw = self.variables[name]
            if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                try:
                    return float(raw)
                except (TypeError, ValueError):
                    raise ValueError(
                        f"variable {name!r} has non-numeric value: {raw!r}")
            return float(raw)

        if tok.kind == 'lparen':
            self._next()
            value = self.parse_expr()
            closing = self._peek()
            if closing is None or closing.kind != 'rparen':
                raise ValueError("unbalanced parenthesis: missing ')'")
            self._next()
            return value

        if tok.kind == 'rparen':
            raise ValueError(f"unbalanced parenthesis at position {tok.pos}")

        raise ValueError(f"unexpected token {tok.value!r} at position {tok.pos}")


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression and return the result as a float."""
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables if variables is not None else {})
    result = parser.parse()
    try:
        return float(result)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("expression did not evaluate to a real number")


if __name__ == "__main__":  # pragma: no cover
    samples = [
        ("1 + 2 * 3", None),
        ("2^3^2", None),
        ("-2^2", None),
        ("--3", None),
        ("(1 + 2) * (3 - 4.5)", None),
        ("10 % 4", None),
        ("x * y + 1", {"x": 2, "y": 3.5}),
    ]
    for text, env in samples:
        print(f"{text!r} -> {evaluate(text, env)}")
