import re
from typing import Optional, List, Tuple, Union

class Token:
    def __init__(self, type_: str, value: Union[str, float], pos: int = 0):
        self.type = type_
        self.value = value
        self.pos = pos
    
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
            
            # Skip whitespace
            if ch.isspace():
                self.pos += 1
                continue
            
            # Parentheses
            if ch == '(':
                self.tokens.append(Token('LPAREN', '(', self.pos))
                self.pos += 1
                continue
            if ch == ')':
                self.tokens.append(Token('RPAREN', ')', self.pos))
                self.pos += 1
                continue
            
            # Operators
            if ch in '+-*/%^':
                op = ch
                self.tokens.append(Token(op, op, self.pos))
                self.pos += 1
                continue
            
            # Numbers (including decimals)
            if ch.isdigit() or ch == '.':
                start = self.pos
                while self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
                    self.pos += 1
                num_str = self.text[start:self.pos]
                
                # Handle cases like ".5" or "3."
                if '.' in num_str:
                    parts = num_str.split('.')
                    if len(parts) > 2:
                        raise ValueError(f"Invalid number format: {num_str}")
                    try:
                        self.tokens.append(Token('NUMBER', float(num_str), start))
                    except ValueError:
                        raise ValueError(f"Invalid number: {num_str}")
                else:
                    try:
                        self.tokens.append(Token('NUMBER', int(num_str), start))
                    except ValueError:
                        raise ValueError(f"Invalid number: {num_str}")
                continue
            
            # Variable names
            if ch.isalpha() or ch == '_':
                start = self.pos
                while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                    self.pos += 1
                var_name = self.text[start:self.pos]
                
                # Check if it's a valid variable name
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                    raise ValueError(f"Invalid variable name: {var_name}")
                
                self.tokens.append(Token('VAR', var_name, start))
                continue
            
            # Unknown character
            raise ValueError(f"Unexpected character: {ch!r} at position {self.pos}")
        
        return self.tokens

class Parser:
    def __init__(self, tokens: List[Token], variables: Optional[dict] = None):
        self.tokens = tokens
        self.variables = variables or {}
        self.pos = 0
    
    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token('EOF', '', len(self.tokens))
    
    def consume(self, expected_type: Optional[str] = None) -> Token:
        token = self.current()
        if expected_type and token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type}")
        self.pos += 1
        return token
    
    def parse(self) -> float:
        result = self.parse_expression()
        if self.current().type != 'EOF':
            raise ValueError(f"Unexpected token after expression: {self.current()}")
        return result
    
    def parse_expression(self) -> float:
        # + and - have lowest precedence (left-associative)
        left = self.parse_term()
        
        while self.current().type in ('+', '-'):
            op_token = self.consume()
            right = self.parse_term()
            
            if op_token.type == '+':
                left = left + right
            else:  # '-'
                left = left - right
        
        return left
    
    def parse_term(self) -> float:
        # *, /, % have higher precedence (left-associative)
        left = self.parse_power()
        
        while self.current().type in ('*', '/', '%'):
            op_token = self.consume()
            right = self.parse_power()
            
            if op_token.type == '*':
                left = left * right
            elif op_token.type == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:  # '%'
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        
        return left
    
    def parse_power(self) -> float:
        # ^ has highest precedence (right-associative)
        base = self.parse_unary()
        
        while self.current().type == '^':
            op_token = self.consume()
            exponent = self.parse_power()  # Right-associative
            base = base ** exponent
        
        return base
    
    def parse_unary(self) -> float:
        # Handle unary minus (and plus if we wanted to support it)
        if self.current().type == '-':
            self.consume()
            value = -self.parse_power()  # Unary minus binds looser than ^
            return value
        
        if self.current().type == '+':
            self.consume()
            return self.parse_power()
        
        return self.parse_primary()
    
    def parse_primary(self) -> float:
        token = self.current()
        
        if token.type == 'NUMBER':
            self.consume()
            return token.value
        
        elif token.type == 'VAR':
            var_name = token.value
            self.consume()
            
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            
            value = self.variables[var_name]
            if isinstance(value, (int, float)):
                return float(value)
            else:
                raise ValueError(f"Variable {var_name} must have a numeric value")
        
        elif token.type == 'LPAREN':
            self.consume()
            result = self.parse_expression()
            self.consume('RPAREN')
            return result
        
        else:
            raise ValueError(f"Unexpected token: {token}")

def evaluate(expr: str, variables: Optional[dict[str, float]] = None) -> float:
    lexer = Lexer(expr)
    tokens = lexer.tokenize()
    
    if not tokens:
        raise ValueError("Empty expression")
    
    parser = Parser(tokens, variables)
    return parser.parse()

# Test cases to verify correctness
if __name__ == "__main__":
    # Basic arithmetic
    assert evaluate("1 + 2") == 3.0
    assert evaluate("1 - 2") == -1.0
    assert evaluate("2 * 3") == 6.0
    assert evaluate("8 / 4") == 2.0
    
    # Precedence
    assert evaluate("2 + 3 * 4") == 14.0
    assert evaluate("(2 + 3) * 4") == 20.0
    
    # Exponentiation (right-associative)
    assert evaluate("2 ^ 3 ^ 2") == 512.0  # 2^(3^2) = 2^9 = 512
    assert evaluate("2 ^ 3") == 8.0
    
    # Unary minus
    assert evaluate("-3") == -3.0
    assert evaluate("--3") == 3.0
    assert evaluate("-2 ^ 2") == -4.0  # -(2^2) = -4
    assert evaluate("-(2 + 3)") == -5.0
    
    # Variables
    assert evaluate("x + y", {"x": 1, "y": 2}) == 3.0
    assert evaluate("x * x", {"x": 5}) == 25.0
    
    # Division by zero
    try:
        evaluate("1 / 0")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Modulo by zero
    try:
        evaluate("5 % 0")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("All tests passed!")
