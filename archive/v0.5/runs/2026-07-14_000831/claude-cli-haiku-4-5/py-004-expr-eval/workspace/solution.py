def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    # Tokenizer
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
        elif expr[i] in '()+-*/%^':
            tokens.append(expr[i])
            i += 1
        elif expr[i].isdigit():
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        else:
            raise ValueError(f"Invalid character: {expr[i]}")
    
    # Parser
    class Parser:
        def __init__(self, tokens, variables):
            self.tokens = tokens
            self.variables = variables
            self.current_idx = 0
        
        def peek(self):
            if self.current_idx < len(self.tokens):
                return self.tokens[self.current_idx]
            return None
        
        def consume(self):
            token = self.peek()
            self.current_idx += 1
            return token
        
        def expression(self):
            return self.additive()
        
        def additive(self):
            left = self.multiplicative()
            while self.peek() in ['+', '-']:
                op = self.consume()
                right = self.multiplicative()
                if op == '+':
                    left = left + right
                else:
                    left = left - right
            return left
        
        def multiplicative(self):
            left = self.unary()
            while self.peek() in ['*', '/', '%']:
                op = self.consume()
                right = self.unary()
                if op == '*':
                    left = left * right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    left = left / right
                else:
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            return left
        
        def unary(self):
            if self.peek() == '-':
                self.consume()
                return -self.unary()
            return self.exponential()
        
        def exponential(self):
            left = self.atom()
            if self.peek() == '^':
                self.consume()
                right = self.exponential()
                return left ** right
            return left
        
        def atom(self):
            token = self.peek()
            if token == '(':
                self.consume()
                result = self.expression()
                if self.consume() != ')':
                    raise ValueError("Unbalanced parentheses")
                return result
            elif token and token[0].isdigit():
                self.consume()
                try:
                    return float(token)
                except ValueError:
                    raise ValueError(f"Invalid number: {token}")
            elif token and (token[0].isalpha() or token[0] == '_'):
                self.consume()
                if token not in self.variables:
                    raise ValueError(f"Unknown variable: {token}")
                return self.variables[token]
            else:
                raise ValueError(f"Unexpected token: {token}")
    
    parser = Parser(tokens, variables)
    result = parser.expression()
    
    if parser.current_idx != len(tokens):
        raise ValueError("Unexpected tokens after expression")
    
    return result
