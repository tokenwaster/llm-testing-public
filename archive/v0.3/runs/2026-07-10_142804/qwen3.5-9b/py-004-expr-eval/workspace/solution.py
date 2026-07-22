import re
from typing import Optional, List, Tuple, Union

class Token:
    NUMBER = 'NUMBER'
    VARIABLE = 'VARIABLE'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    STAR = 'STAR'
    SLASH = 'SLASH'
    PERCENT = 'PERCENT'
    CARET = 'CARET'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    
    def __init__(self, type: str, value: Union[str, float]):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

class Lexer:
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
            
            # Parentheses
            if ch == '(':
                self.tokens.append(Token(Token.LPAREN, '('))
                self.pos += 1
                continue
            if ch == ')':
                self.tokens.append(Token(Token.RPAREN, ')'))
                self.pos += 1
                continue
            
            # Operators
            if ch in '+-*/%^':
                self.tokens.append(Token(
                    Token.PLUS if ch == '+' else
                    Token.MINUS if ch == '-' else
                    Token.STAR if ch == '*' else
                    Token.SLASH if ch == '/' else
                    Token.PERCENT if ch == '%' else
                    Token.CARET, ch))
                self.pos += 1
                continue
            
            # Numbers and variables
            start = self.pos
            while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] in '_.'):
                self.pos += 1
            text = self.text[start:self.pos]
            
            if text[0].isdigit():
                num_val = float(text.replace('.', ''))
                # Check if it's a decimal number
                if '.' in text:
                    parts = text.split('.')
                    int_part = parts[0] or '0'
                    frac_part = parts[1] if len(parts) > 1 else ''
                    num_val = float(int_part + '.' + frac_part)
                self.tokens.append(Token(Token.NUMBER, num_val))
            elif text[0].isalpha() or text[0] == '_':
                self.tokens.append(Token(Token.VARIABLE, text))
            else:
                raise ValueError(f"Invalid character: {ch}")
        
        self.tokens.append(Token(Token.EOF, None))
        return self.tokens

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current(self) -> Token:
        return self.tokens[self.pos]
    
    def consume(self, expected_type: str = None) -> Token:
        token = self.current()
        if expected_type and token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type}")
        self.pos += 1
        return token
    
    def parse(self) -> float:
        result = self.parse_expression()
        if self.current().type != Token.EOF:
            raise ValueError(f"Unexpected token: {self.current()}")
        return result
    
    def parse_expression(self) -> float:
        left = self.parse_term()
        
        while self.current().type in (Token.PLUS, Token.MINUS):
            op_token = self.consume()
            right = self.parse_term()
            
            if op_token.type == Token.PLUS:
                left = left + right
            else:
                left = left - right
        
        return left
    
    def parse_term(self) -> float:
        left = self.parse_power()
        
        while self.current().type in (Token.STAR, Token.SLASH, Token.PERCENT):
            op_token = self.consume()
            right = self.parse_power()
            
            if op_token.type == Token.STAR:
                left = left * right
            elif op_token.type == Token.SLASH:
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:  # PERCENT
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        
        return left
    
    def parse_power(self) -> float:
        base = self.parse_unary()
        
        if self.current().type == Token.CARET:
            self.consume()
            exponent = self.parse_power()  # Right-associative
            result = base ** exponent
            return result
        
        return base
    
    def parse_unary(self) -> float:
        if self.current().type == Token.MINUS:
            self.consume()
            value = -self.parse_unary()
            return value
        elif self.current().type == Token.PLUS:
            self.consume()
            return self.parse_unary()
        
        return self.parse_primary()
    
    def parse_primary(self) -> float:
        token = self.current()
        
        if token.type == Token.NUMBER:
            self.consume()
            return token.value
        
        elif token.type == Token.VARIABLE:
            self.consume()
            var_name = token.value
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return float(self.variables[var_name])
        
        elif token.type == Token.LPAREN:
            self.consume()
            result = self.parse_expression()
            self.consume(Token.RPAREN)
            return result
        
        else:
            raise ValueError(f"Unexpected token: {token}")

def evaluate(expr: str, variables: Optional[dict[str, float]] = None) -> float:
    lexer = Lexer(expr)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    parser.variables = variables or {}
    
    return parser.parse()
