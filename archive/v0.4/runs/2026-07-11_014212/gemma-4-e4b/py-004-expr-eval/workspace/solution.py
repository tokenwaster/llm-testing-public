import re
from typing import Dict, Optional

class Token:
    """Represents a recognized token."""
    def __init__(self, type: str, value: any = None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

class Lexer:
    """Tokenizes the input expression."""
    TOKEN_SPECIFICATION = [
        ('NUMBER', r'\d+(\.\d*)?'),  # Integers and decimals
        ('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*'), # Variable names
        ('OP', r'[\+\-\*/%^()]'),    # Operators and parentheses (grouped for simplicity)
        ('SKIP', r'\s+'),           # Whitespace to skip
        ('MISMATCH', r'.'),         # Any other character
    ]

    def __init__(self, text: str):
        self.text = text
        self.tokens = self._tokenize()

    def _tokenize(self) -> list[Token]:
        tokens = []
        token_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.TOKEN_SPECIFICATION if pair[0] != 'SKIP')
        
        for match in re.finditer(token_regex, self.text):
            token_type = None
            value = None
            
            # Determine the type and value based on which group matched
            for name, pattern in self.TOKEN_SPECIFICATION:
                if name == 'SKIP': continue
                
                match_obj = re.search(pattern, match.group(0))
                if match_obj:
                    token_type = name
                    value = match_obj.group(0)
                    break

            if token_type:
                tokens.append(Token(token_type, value))
        
        # Add a sentinel EOF token
        tokens.append(Token('EOF', None))
        return tokens


class Parser:
    """Parses the token stream using recursive descent."""
    def __init__(self, tokens: list[Token], variables: Optional[Dict[str, float]]):
        self.tokens = tokens
        self.variables = variables if variables is not None else {}
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected_type: Optional[str] = None) -> Token:
        token = self.tokens[self.pos]
        if expected_type and token.type != expected_type:
            raise ValueError(f"Syntax Error: Expected {expected_type} but found {token.type}")
        self.pos += 1
        return token

    def parse(self) -> float:
        """Entry point for parsing."""
        result = self._parse_expression()
        # Ensure we consumed all meaningful tokens (up to EOF)
        if self.peek().type != 'EOF':
             raise ValueError("Malformed syntax: Unexpected tokens remaining.")
        return result

    def _is_operator(self, token: Token) -> bool:
        """Checks if a token is an arithmetic operator."""
        op_types = {'OP'}
        return token.type in op_types and token.value in ['+', '-', '*', '/', '%', '^']

    # --- Precedence Levels ---

    def _parse_primary(self) -> float:
        """Handles numbers, variables, parentheses, and unary minus."""
        token = self.peek()

        if token.type == 'NUMBER':
            self.consume('NUMBER')
            return float(token.value)
        
        elif token.type == 'VARIABLE':
            var_name = self.consume('VARIABLE').value
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable '{var_name}'")
            return self.variables[var_name]

        elif token.type == 'OP' and token.value == '(':
            self.consume('OP') # Consume '('
            result = self._parse_expression()
            self.consume('OP', ')') # Expect ')'
            return result

        # Handle Unary Minus (Prefix)
        elif token.type == 'OP' and token.value == '-':
            # Check if '-' is unary: start of expression, after '(', or after another operator
            is_unary = (self.pos == 0 or self.tokens[self.pos-1].value in ['(', '+', '-', '*', '/', '%', '^'])
            if is_unary:
                self.consume('OP') # Consume '-'
                # Recursively parse the next primary factor, which might also start with unary minus
                return -self._parse_primary()
            else:
                # If it's not unary, let the calling function handle it as binary subtraction
                pass 

        raise ValueError(f"Syntax Error: Unexpected token when expecting primary expression: {token}")


    def _parse_factor(self) -> float:
        """Handles exponentiation (Right Associative: ^). Precedence level 3."""
        # Start by parsing the highest precedence item (primary/unary)
        result = self._parse_primary()

        while self.peek().type == 'OP' and self.peek().value == '^':
            self.consume('OP') # Consume '^'
            # Exponentiation is right-associative, so we recursively call _parse_factor
            right = self._parse_factor() 
            result *= (right ** result) # Note: Python handles float exponentiation correctly

        return result


    def _parse_term(self) -> float:
        """Handles multiplication, division, modulo (Left Associative). Precedence level 2."""
        # Start by parsing the factor
        result = self._parse_factor()

        while self.peek().type == 'OP' and self.peek().value in ['*', '/', '%']:
            op_token = self.consume('OP')
            right = self._parse_factor()

            if op_token.value == '*':
                result *= right
            elif op_token.value == '/':
                if right == 0: raise ValueError("Division by zero")
                result /= right
            elif op_token.value == '%':
                if right == 0: raise ValueError("Modulo by zero")
                result %= right
        return result


    def _parse_expression(self) -> float:
        """Handles addition and subtraction (Left Associative). Precedence level 1."""
        # Start by parsing the term
        result = self._parse_term()

        while self.peek().type == 'OP' and self.peek().value in ['+', '-']:
            op_token = self.consume('OP')
            right = self._parse_term()

            if op_token.value == '+':
                result += right
            elif op_token.value == '-':
                result -= right
        return result


