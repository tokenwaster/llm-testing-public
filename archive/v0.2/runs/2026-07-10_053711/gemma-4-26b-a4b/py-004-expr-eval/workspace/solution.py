import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression without using eval, exec, ast, or any parsing library.
    Supports numbers, binary operators (+, -, *, /, %, ^), unary minus, parentheses, and variables.
    """
    if variables is None:
        variables = {}

    def tokenize(expr_str):
        # Remove all whitespace from the expression
        expr_str = "".join(expr_str.split())
        # Regex to match numbers (integers/decimals), variable names, and operators/parentheses
        token_pattern = re.compile(r'(\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\%\^\(\)])')
        tokens = []
        last_end = 0
        for match in token_pattern.finditer(expr_str):
            # If there's a gap between matches, it means there are invalid characters
            if match.start() != last_end:
                raise ValueError("Malformed syntax")
            token = match.group()
            try:
                # Try to convert the token to a float if it looks like a number
                tokens.append(float(token))
            except ValueError:
                tokens.append(token)
            last_end = match.end()

        if last_end != len(expr_str):
            raise ValueError("Malformed syntax")
        return tokens

    class Parser:
        def __init__(self, tokens, variables):
            self.tokens = tokens
            self.variables = variables
            self.pos = 0

        def peek(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def consume(self):
            token = self.peek()
            if token is not None:
                self.pos += 1
            return token

        def get_precedence(self, op):
            # Precedence levels (higher number means higher precedence)
            prec_map = {
                '^': 40,
                '*': 20,
                '/': 20,
                '%': 20,
                '+': 10,
                '-': 10
            }
            return prec_map.get(op, 0)

        def is_right_associative(self, op):
            return op == '^'

        def parse_expression(self, min_prec=0):
            token = self.consume()
            if token is None:
                raise ValueError("Unexpected end of expression")

            # Handle Prefix (Unary) part
            if token == '(':
                val = self.parse_expression(0)
                if self.consume() != ')':
                    raise ValueError("Unbalanced parentheses")
            elif token == '-':  # Unary minus
                # The prompt states unary minus binds looser than '^' (40). 
                # We use precedence 31 so that any operator with prec >= 31 (like '^') is consumed.
                val = -self.parse_expression(31)
            elif isinstance(token, float):
                val = token
            elif isinstance(token, str) and re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
                if token in self.variables:
                    val = float(self.variables[token])
                else:
                    raise ValueError(f"Unknown variable: {token}")
            else:
                raise ValueError("Malformed syntax")

            # Handle Infix part (Binary operators)
            while True:
                op = self.peek()
                if op is None or op == ')':
                    break
                
                prec = self.get_preint_prec(op)
                if prec < min_prec:
                    break

                self.consume()  # Consume the operator
                # For left-associative, we use prec + 1 to stop at same precedence level.
                # For right-associative, we use prec to allow recursive binding.
                next_min_prec = prec + 1 if not self.is_right_associative(op) else prec
                right_val = self.parse_expression(next_min_prec)

                if op == '+': val += right_val
                elif op == '-': val -= right_val
                elif op == '*': val *= right_val
                elif op == '/':
                    if right_val == 0: raise ValueError("Division by zero")
                    val /= right_val
                elif op == '%':
                    if right_val == 0: raise ValueError("Modulo by zero")
                    val %= right_val
                elif op == '^':
                    try:
                        val = val ** right_val
                    except OverflowError:
                        val = float('inf')
                else:
                    raise ValueError(f"Unknown operator: {op}")

            return val

        def get_preint_prec(self, op):
            # Helper to safely get precedence for the loop check
            if isinstance(op, str):
                return self.get_precedence(op)
            return 0

    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    result = parser.parse_expression(0)
    
    # If there are tokens left after parsing the main expression, it's a syntax error (e.g., "2+3)")
    if parser.pos < len(tokens):
        raise ValueError("Malformed syntax")
        
    return float(result)
