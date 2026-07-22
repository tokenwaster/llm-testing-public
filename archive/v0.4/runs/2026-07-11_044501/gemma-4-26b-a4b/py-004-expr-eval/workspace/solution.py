import re

class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.variables = variables if variables is not None else {}
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected=None):
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if expected is notly_none and token != expected:
            # This check is only used for parentheses in our implementation
            pass 
        self.pos += 1
        return token

    def parse_expression(self):
        """Handles binary + and - (left-associative, lowest precedence)."""
        node = self.parse_term()
        while self.peek() in ('+', '-'):
            op = self.consume()
            right = self.parse_term()
            node = ('binop', op, node, right)
        return node

    def parse_term(self):
        """Handles binary *, /, and % (left-associative)."""
        node = self.parse_unary()
        while self.peek() in ('*', '/', '%'):
            op = self.consume()
            right = self.parse_unary()
            node = ('binop', op, node, right)
        return node

    def parse_unary(self):
        """Handles unary minus (can be repeated)."""
        if self.peek() == '-':
            self.consume()
            operand = self.parse_unary()
            return ('unary', '-', operand)
        else:
            return self.parse_exponentiation()

    def parse_exponentiation(self):
        """Handles binary ^ (right-associative, higher precedence than unary minus)."""
        node = self.parse_atom()
        if self.peek() == '^':
            op = self.consume()
            # Right-associativity is achieved by calling parse_exponentiation recursively
            right = self.parse_exponentiation()
            node = ('binop', op, node, right)
        return node

    def parse_atom(self):
        """Handles numbers, variables, and parentheses (highest precedence)."""
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        if token == '(':
            self.consume('(')
            node = self.parse_expression()
            if self.peek() != ')':
                raise ValueError("Unbalanced parentheses")
            self.consume(')')
            return node
        elif isinstance(token, float):
            return ('num', self.consume())
        elif isinstance(token, str) and re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
            var_name = self.consume()
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return ('var', var_name)
        else:
            raise ValueError(f"Malformed syntax: unexpected token {token}")

    def evaluate(self, node):
        """Recursively evaluates the parsed expression tree."""
        if node[0] == 'num':
            return float(node[1])
        elif node[0] == 'var':
            return float(self.variables[node[1]])
        elif node[0] == 'unary':
            val = self.evaluate(node[2])
            return -val
        elif node[0] == 'binop':
            _, op, left_node, right_node = node
            left = self.evaluate(left_node)
            right = self.evaluate(right_node)
            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/':
                if right == 0: raise ValueError("Division by zero")
                return left / right
            if op == '%':
                if right == 0: raise ValueError("Modulo by zero")
                return left % right
            if op == '^': return left ** right
        raise ValueError("Invalid expression tree")

def tokenize(expr):
    """Converts the input string into a list of tokens."""
    token_pattern = re.compile(r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\%\^\(\)]')
    tokens = []
    last_end = 0
    for match in token_pattern.finditer(expr):
        # Check for invalid characters between tokens
        if expr[last_end:match.start()].strip():
            raise ValueError("Malformed syntax: invalid character detected")
        
        val = match.group()
        # Try to parse as float if it's a number pattern
        if re.match(r'\d+\.\d+|\d+', val):
            tokens.append(float(val))
        else:
            tokens.append(val)
        last_end = match.end()
    
    # Check for invalid characters after the last token
    if expr[last_end:].strip():
        raise ValueError("Malformed syntax: invalid character detected")
    return tokens

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluates an arithmetic expression string."""
    try:
        tokens = tokenize(expr)
        if not tokens:
            raise ValueError("Empty expression")
        
        parser = Parser(tokens, variables)
        tree = parser.parse_expression()
        
        # Ensure all tokens were consumed (detects trailing garbage)
        if parser.pos < len(tokens):
            raise ValueError("Malformed syntax: extra tokens found")
            
        return float(parser.evaluate(tree))
    except (ValueError, IndexError, TypeError, ZeroDivisionError) as e:
        # Re-raise ValueErrors specifically for the required error type
        if isinstance(e, ValueError):
            raise e
        raise ValueError(str(e))