def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluates an arithmetic expression without using eval/exec/ast.
    Implements a custom tokenizer and recursive descent parser.
    """
    if not expr.strip():
        raise ValueError("Input expression cannot be empty.")

    # 1. Tokenization
    lexer = Lexer(expr)
    tokens = lexer.tokens

    # 2. Parsing and Evaluation
    parser = Parser(tokens, variables)
    return parser.parse()


if __name__ == '__main__':
    # Example Usage (for testing purposes - not part of the final output)
    variables_test = {'a': 2.0, 'b': 3.0}

    print("--- Basic Tests ---")
    try:
        print(f"1 + 2 * 3: {evaluate('1 + 2 * 3')}") # Expected: 7.0
        print(f"(1 + 2) * 3: {evaluate('(1 + 2) * 3')}") # Expected: 9.0
    except ValueError as e:
        print(f"Error during basic test: {e}")

    print("\n--- Exponentiation (Right Associative) ---")
    try:
        # 2^3^2 = 2^(3^2) = 2^9 = 512
        result_pow = evaluate('2^3^2')
        print(f"2^3^2: {result_pow}") # Expected: 512.0
    except ValueError as e:
        print(f"Error during exponentiation test: {e}")

    print("\n--- Unary Minus Tests ---")
    try:
        # -3 + (-4 * 2) = -3 - 8 = -11
        result_unary = evaluate('-3 + (-4 * 2)')
        print(f"-3 + (-4 * 2): {result_unary}") # Expected: -11.0
    except ValueError as e:
        print(f"Error during unary test: {e}")

    try:
        # --3 = 3
        result_double_neg = evaluate('--3')
        print(f"--3: {result_double_neg}") # Expected: 3.0
    except ValueError as e:
        print(f"Error during double negation test: {e}")

    print("\n--- Variables and Mixed Ops ---")
    try:
        # a * (b + 1) = 2 * (3 + 1) = 8
        result_var = evaluate('a * (b + 1)', variables=variables_test)
        print(f"a * (b + 1): {result_var}") # Expected: 8.0
    except ValueError as e:
        print(f"Error during variable test: {e}")

    print("\n--- Error Handling Tests ---")
    # Division by zero
    try:
        evaluate("1 / (2 - 2)")
    except ValueError as e:
        print(f"Caught expected error (Div/Mod Zero): {e}")

    # Unknown variable
    try:
        evaluate("x + 1")
    except ValueError as e:
        print(f"Caught expected error (Unknown Variable): {e}")

    # Unbalanced parentheses
    try:
        evaluate("(1 + 2")
    except ValueError as e:
        print(f"Caught expected error (Unbalanced Parens): {e}")
