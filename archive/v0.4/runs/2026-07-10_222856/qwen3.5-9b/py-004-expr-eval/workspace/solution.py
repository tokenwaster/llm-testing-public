import re
from typing import List, Tuple, Optional

class Token:
    NUMBER = 'NUMBER'
    OPERATOR = 'OPERATOR'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    IDENTIFIER = 'IDENTIFIER'
    
    def __init__(self, type_: str, value: str):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

class Parser:
    def __init__(self, tokens: List[Token], variables: dict[str, float]):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables or {}
    
    def current(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None
    
    def consume(self, expected_type: str = None) -> Token:
        token = self.current()
        if expected_type and token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type}")
        self.pos += 1
        return token
    
    def parse_expression(self) -> float:
        result = self.parse_additive()
        if self.current():
            raise ValueError(f"Unexpected token after expression: {self.current()}")
        return result
    
    def parse_additive(self) -> float:
        left = self.parse_multiplicative()
        
        while True:
            token = self.current()
            if token and token.type == 'OPERATOR' and token.value in ('+', '-'):
                op = token.value
                self.consume('OPERATOR')
                right = self.parse_multiplicative()
                if op == '+':
                    left = left + right
                else:
                    left = left - right
            else:
                break
        
        return left
    
    def parse_multiplicative(self) -> float:
        left = self.parse_power()
        
        while True:
            token = self.current()
            if token and token.type == 'OPERATOR' and token.value in ('*', '/', '%'):
                op = token.value
                self.consume('OPERATOR')
                right = self.parse_power()
                if op == '*':
                    left = left * right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    left = left / right
                else:  # '%'
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            else:
                break
        
        return left
    
    def parse_power(self) -> float:
        base = self.parse_unary()
        
        token = self.current()
        if token and token.type == 'OPERATOR' and token.value == '^':
            self.consume('OPERATOR')
            exponent = self.parse_power()  # right-associative
            return base ** exponent
        
        return base
    
    def parse_unary(self) -> float:
        token = self.current()
        
        if token and token.type == 'OPERATOR' and token.value == '-':
            self.consume('OPERATOR')
            value = self.parse_unary()
            return -value
        
        return self.parse_primary()
    
    def parse_primary(self) -> float:
        token = self.current()
        
        if not token:
            raise ValueError("Unexpected end of expression")
        
        if token.type == 'NUMBER':
            self.consume('NUMBER')
            return float(token.value)
        
        elif token.type == 'IDENTIFIER':
            self.consume('IDENTIFIER')
            name = token.value
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            value = self.variables[name]
            if isinstance(value, (int, float)):
                return float(value)
            else:
                raise ValueError(f"Variable {name} has non-numeric value")
        
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            result = self.parse_expression()
            self.consume('RPAREN', 'RPAREN')
            return result
        
        else:
            raise ValueError(f"Unexpected token: {token}")

def tokenize(expr: str) -> List[Token]:
    tokens = []
    i = 0
    
    while i < len(expr):
        ch = expr[i]
        
        # Skip whitespace
        if ch.isspace():
            i += 1
            continue
        
        # Parentheses
        if ch == '(':
            tokens.append(Token('LPAREN', '('))
            i += 1
            continue
        
        if ch == ')':
            tokens.append(Token('RPAREN', ')'))
            i += 1
            continue
        
        # Operators and ^
        if ch in '+-*/%^':
            tokens.append(Token('OPERATOR', ch))
            i += 1
            continue
        
        # Numbers (including decimals)
        if ch.isdigit() or ch == '.':
            j = i
            has_dot = False
            
            while j < len(expr):
                c = expr[j]
                if c.isdigit():
                    j += 1
                elif c == '.' and not has_dot:
                    has_dot = True
                    j += 1
                else:
                    break
            
            num_str = expr[i:j]
            tokens.append(Token('NUMBER', num_str))
            i = j
            continue
        
        # Identifiers (variable names)
        if ch.isalpha() or ch == '_':
            j = i
            while j < len(expr):
                c = expr[j]
                if c.isalnum() or c == '_':
                    j += 1
                else:
                    break
            
            ident_str = expr[i:j]
            tokens.append(Token('IDENTIFIER', ident_str))
            i = j
            continue
        
        # Unknown character
        raise ValueError(f"Unexpected character: {ch}")
    
    return tokens

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if not expr or not expr.strip():
        raise ValueError("Empty expression")
    
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    result = parser.parse_expression()
    
    return result
