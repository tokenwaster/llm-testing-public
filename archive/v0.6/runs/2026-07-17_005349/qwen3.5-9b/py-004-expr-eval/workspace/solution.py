import re
from typing import Optional, Tuple, Union

class ExpressionEvaluator:
    def __init__(self, expr: str, variables: Optional[dict[str, float]] = None):
        self.expr = expr.strip()
        self.variables = variables or {}
        self.pos = 0
        self.tokens: list[Tuple[str, Union[float, str]]] = []
        
    def tokenize(self) -> list[Tuple[str, Union[float, str]]]:
        tokens = []
        i = 0
        n = len(self.expr)
        
        while i < n:
            c = self.expr[i]
            
            if c.isspace():
                i += 1
                continue
            
            if c in '+-*/%^()':
                tokens.append(('OP', c))
                i += 1
                continue
            
            if c.isdigit() or (c == '.' and i + 1 < n and self.expr[i+1].isdigit()):
                j = i
                while j < n and (self.expr[j].isdigit() or self.expr[j] == '.'):
                    j += 1
                num_str = self.expr[i:j]
                tokens.append(('NUM', float(num_str)))
                i = j
                continue
            
            if c.isalpha() or c == '_':
                j = i
                while j < n and (self.expr[j].isalnum() or self.expr[j] == '_'):
                    j += 1
                var_name = self.expr[i:j]
                if var_name in self.variables:
                    tokens.append(('VAR', var_name))
                else:
                    raise ValueError(f"Unknown variable: {var_name}")
                i = j
                continue
            
            raise ValueError(f"Invalid character: {c}")
        
        return tokens
    
    def parse(self) -> float:
        self.tokens = self.tokenize()
        if not self.tokens:
            return 0.0
        
        result = self.parse_expression()
        
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token at position {self.pos}: {self.tokens[self.pos]}")
        
        return result
    
    def parse_expression(self) -> float:
        """Parse addition and subtraction (lowest precedence, left-associative)"""
        left = self.parse_term()
        
        while self.pos < len(self.tokens):
            op = self.tokens[self.pos][1]
            if op == '+':
                self.pos += 1
                right = self.parse_term()
                left = left + right
            elif op == '-':
                self.pos += 1
                right = self.parse_term()
                left = left - right
            else:
                break
        
        return left
    
    def parse_term(self) -> float:
        """Parse multiplication, division, modulo (left-associative)"""
        left = self.parse_power()
        
        while self.pos < len(self.tokens):
            op = self.tokens[self.pos][1]
            if op == '*':
                self.pos += 1
                right = self.parse_power()
                left = left * right
            elif op == '/':
                self.pos += 1
                right = self.parse_power()
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            elif op == '%':
                self.pos += 1
                right = self.parse_power()
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
            else:
                break
        
        return left
    
    def parse_power(self) -> float:
        """Parse exponentiation (right-associative)"""
        base = self.parse_unary()
        
        if self.pos < len(self.tokens) and self.tokens[self.pos][1] == '^':
            self.pos += 1
            exp = self.parse_power()  # Right-associative
            return base ** exp
        
        return base
    
    def parse_unary(self) -> float:
        """Parse unary minus (binds looser than ^)"""
        if self.pos < len(self.tokens):
            op = self.tokens[self.pos][1]
            if op == '-':
                self.pos += 1
                return -self.parse_power()
            elif op == '+':
                self.pos += 1
                return self.parse_power()
        
        return self.parse_primary()
    
    def parse_primary(self) -> float:
        """Parse numbers, variables, and parenthesized expressions"""
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of expression")
        
        token_type, value = self.tokens[self.pos]
        
        if token_type == 'NUM':
            self.pos += 1
            return value
        
        elif token_type == 'VAR':
            var_name = str(value)
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            self.pos += 1
            return float(self.variables[var_name])
        
        elif token_type == 'OP' and value == '(':
            self.pos += 1
            result = self.parse_expression()
            
            if self.pos >= len(self.tokens) or self.tokens[self.pos][1] != ')':
                raise ValueError("Missing closing parenthesis")
            
            self.pos += 1
            return result
        
        else:
            raise ValueError(f"Unexpected token: {token_type} {value}")


def evaluate(expr: str, variables: Optional[dict[str, float]] = None) -> float:
    """Evaluate an arithmetic expression without using eval, exec, ast, or parsing libraries."""
    evaluator = ExpressionEvaluator(expr, variables)
    return evaluator.parse()
