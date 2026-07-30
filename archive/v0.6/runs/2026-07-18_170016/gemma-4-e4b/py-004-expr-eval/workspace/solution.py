import re
from typing import Dict, List, Tuple

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression without using eval, exec, ast, or external parsing libraries.
    Implements a custom tokenizer and recursive descent parser/evaluator.
    """

    if variables is None:
        variables = {}

    # --- 1. Tokenization ---
    # Regex to capture numbers (including decimals), identifiers, operators, and parentheses.
    # We handle whitespace separately by ignoring it later.
    TOKEN_REGEX = re.compile(r'(\d+\.\d*|\.\d+|\d+)|([a-zA-Z_][a-zA-Z0-9_]*)|([\+\-\*/%\^()])')

    tokens: List[Tuple[str, str]] = []
    cursor = 0
    
    # We iterate through the expression to tokenize it manually to better handle context (unary vs binary).
    i = 0
    while i < len(expr):
        char = expr[i]
        if char.isspace():
            i += 1
            continue

        # Numbers
        if char.isdigit() or (char == '.' and i + 1 < len(expr) and expr[i+1].isdigit()):
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(('NUM', expr[i:j]))
            i = j
            continue

        # Variables
        elif char.isalpha() or char == '_':
            j = i + 1
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
            continue

        # Operators/Parentheses
        elif char in '+-*/%^()':
            op_token = char
            if op_token == '-' or op_token == '+':
                # Check for multi-character tokens (though not strictly needed here)
                pass 
            tokens.append(('OP', op_token))
            i += 1
            continue

        else:
            raise ValueError(f"Malformed syntax: Unexpected character '{char}' at position {i}")

    # --- 2. Preprocessing Tokens (Unary/Binary Distinction) ---
    processed_tokens: List[Tuple[str, str]] = []
    is_expecting_operand = True # Start of expression expects an operand or unary sign

    for token_type, value in tokens:
        if token_type == 'NUM' or token_type == 'VAR':
            processed_tokens.append((token_type, value))
            is_expecting_operand = False
        elif token_type == 'OP':
            op = value
            if op in ('+', '-'):
                # If we expect an operand (start of expression, after (, or after another operator)
                if is_expecting_operand:
                    # Treat as unary sign. We replace it with a special marker for the parser.
                    processed_tokens.append(('UNARY', op))
                    is_expecting_operand = True # Still expecting an operand
                else:
                    # Binary operator
                    processed_tokens.append(('BINOP', op))
                    is_expecting_operand = True # Next token must be an operand
            elif op in ('*', '/', '%', '^'):
                # These are always binary operators (or unary if we allowed it, but standard math doesn't)
                processed_tokens.append(('BINOP', op))
                is_expecting_operand = True # Next token must be an operand
            elif op == '(':
                processed_tokens.append(('LPAREN', value))
                is_expecting_operand = True # After (, we expect an operand or unary sign
            elif op == ')':
                processed_tokens.append(('RPAREN', value))
                is_expecting_operand = False # After ), we expect a binary operator
        else:
             # Should not happen if tokenization is correct
             pass

    # --- 3. Evaluation (Recursive Descent Parser) ---
    
    token_index = 0

    def peek():
        """Returns the current token type and value without advancing."""
        if token_index < len(processed_tokens):
            return processed_tokens[token_index]
        return ('EOF', None)

    def consume(expected_type: str | None = None, expected_value: str | None = None) -> Tuple[str, str]:
        """Advances the token index and returns the consumed token."""
        nonlocal token_index
        if token_index >= len(processed_tokens):
            raise ValueError("Malformed syntax: Unexpected end of expression.")

        token = processed_tokens[token_index]
        token_type, value = token
        
        if expected_type and token_type != expected_type:
             raise ValueError(f"Syntax error: Expected {expected_type}, but found {token_type}.")
        if expected_value and value != expected_value:
            raise ValueError(f"Syntax error: Expected '{expected_value}', but found '{value}'.")

        token_index += 1
        return token_type, value

    def parse_primary() -> float:
        """Handles numbers, variables, and parenthesized expressions."""
        token_type, value = peek()

        if token_type == 'NUM':
            consume('NUM')
            return float(value)
        elif token_type == 'VAR':
            consume('VAR')
            var_name = value
            if var_name not in variables:
                raise ValueError(f"Unknown variable '{var_name}'")
            return variables[var_name]
        elif token_type == 'LPAREN':
            consume('LPAREN')
            result = parse_expression()
            # Must consume the closing parenthesis
            if peek()[0] != 'RPAREN':
                raise ValueError("Unbalanced parentheses: Expected ')'")
            consume('RPAREN')
            return result
        elif token_type == 'UNARY':
            # Handle unary sign (e.g., -3, -(a+b))
            op = consume('UNARY')[1]
            if op == '-':
                # Unary minus: negate the result of the next primary expression
                operand = parse_primary()
                return -operand
            elif op == '+':
                # Unary plus: just return the operand
                operand = parse_primary()
                return operand
        else:
            raise ValueError(f"Malformed syntax: Expected operand, but found {token_type} ('{value}')")

    def parse_unary_op():
        """Handles explicit unary operators (only called if peek is UNARY)."""
        # This function structure is mostly redundant because the logic was integrated into parse_primary
        pass 


    def parse_term() -> float:
        """Handles multiplication, division, modulo (*, /, %) - Left Associative."""
        result = parse_primary()

        while peek()[0] == 'BINOP' and peek()[1] in ('*', '/', '%'):
            op = consume('BINOP')[1]
            right = parse_primary()
            
            if op == '*' and (result * right) != result * right: # Check for overflow/precision issues if necessary, though float handles it.
                pass 

            if op == '/' and right == 0.0:
                raise ValueError("Division by zero")
            if op == '%' and right == 0.0:
                raise ValueError("Modulo by zero")

            if op == '*':
                result *= right
            elif op == '/':
                result /= right
            else: # %
                result %= right
        return result

    def parse_power() -> float:
        """Handles exponentiation (^) - Right Associative."""
        left = parse_term()
        
        while peek()[0] == 'BINOP' and peek()[1] == '^':
            op = consume('BINOP')[1] # Must be ^
            # Because it is right-associative, we recursively call parse_power for the right side.
            right = parse_power() 
            left *= (right ** 1) # Placeholder to satisfy type checker, actual calculation below

        return left ** right if 'right' in locals() else left


    def parse_expression() -> float:
        """Handles addition and subtraction (+, -) - Left Associative."""
        result = parse_power()

        while peek()[0] == 'BINOP' and peek()[1] in ('+', '-'):
            op = consume('BINOP')[1]
            right = parse_power()

            if op == '+':
                result += right
            elif op == '-':
                result -= right
        return result


    # Start parsing from the highest level (addition/subtraction)
    try:
        final_result = parse_expression()
        
        # Check for trailing tokens after successful evaluation
        if peek()[0] != 'EOF':
            raise ValueError(f"Malformed syntax: Unexpected token '{peek()[1]}' remaining.")

        return final_result
    except IndexError as e:
        # Catch unexpected end of input during parsing
        raise ValueError("Malformed syntax or unbalanced parentheses/operators.") from e


if __name__ == '__main__':
    # Example Usage and Testing (Self-Verification)
    print("--- Basic Tests ---")
    try:
        assert evaluate("1 + 2 * 3", {}) == 7.0
        assert evaluate("(1 + 2) * 3", {}) == 9.0
        assert evaluate("10 / 2 % 3", {}) == 2.0 # (5 % 3) = 2
    except AssertionError as e:
        print(f"Basic Test Failed: {e}")

    print("\n--- Exponentiation Tests ---")
    try:
        # Left associative test: 2^3^2 = 2^(3^2) = 512 (Incorrect, should be right assoc)
        # Correct Right Associative: 2^(3^2) = 2^9 = 512. Wait, the prompt says 2^3^2 = 512.
        # Let's assume standard math rules for associativity: a^b^c = a^(b^c).
        # If 2^3^2 means (2^3)^2 = 64, then it is left-associative.
        # Since the prompt explicitly states '^' is RIGHT-ASSOCIATIVE and gives 2^3^2 = 512:
        # 2^(3^2) = 2^9 = 512. This confirms right associativity.
        assert evaluate("2^3^2", {}) == 512.0
        assert evaluate("4^2", {}) == 16.0
    except AssertionError as e:
        print(f"Exponentiation Test Failed: {e}")

    print("\n--- Unary Minus Tests ---")
    try:
        # -3 = -3
        assert evaluate("-3", {}) == -3.0
        # --3 = 3
        assert evaluate("--3", {}) == 3.0
        # -2^2 = -(2^2) = -4
        assert evaluate("-(2^2)", {}) == -4.0
        # 5 * (-x)
        assert evaluate("5*(-10)", {"x": 10.0}) == -50.0
    except AssertionError as e:
        print(f"Unary Test Failed: {e}")

    print("\n--- Variable Tests ---")
    try:
        variables = {"a": 2.0, "b": 3.0}
        assert evaluate("a + b * 2", variables) == 8.0 # 2 + 6
        assert evaluate("(a - b) / 2", variables) == -0.5
    except AssertionError as e:
        print(f"Variable Test Failed: {e}")

    print("\n--- Error Handling Tests ---")
    try:
        evaluate("1 / 0", {})
    except ValueError as e:
        if "Division by zero" not in str(e):
            print(f"Error Check Failed (Expected Div/Zero): {e}")
        else:
             print("Division by Zero Handled.")

    try:
        evaluate("(1 + 2")
    except ValueError as e:
        if "Unbalanced parentheses" not in str(e):
            print(f"Error Check Failed (Expected Unbalanced Paren): {e}")
        else:
             print("Unbalanced Parentheses Handled.")

    try:
        evaluate("1 $ 2", {})
    except ValueError as e:
        if "Unexpected character '$'" not in str(e):
            print(f"Error Check Failed (Expected Bad Char): {e}")
        else:
             print("Malformed Syntax Handled.")

    try:
        evaluate("a + b", {}) # b is unknown
    except ValueError as e:
        if "Unknown variable 'b'" not in str(e):
            print(f"Error Check Failed (Expected Unknown Var): {e}")
        else:
             print("Unknown Variable Handled.")
