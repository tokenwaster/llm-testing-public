import re
from typing import Optional, List, Tuple, Union

class Token:
    NUMBER = 'NUMBER'
    OPERATOR = 'OPERATOR'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    IDENTIFIER = 'IDENTIFIER'
    EOF = 'EOF'
    
    def __init__(self, type_: str, value: Union[str, float]):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

class Tokenizer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            
            if ch.isspace():
                self.pos += 1
                continue
            
            # Number (integer or decimal)
            if ch.isdigit() or ch == '.':
                start = self.pos
                has_dot = False
                while self.pos < len(self.text):
                    ch = self.text[self.pos]
                    if ch.isdigit():
                        self.pos += 1
                    elif ch == '.' and not has_dot:
                        has_dot = True
                        self.pos += 1
                    else:
                        break
                num_str = self.text[start:self.pos]
                try:
                    value = float(num_str)
                    self.tokens.append(Token(Token.NUMBER, value))
                except ValueError:
                    raise ValueError(f"Invalid number: {num_str}")
                continue
            
            # Operator or identifier
            if ch in '+-*/%^':
                op_map = {'+': '+', '-': '-', '*': '*', '/': '/', '%': '%', '^': '^'}
                self.tokens.append(Token(Token.OPERATOR, op_map[ch]))
                self.pos += 1
                continue
            
            # Parentheses
            if ch == '(':
                self.tokens.append(Token(Token.LPAREN, '('))
                self.pos += 1
                continue
            
            if ch == ')':
                self.tokens.append(Token(Token.RPAREN, ')'))
                self.pos += 1
                continue
            
            # Identifier (variable name)
            if ch.isalpha() or ch == '_':
                start = self.pos
                while self.pos < len(self.text):
                    ch = self.text[self.pos]
                    if ch.isalnum() or ch == '_':
                        self.pos += 1
                    else:
                        break
                ident = self.text[start:self.pos]
                self.tokens.append(Token(Token.IDENTIFIER, ident))
                continue
            
            # Unknown character
            raise ValueError(f"Unexpected character: {ch!r}")
        
        self.tokens.append(Token(Token.EOF, None))
        return self.tokens

class Parser:
    def __init__(self, tokens: List[Token], variables: Optional[dict] = None):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables or {}
    
    def current(self) -> Token:
        return self.tokens[self.pos]
    
    def peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.current()
    
    def consume(self, expected_type: str = None, expected_value: str = None) -> Token:
        token = self.current()
        if expected_type and token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type}")
        if expected_value and token.value != expected_value:
            raise ValueError(f"Expected '{expected_value}', got '{token.value}'")
        self.pos += 1
        return token
    
    def parse(self) -> float:
        result = self.parse_expression()
        if self.current().type != Token.EOF:
            raise ValueError(f"Unexpected token after expression: {self.current()}")
        return result
    
    def parse_expression(self) -> float:
        # expression -> term (('+' | '-') term)*
        left = self.parse_term()
        
        while self.current().type == Token.OPERATOR and self.current().value in ('+', '-'):
            op = self.consume().value
            right = self.parse_term()
            if op == '+':
                left = left + right
            else:  # '-'
                left = left - right
        
        return left
    
    def parse_term(self) -> float:
        # term -> factor (('*' | '/' | '%') factor)*
        left = self.parse_factor()
        
        while self.current().type == Token.OPERATOR and self.current().value in ('*', '/', '%'):
            op = self.consume().value
            right = self.parse_factor()
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
        
        return left
    
    def parse_factor(self) -> float:
        # factor -> power ('^' power)? for right-associativity
        base = self.parse_power()
        
        while self.current().type == Token.OPERATOR and self.current().value == '^':
            exp = self.parse_power()
            base = base ** exp
        
        return base
    
    def parse_power(self) -> float:
        # power -> unary
        return self.parse_unary()
    
    def parse_unary(self) -> float:
        # unary -> ('-' | '+')? primary
        if self.current().type == Token.OPERATOR and self.current().value in ('-', '+'):
            op = self.consume().value
            value = self.parse_unary()  # Recursive for multiple unary operators
            if op == '-':
                return -value
            else:  # '+'
                return value
        
        return self.parse_primary()
    
    def parse_primary(self) -> float:
        token = self.current()
        
        if token.type == Token.NUMBER:
            self.consume()
            return token.value
        
        elif token.type == Token.IDENTIFIER:
            name = token.value
            self.consume()
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            value = self.variables[name]
            if not isinstance(value, (int, float)):
                raise ValueError(f"Variable '{name}' must have numeric value")
            return float(value)
        
        elif token.type == Token.LPAREN:
            self.consume()  # consume '('
            result = self.parse_expression()
            self.consume(Token.RPAREN, ')')  # consume ')'
            return result
        
        else:
            raise ValueError(f"Unexpected token: {token}")

def evaluate(expr: str, variables: Optional[dict] = None) -> float:
    tokenizer = Tokenizer(expr)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens, variables)
    return parser.parse()
