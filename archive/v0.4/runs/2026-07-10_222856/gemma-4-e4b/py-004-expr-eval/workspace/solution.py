import re
from typing import Dict, List, Tuple

class ExpressionEvaluator:
    """
    Evaluates arithmetic expressions without using eval, exec, or ast.
    Implements custom tokenization and recursive descent parsing logic.
    """

    def __init__(self, expr: str, variables: Dict[str, float] | None = None):
        self.expr = expr
        self.variables = variables if variables is not None else {}
        self.tokens = self._tokenize(expr)
        self.pos = 0

    def _tokenize(self, expr: str) -> List[str]:
        """
        Tokenizes the input string into numbers, variables, operators, and parentheses.
        Handles whitespace removal implicitly.
        """
        # Regex pattern to match tokens:
        # 1. Numbers (integers or decimals): \d+(\.\d*)?|\.\d+
        # 2. Variables: [a-zA-Z_][a-zA-Z0-9_]*
        # 3. Operators/Parentheses: [+\-*/%^()]
        token_specification = r'''
            \s+ |                          # Whitespace (ignored)
            (\d+\.\d*|\.\d+|\d+) |         # Numbers
            ([a-zA-Z_][a-zA-Z0-9_]*) |    # Variables
            ([+\-*/%^()]|[\+\-\*\/%\^\(\)]) # Operators and Parentheses (must handle single chars)
        '''
        
        tokens = []
        cursor = 0
        while cursor < len(expr):
            match = re.match(token_specification, expr[cursor:], re.VERBOSE)
            if not match:
                # Should not happen if regex is comprehensive, but good safeguard
                raise ValueError("Malformed syntax near position " + str(cursor))

            token = match.group(0).strip()
            if token and not token.isspace():
                tokens.append(token)
            
            cursor += len(match.group(0))
        
        return tokens

    def _peek(self) -> str | None:
        """Returns the next token without advancing position."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self, expected_type: str = None) -> str:
        """Consumes the current token and advances position."""
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of expression.")
        token = self.tokens[self.pos]
        self.pos += 1
        
        if expected_type and token != expected_type:
            raise ValueError(f"Expected '{expected_type}' but found '{token}'.")
        return token

    def _is_operator(self, token: str) -> bool:
        """Checks if a token is a binary operator."""
        return token in ['+', '-', '*', '/', '%', '^']

    def _is_unary_context(self) -> bool:
        """
        Determines if the current position allows for a unary minus/plus.
        This happens at the start, or after an opening parenthesis, 
        or immediately after another binary operator.
        """
        if self.pos == 0:
            return True
        
        # Check previous token type (requires looking back)
        prev_token = self.tokens[self.pos - 1]
        
        # Unary context if previous was an opening parenthesis or a binary operator
        return prev_token in ['(', '+', '-', '*', '/', '%', '^']

    def _parse_number(self, token: str) -> float:
        """Converts a numeric string token to float."""
        try:
            return float(token)
        except ValueError:
            # Should be caught by tokenizer, but safe check anyway
            raise ValueError(f"Invalid number format: {token}")

    def _parse_variable(self, token: str) -> float:
        """Resolves a variable name using the provided dictionary."""
        if token not in self.variables:
            raise ValueError(f"Unknown variable '{token}'")
        return self.variables[token]

    def _parse_primary(self) -> float:
        """Handles numbers, variables, and parenthesized expressions."""
        token = self._peek()
        if token is None:
            raise ValueError("Unexpected end of expression.")

        # 1. Parentheses
        if token == '(':
            self._consume('(')
            result = self._parse_expression()
            self._consume(')') # Expect closing parenthesis
            return result

        # 2. Unary Minus/Plus Handling (Highest precedence, binds looser than ^)
        is_unary = self._is_unary_context() and self._peek() in ['+', '-']
        
        if is_unary:
            op = self._consume() # Consume '+' or '-'
            # If it's a unary plus, we just proceed with the next primary value.
            if op == '+':
                return self._parse_primary() 

            # It must be a unary minus
            value = self._parse_primary()
            return -value
        
        # 3. Numbers or Variables
        elif token.replace('.', '', 1).isdigit(): # Check if it looks like a number
            self._consume()
            return self._parse_number(token)
        elif re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', token): # Variable check
            self._consume()
            return self._parse_variable(token)
        else:
            # If it's an operator or closing parenthesis here, it's a syntax error.
            raise ValueError(f"Unexpected token in primary expression: {token}")

    def _parse_power(self) -> float:
        """Handles exponentiation (^) - Right-associative."""
        result = self._parse_primary()
        
        while self._peek() == '^':
            # Consume the right-associative operator
            self._consume('^') 
            # Recursively call to handle right associativity: a ^ (b ^ c)
            right_operand = self._parse_power() 
            result *= (right_operand ** result) # Note: Python's built-in ** handles float exponents correctly
        return result

    def _parse_term(self) -> float:
        """Handles multiplication (*), division (/), and modulo (%). Left-associative."""
        result = self._parse_power()
        
        while self._peek() in ['*', '/', '%']:
            op = self._consume()
            right_operand = self._parse_power()

            if op == '*':
                result *= right_operand
            elif op == '/':
                if right_operand == 0.0:
                    raise ValueError("Division by zero.")
                result /= right_operand
            elif op == '%':
                if right_operand == 0.0:
                    raise ValueError("Modulo by zero.")
                # Python's % operator handles floats correctly for modulo arithmetic
                result = result % right_operand
        return result

    def _parse_expression(self) -> float:
        """Handles addition (+) and subtraction (-) - Left-associative."""
        result = self._parse_term()
        
        while self._peek() in ['+', '-']:
            op = self._consume()
            right_operand = self._parse_term()

            if op == '+':
                result += right_operand
            elif op == '-':
                result -= right_operand
        return result

    def evaluate(self) -> float:
        """Main entry point for evaluation."""
        try:
            # Start parsing from the lowest precedence level (addition/subtraction)
            result = self._parse_expression()
            
            # Check if all tokens were consumed
            if self.pos < len(self.tokens):
                raise ValueError(f"Malformed syntax: unexpected token '{self.tokens[self.pos]}' remaining.")
            
            return result

        except IndexError as e:
            # Catch internal parsing errors related to position/index out of bounds
            raise ValueError("Malformed syntax or unbalanced parentheses.") from e


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates arithmetic expressions using custom parser logic.
    """
    if not expr.strip():
        # Handle empty input gracefully if required, though usually an error is better.
        raise ValueError("Input expression cannot be empty.")

    evaluator = ExpressionEvaluator(expr, variables)
    return evaluator.evaluate()


