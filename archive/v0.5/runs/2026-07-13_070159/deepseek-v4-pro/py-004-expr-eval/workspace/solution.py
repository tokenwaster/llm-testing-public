from __future__ import annotations
from typing import Dict, Optional

class Token:
    def __init__(self, type: str, value: Optional[float | str] = None):
        self.type = type
        self.value = value

def tokenize(expr: str) -> list[Token]:
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            start = i
            while i < n and expr[i].isdigit():
                i += 1
            if i < n and expr[i] == '.':
                i += 1
                if i < n and expr[i].isdigit():
                    while i < n and expr[i].isdigit():
                        i += 1
                else:
                    raise ValueError(f"Malformed number: {expr[start:i]}")
            num_str = expr[start:i]
            tokens.append(Token('NUMBER', float(num_str)))
            continue
        if c.isalpha() or c == '_':
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            var_name = expr[start:i]
            tokens.append(Token('VARIABLE', var_name))
            continue
        if c == '+':
            tokens.append(Token('PLUS'))
        elif c == '-':
            tokens.append(Token('MINUS'))
        elif c == '*':
            tokens.append(Token('STAR'))
        elif c == '/':
            tokens.append(Token('SLASH'))
        elif c == '%':
            tokens.append(Token('PERCENT'))
        elif c == '^':
            tokens.append(Token('CARET'))
        elif c == '(':
            tokens.append(Token('LPAREN'))
        elif c == ')':
            tokens.append(Token('RPAREN'))
        else:
            raise ValueError(f"Invalid character: {c}")
        i += 1
    tokens.append(Token('EOF'))
    return tokens

class Parser:
    def __init__(self, tokens: list[Token], variables: Dict[str, float]):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def consume(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def expect(self, type: str) -> Token:
        token = self.consume()
        if token.type != type:
            raise ValueError(f"Expected {type}, got {token.type}")
        return token

    def parse_expression(self, precedence: int = 0) -> float:
        token = self.consume()
        left = self.nud(token)
        while True:
            token = self.peek()
            if token.type in ('PLUS', 'MINUS', 'STAR', 'SLASH', 'PERCENT', 'CARET'):
                op_prec = self._precedence(token.type)
                if op_prec <= precedence:
                    break
                self.consume()
                # Right-associative for '^', left-associative for others
                if token.type == 'CARET':
                    next_prec = op_prec
                else:
                    next_prec = op_prec + 1
                right = self.parse_expression(next_prec)
                left = self._apply_infix(left, token.type, right)
            else:
                break
        return left

    def nud(self, token: Token) -> float:
        if token.type == 'NUMBER':
            return float(token.value)
        elif token.type == 'VARIABLE':
            name = token.value
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        elif token.type == 'LPAREN':
            expr = self.parse_expression(0)
            self.expect('RPAREN')
            return expr
        elif token.type == 'MINUS':
            # Unary minus, precedence 3 (binds looser than ^, tighter than * / %)
            operand = self.parse_expression(3)
            return -operand
        else:
            raise ValueError(f"Unexpected token: {token.type}")

    def _apply_infix(self, left: float, op: str, right: float) -> float:
        if op == 'PLUS':
            return left + right
        elif op == 'MINUS':
            return left - right
        elif op == 'STAR':
            return left * right
        elif op == 'SLASH':
            if right == 0:
                raise ValueError("Division by zero")
            return left / right
        elif op == 'PERCENT':
            if right == 0:
                raise ValueError("Modulo by zero")
            return left % right
        elif op == 'CARET':
            return left ** right
        else:
            raise ValueError(f"Unknown operator: {op}")

    @staticmethod
    def _precedence(op: str) -> int:
        if op in ('PLUS', 'MINUS'):
            return 1
        elif op in ('STAR', 'SLASH', 'PERCENT'):
            return 2
        elif op == 'CARET':
            return 4
        else:
            return 0

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluate an arithmetic expression without using eval/exec/ast.

    Args:
        expr: The expression string to evaluate.
        variables: Optional dictionary mapping variable names to float values.

    Returns:
        The result as a float.

    Raises:
        ValueError: For malformed syntax, unbalanced parentheses, unknown variables,
                    or division/modulo by zero.
    """
    if variables is None:
        variables = {}
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    result = parser.parse_expression(0)
    if parser.peek().type != 'EOF':
        raise ValueError("Unexpected tokens after expression")
    return float(result)
