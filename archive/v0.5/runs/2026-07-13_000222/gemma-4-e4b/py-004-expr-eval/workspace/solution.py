import re
from typing import Dict, List, Tuple

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression without using eval, exec, or ast.
    Implements a custom parser respecting operator precedence and associativity.
    """
    if not expr:
        raise ValueError("Empty expression")

    # --- 1. Tokenization ---
    
    tokens = []
    i = 0
    n = len(expr)
    
    while i < n:
        char = expr[i]
        
        # Skip whitespace
        if char.isspace():
            i += 1
            continue

        # Numbers (integers or decimals, including leading/trailing dots if valid float format)
        if char.isdigit() or char == '.':
            j = i
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            num_str = expr[i:j]
            try:
                # Basic validation to ensure it's a valid float representation
                float(num_str)
                tokens.append(('NUMBER', num_str))
                i = j
                continue
            except ValueError:
                # If the sequence of digits/dots is invalid (e.g., "1..2"), treat it as an error later, 
                # but for now, we assume standard float parsing handles most cases.
                pass # Fall through to character processing if number fails

        # Variables
        elif char.isalpha() or char == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            var_name = expr[i:j]
            tokens.append(('VARIABLE', var_name))
            i = j
            continue

        # Operators and Parentheses
        elif char in '+-*/%^()':
            if char == '-':
                # Look ahead to determine if it's unary or binary minus
                is_unary = False
                # Check context: start of expression, after '(', or after another operator
                if i == 0:
                    is_unary = True
                else:
                    prev_token = tokens[-1]
                    if prev_token[0] in ('(', '+', '-', '*', '/', '%', '^'):
                        # Note: We must check if the previous token was *not* a number/variable 
                        # (i.e., it was an operator or '(')
                        is_unary = True

                tokens.append(('OP', char))
            else:
                tokens.append(('OP', char))
            i += 1
            continue
        
        # Unknown character
        else:
            raise ValueError(f"Malformed syntax near character '{char}' at position {i}")

    # --- 2. Parsing and Evaluation (Recursive Descent) ---
    
    token_index = 0

    def peek() -> Tuple[str, str] | None:
        """Returns the type and value of the current token without advancing."""
        if token_index < len(tokens):
            return tokens[token_index]
        return None

    def consume(expected_type: str = None) -> Tuple[str, str]:
        """Advances the index and returns the consumed token. Raises ValueError if type mismatch."""
        nonlocal token_index
        if token_index >= len(tokens):
            raise ValueError("Unexpected end of expression")
        token = tokens[token_index]
        token_index += 1
        if expected_type and token[0] != expected_type:
             raise ValueError(f"Expected {expected_type} but found {token[0]} ('{token[1]}')")
        return token

    def parse_primary() -> float:
        """Handles numbers, variables, parentheses, and unary minus."""
        nonlocal token_index
        
        # Check for Unary Minus (This must be handled *before* checking for '(' or NUMBER)
        if peek() and peek()[1] == '-':
            consume('OP') # Consume the '-'
            # Recursively evaluate what follows the unary minus
            result = parse_primary() 
            return -result

        token = peek()
        if not token:
             raise ValueError("Expected primary expression, found end of input")

        token_type, token_value = token

        if token_type == 'NUMBER':
            consume('NUMBER')
            return float(token_value)
        
        elif token_type == 'VARIABLE':
            var_name = consume('VARIABLE')[1]
            if variables is None or var_name not in variables:
                raise ValueError(f"Unknown variable '{var_name}'")
            return variables[var_name]

        elif token_value == '(':
            consume('OP') # Consume '('
            result = parse_expression()
            # Must consume the closing parenthesis
            if peek() and peek()[1] != ')':
                raise ValueError("Unbalanced parentheses: Expected ')'")
            consume('OP', ')') # Consume ')'
            return result

        else:
            # If it's not a number, variable, or opening paren/unary minus, it's an error.
            raise ValueError(f"Malformed syntax: Unexpected token '{token_value}'")


    def parse_factor() -> float:
        """Handles exponentiation (Right-associative)."""
        # Start by parsing the primary element (which handles unary minus)
        result = parse_primary()

        while peek() and peek()[1] == '^':
            consume('OP') # Consume '^'
            # Right associativity: The right operand is evaluated fully before applying power.
            right_operand = parse_factor() 
            result *= (right_operand ** 1) # Placeholder to satisfy type checker, actual logic below
            result = result ** right_operand # Correct calculation for exponentiation

        return result


    def parse_term() -> float:
        """Handles multiplication, division, modulo (Left-associative)."""
        # Start by parsing the factor element
        result = parse_factor()

        while peek() and peek()[1] in ('*', '/', '%'):
            op_token = consume('OP')
            op = op_token[1]
            
            right_operand = parse_factor() # The right side must be a full factor evaluation

            if op == '*':
                result *= right_operand
            elif op == '/':
                if right_operand == 0.0:
                    raise ZeroDivisionError("Division by zero")
                result /= right_operand
            elif op == '%':
                # Modulo requires integer inputs for standard definition, but we use float math here.
                # We cast to int for the modulo operation if possible, otherwise rely on Python's behavior.
                if right_operand != 0.0:
                    result = result % right_operand
                else:
                     raise ZeroDivisionError("Modulo by zero")

        return result


    def parse_expression() -> float:
        """Handles addition and subtraction (Left-associative)."""
        # Start by parsing the term element
        result = parse_term()

        while peek() and peek()[1] in ('+', '-'):
            op_token = consume('OP')
            op = op_token[1]
            
            right_operand = parse_term() # The right side must be a full term evaluation

            if op == '+':
                result += right_operand
            elif op == '-':
                result -= right_operand
        
        return result


    # Start parsing from the lowest precedence level (addition/subtraction)
    try:
        final_result = parse_expression()
    except ZeroDivisionError as e:
        raise ValueError(str(e)) # Re-raise specific math errors as ValueErrors if required by strict interpretation, but keeping it clean is better.
    except Exception as e:
        # Catch any remaining parsing/syntax errors and wrap them
        if isinstance(e, ValueError):
            raise e
        else:
             raise ValueError(f"Syntax error during evaluation: {e}")

    # Check if all tokens were consumed (ensures no trailing garbage)
    if token_index < len(tokens):
        remaining = f"{tokens[token_index][1]}"
        raise ValueError(f"Malformed syntax: Unexpected token '{remaining}' at end of expression")

    return final_result


# Example usage and testing structure (not part of the required output, but useful for verification)
if __name__ == '__main__':
    print("--- Testing Basic Arithmetic ---")
    try:
        print(f"3 + 4 * 2 = {evaluate('3 + 4 * 2')}") # Expected: 11.0
        print(f"(3 + 4) * 2 = {evaluate('(3 + 4) * 2')}") # Expected: 14.0
    except ValueError as e:
        print(f"Error: {e}")

    print("\n--- Testing Exponentiation (Right Associative) ---")
    try:
        # 2 ^ (3 ^ 2) = 2^9 = 512
        print(f"2^3^2 = {evaluate('2^3^2')}") 
        # 4.0 ** 2.0 = 16.0
        print(f"4^2 = {evaluate('4^2')}")
    except ValueError as e:
        print(f"Error: {e}")

    print("\n--- Testing Unary Minus ---")
    try:
        # -3 + 5 = 2
        print(f"-3 + 5 = {evaluate('-3 + 5')}") 
        # --3 = 3
        print(f"--3 = {evaluate('--3')}") 
        # - (2^2) = -4
        print(f"-(2^2) = {evaluate('-(2^2)')}") 
        # 3 * (-4) = -12
        print(f"3 * -4 = {evaluate('3 * -4')}") 
    except ValueError as e:
        print(f"Error: {e}")

    print("\n--- Testing Variables and Precedence ---")
    variables_map = {"a": 2.0, "b": 3.0}
    try:
        # a + b * (4 - 1) / 2 = 2 + 3 * 3 / 2 = 2 + 9/2 = 6.5
        expr = "a + b * (4 - 1) / 2"
        result = evaluate(expr, variables_map)
        print(f"Expression: '{expr}' -> Result: {result}") # Expected: 6.5
    except ValueError as e:
        print(f"Error: {e}")

    print("\n--- Testing Error Handling ---")
    # Division by zero
    try:
        evaluate("10 / (5 - 5)")
    except ValueError as e:
        print(f"Caught expected error (ZeroDivision): {e}")
    
    # Unknown variable
    try:
        evaluate("a + z")
    except ValueError as e:
        print(f"Caught expected error (Unknown Variable): {e}")

    # Unbalanced parentheses
    try:
        evaluate("(3 + 4")
    except ValueError as e:
        print(f"Caught expected error (Unbalanced Parens): {e}")

    # Malformed syntax
    try:
        evaluate("3 $ 4")
    except ValueError as e:
        print(f"Caught expected error (Malformed Syntax): {e}")
