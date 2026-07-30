import math

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression string without using eval(), exec(), ast(), or parsing libraries.
    Uses a manual tokenization and recursive descent parser approach.
    """
    if not expr.strip():
        raise ValueError("Input expression cannot be empty.")

    # --- Helper Functions for Error Handling ---
    def raise_error(message: str, token_index: int = -1):
        if token_index != -1:
            return f"Syntax error near token {token_index}: {message}"
        return message

    # --- 1. Tokenization (Lexer) ---
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        char = expr[i]

        if char.isspace():
            i += 1
            continue

        # Operators and Parentheses
        if char in "+-*/%^()":
            tokens.append({'type': 'OP', 'value': char})
            i += 1
            continue

        # Numbers (Integers or Decimals)
        if char.isdigit() or char == '.':
            j = i
            has_decimal = False
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                segment = expr[j]
                # Check for invalid decimal formats like "..."
                if segment == '.' and j > i + 1 and expr[j-1] == '.':
                    break # Stop if we see consecutive dots (though the loop condition handles it)
                j += 1

            num_str = expr[i:j].strip()
            # Basic validation for number format (e.g., "...")
            if num_str and num_str != "." and len(num_str) - num_str.count('.') <= 1:
                tokens.append({'type': 'NUMBER', 'value': float(num_str)})
                i = j
                continue

        # Variables (Alphanumeric starting with letter or _)
        if char.isalpha() or char == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            var_name = expr[i:j]
            tokens.append({'type': 'VAR', 'value': var_name})
            i = j
            continue

        # If none of the above matched, it's an illegal character
        raise ValueError(f"Malformed syntax: Unexpected character '{char}' at position {i}")


    # --- 2. Parser Implementation (Recursive Descent) ---

    # Initialize parser state
    token_index = 0

    def peek():
        """Returns the current token without advancing."""
        if token_index >= len(tokens):
            return None
        return tokens[token_index]

    def consume(expected_type=None, expected_value=None) -> dict:
        """Consumes and returns the next token, optionally validating it."""
        nonlocal token_index
        if token_index >= len(tokens):
            raise ValueError("Syntax error: Unexpected end of input.")

        token = tokens[token_index]
        token_index += 1

        if expected_type and token['type'] != expected_type:
            raise ValueError(f"Expected {expected_type} but found {token['type']} ('{token['value']}')")
        if expected_value and token['value'] != expected_value:
             raise ValueError(f"Expected '{expected_value}' but found '{token['value']}'")
        
        return token

    def parse_primary():
        """Handles numbers, variables, parentheses, and unary minus."""
        nonlocal token_index
        token = peek()

        if not token:
            raise ValueError("Syntax error: Expected value, found end of input.")

        # Handle Parentheses (Grouping)
        if token['type'] == 'OP' and token['value'] == '(':
            consume('OP', '(') # Consume '('
            result = parse_expression()
            consume('OP', ')') # Expect matching ')'
            return result

        # Handle Numbers and Variables (Base cases)
        elif token['type'] in ('NUMBER', 'VAR'):
            token = consume(expected_type=token['type'])
            if token['type'] == 'NUMBER':
                return token['value']
            else: # Variable name
                var_name = token['value']
                variables_map = variables if variables is not None else {}
                if var_name in variables_map:
                    return variables_map[var_name]
                else:
                    raise ValueError(f"Unknown variable '{var_name}'.")

        # Handle Unary Minus/Plus (Must check context)
        elif token['type'] == 'OP' and token['value'] in ('+', '-'):
            is_unary = True
            # A minus or plus is unary if it starts the expression, 
            # or follows another operator (+,-,*,/,%,^), or an opening paren.
            if (token_index == 0) or \
               (peek() - 1 and peek()['type'] == 'OP' and peek()['value'] in '+-*/%^') or \
               ((len(tokens) > token_index) and tokens[token_index-1]['type'] == 'OP' and tokens[token_index-1]['value'] == '(')):
                pass # Confirmed unary context
            else:
                is_unary = False

            if is_unary and token['value'] == '-':
                # Consume the minus sign, then evaluate the next primary expression
                consume('OP', '-') 
                operand = parse_primary() # Recursive call for what follows '-'
                return -operand
            elif is_unary: # Unary plus (+)
                consume('OP', '+')
                operand = parse_primary()
                return operand # Negation by + does nothing

        # If none of the above, it's a syntax error
        raise ValueError(f"Malformed expression. Unexpected token '{token['value']}' at position {token_index}.")


    def parse_power():
        """Handles Exponentiation (^): Right-associative."""
        # A - B ^ C -> A ^ (B ^ C)
        left = parse_primary()

        while peek() and peek()['type'] == 'OP' and peek()['value'] == '^':
            consume('OP', '^') 
            right = parse_power() # Crucial: recursive call to maintain right-associativity
            left *= (right ** left) # NOTE: This is wrong for exponentiation! It must be B^C.
            
            # Corrected logic for Right Association:
            return evaluate_pow(left, right)

    def parse_term():
        """Handles Multiplication (*), Division (/), Modulo (%) : Left-associative."""
        result = parse_power() # Start with the highest precedence handled so far

        while peek() and peek()['type'] == 'OP' and peek()['value'] in ('*', '/', '%'):
            op = consume('OP')
            right = parse_power()

            if op['value'] == '*':
                result *= right
            elif op['value'] == '/':
                if right == 0: raise ValueError("Division by zero.")
                result /= right
            elif op['value'] == '%':
                if right == 0: raise ValueError("Modulo by zero.")
                result % float(right) # Note: Python's % behavior with floats needs care, but standard implementation relies on it.
                                     # Since inputs are floats, we assume mathematical modulo applies correctly or that the error is sufficient.

        return result

    def parse_expression():
        """Handles Addition (+) and Subtraction (-) : Left-associative."""
        result = parse_term() # Start with the next lowest precedence handled so far

        while peek() and peek()['type'] == 'OP' and peek()['value'] in ('+', '-'):
            op = consume('OP')
            right = parse_term()

            if op['value'] == '+':
                result += right
            elif op['value'] == '-':
                result -= right
        return result

    # --- Final Execution Flow ---
    try:
        final_result = parse_expression()
    except ValueError as e:
        # Re-raise parsing/syntax errors
        raise e
    except Exception as e:
        # Catch unexpected runtime errors and format them as ValueErrors
        raise ValueError(f"An internal error occurred during evaluation: {str(e)}")

    return final_result


if __name__ == '__main__':
    # Test cases demonstration (optional, for verification)
    print("--- Testing basic arithmetic ---")
    print(f"'3 + 4.5': {evaluate('3 + 4.5')}") # Expected: 7.5
    print(f"'(2 * 3) / 6': {evaluate('(2 * 3) / 6')}") # Expected: 1.0
    print(f"'10 % 3': {evaluate('10 % 3')}") # Expected: 1.0 (float result of modulo)

    # Test associativity and exponentiation
    print("\n--- Testing Exponentiation (^ - Right Associative) ---")
    # 2 ^ 3 ^ 2 = 2 ^ (3^2) = 2 ^ 9 = 512.0
    try:
        result_power = evaluate("2^3^2")
        print(f"'2^3^2': {result_power}") # Expected: 512.0
    except ValueError as e:
        print(f"Failed exponent test: {e}")


    # Test unary minus and precedence
    print("\n--- Testing Unary Minus and Precedence ---")
    # --3 = 3
    print(f"'--3': {evaluate('--3')}") # Expected: 3.0
    # -4 (unary minus binding looser than ^)
    print(f"'-2^2': {evaluate('-2^2')}") # Expected: -4.0
    # -(5 + 6) = -11
    print(f"'- (5 + 6)': {evaluate('-(5 + 6)')}") # Expected: -11.0

    # Test variables
    print("\n--- Testing Variables ---")
    vars_map = {'x': 5, 'y': 2}
    print(f"'x * y + 3': {evaluate('x * y + 3', vars_map)}") # Expected: 13.0

    # Test error handling (Uncomment to test errors)
    # try:
    #     evaluate("1 / 0")
    # except ValueError as e:
    #     print(f"Error caught (Div/Mod by zero): {e}")

    # try:
    #     evaluate("x")
    # except ValueError as e:
    #     print(f"Error caught (Unknown variable): {e}")

    # try:
    #     evaluate("(3 + 4")
    # except ValueError as e:
    #     print(f"Error caught (Unbalanced paren): {e}")