# Example usage (for testing purposes, removed in final output):
if __name__ == '__main__':
    print("--- Basic Tests ---")
    try:
        print(f"3 + 4 * 2 = {evaluate('3 + 4 * 2')}") # Expected: 11.0
        print(f"(3 + 4) * 2 = {evaluate('(3 + 4) * 2')}") # Expected: 14.0
    except ValueError as e:
        print(f"Error during basic test: {e}")

    print("\n--- Precedence and Associativity Tests ---")
    try:
        # Exponentiation (Right-associative): 2 ^ (3 ^ 2) = 512
        print(f"2^3^2 = {evaluate('2^3^2')}") 
        # Standard multiplication/division precedence
        print(f"6 / 2 * 3 = {evaluate('6 / 2 * 3')}") # Expected: 9.0 (Left-associative)
    except ValueError as e:
        print(f"Error during precedence test: {e}")

    print("\n--- Unary Minus Tests ---")
    try:
        # Simple unary minus
        print(f"-5 + 3 = {evaluate('-5 + 3')}") # Expected: -2.0
        # Unary minus binding looser than ^: -(2^2) = -4
        print(f"-(2^2) = {evaluate('-(2^2)')}") # Expected: -4.0
        # Repeated unary minus: --3 = 3
        print(f"--3 * 5 = {evaluate('--3 * 5')}") # Expected: 15.0
    except ValueError as e:
        print(f"Error during unary test: {e}")

    print("\n--- Variable Tests ---")
    vars_dict = {"x": 2.0, "y": 3.0}
    try:
        # x * (y + 1)
        result = evaluate("x * (y + 1)", variables=vars_dict)
        print(f"x * (y + 1) = {result}") # Expected: 8.0
    except ValueError as e:
        print(f"Error during variable test: {e}")

    print("\n--- Error Tests ---")
    # Division by zero
    try:
        evaluate("5 / (3 - 3)")
    except ValueError as e:
        print(f"Caught expected error (Div/Mod Zero): {e}")

    # Unbalanced parentheses
    try:
        evaluate("(5 + 2")
    except ValueError as e:
        print(f"Caught expected error (Unbalanced Parens): {e}")
        
    # Unknown variable
    try:
        evaluate("a * z")
    except ValueError as e:
        print(f"Caught expected error (Unknown Variable): {e}")

    # Malformed syntax (missing operator)
    try:
        evaluate("5 (3)")
    except ValueError as e:
        print(f"Caught expected error (Malformed Syntax): {e}")
