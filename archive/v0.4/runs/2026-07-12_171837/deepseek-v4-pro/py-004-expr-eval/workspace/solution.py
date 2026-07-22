import re
from typing import Optional

# Token types
NUMBER = 'NUMBER'
PLUS = 'PLUS'
MINUS = 'MINUS'
STAR = 'STAR'
SLASH = 'SLASH'
PERCENT = 'PERCENT'
CARET = 'CARET'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
VARIABLE = 'VARIABLE'
EOF = 'EOF'

class Token:
    def __init__(self, type: str, value=None):
        self.type = type
        self.value = value

def tokenize(expr: str):
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            num_str = expr[i:j]
            if num_str.count('.') > 1:
                raise ValueError(f"Invalid number: {num_str}")
            tokens.append(Token(NUMBER, float(num_str)))
            i = j
            continue
        if c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            var_name = expr[i:j]
            tokens.append(Token(VARIABLE, var_name))
            i = j
            continue
        # single char tokens
        if c == '+':
            tokens.append(Token(PLUS))
        elif c == '-':
            tokens.append(Token(MINUS))
        elif c == '*':
            tokens.append(Token(STAR))
        elif c == '/':
            tokens.append(Token(SLASH))
        elif c == '%':
            tokens.append(Token(PERCENT))
        elif c == '^':
            tokens.append(Token(CARET))
        elif c == '(':
            tokens.append(Token(LPAREN))
        elif c == ')':
            tokens.append(Token(RPAREN))
        else:
            raise ValueError(f"Invalid character: {c}")
        i += 1
    tokens.append(Token(EOF))
    return tokens

class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables if variables is not None else {}

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(EOF)

    def consume(self, expected_type=None):
        token = self.peek()
        if expected_type and token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type}")
        self.pos += 1
        return token

    def parse(self):
        result = self.expr()
        if self.peek().type != EOF:
            raise ValueError("Unexpected token after expression")
        return result

    def expr(self):
        left = self.term()
        while self.peek().type in (PLUS, MINUS):
            op = self.consume().type
            right = self.term()
            if op == PLUS:
                left = left + right
            else:
                left = left - right
        return left

    def term(self):
        left = self.unary()
        while self.peek().type in (STAR, SLASH, PERCENT):
            op = self.consume().type
            right = self.unary()
            if op == STAR:
                left = left * right
            elif op == SLASH:
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            elif op == PERCENT:
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def unary(self):
        if self.peek().type == MINUS:
            self.consume(MINUS)
            operand = self.unary()
            return -operand
        else:
            return self.factor()

    def factor(self):
        base = self.primary()
        if self.peek().type == CARET:
            self.consume(CARET)
            exponent = self.factor()  # right-associative
            return base ** exponent
        return base

    def primary(self):
        token = self.peek()
        if token.type == NUMBER:
            self.consume()
            return token.value
        elif token.type == VARIABLE:
            self.consume()
            name = token.value
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return self.variables[name]
        elif token.type == LPAREN:
            self.consume(LPAREN)
            expr_val = self.expr()
            if self.peek().type != RPAREN:
                raise ValueError("Unbalanced parentheses: missing closing parenthesis")
            self.consume(RPAREN)
            return expr_val
        else:
            raise ValueError(f"Unexpected token: {token.type}")

def evaluate(expr: str, variables: Optional[dict[str, float]] = None) -> float:
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
