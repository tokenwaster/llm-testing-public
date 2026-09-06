def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    variables = {} if variables is None else variables
    values = []
    operators = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "~": 3, "^": 4}

    def apply_operator():
        op = operators.pop()
        if op == "~":
            if not values:
                raise ValueError("Missing operand")
            values.append(-values.pop())
            return

        if len(values) < 2:
            raise ValueError("Missing operand")
        right = values.pop()
        left = values.pop()
        if op in ("/", "%") and right == 0:
            raise ValueError("Division or modulo by zero")

        try:
            if op == "+":
                result = left + right
            elif op == "-":
                result = left - right
            elif op == "*":
                result = left * right
            elif op == "/":
                result = left / right
            elif op == "%":
                result = left % right
            elif op == "^":
                result = left ** right
            else:
                raise ValueError("Invalid operator")
            values.append(float(result))
        except (ArithmeticError, TypeError, ValueError) as error:
            raise ValueError("Invalid arithmetic operation") from error

    def is_letter(char):
        return "a" <= char <= "z" or "A" <= char <= "Z" or char == "_"

    def is_digit(char):
        return "0" <= char <= "9"

    i = 0
    expect_operand = True

    while i < len(expr):
        char = expr[i]
        if char.isspace():
            i += 1
            continue

        if is_digit(char):
            if not expect_operand:
                raise ValueError("Missing operator")
            start = i
            while i < len(expr) and is_digit(expr[i]):
                i += 1
            if i < len(expr) and expr[i] == ".":
                i += 1
                while i < len(expr) and is_digit(expr[i]):
                    i += 1
            values.append(float(expr[start:i]))
            expect_operand = False
            continue

        if is_letter(char):
            if not expect_operand:
                raise ValueError("Missing operator")
            start = i
            i += 1
            while i < len(expr) and (is_letter(expr[i]) or is_digit(expr[i])):
                i += 1
            name = expr[start:i]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            try:
                values.append(float(variables[name]))
            except (TypeError, ValueError, OverflowError) as error:
                raise ValueError(f"Invalid value for variable: {name}") from error
            expect_operand = False
            continue

        if char == "(":
            if not expect_operand:
                raise ValueError("Missing operator")
            operators.append("(")
        elif char == ")":
            if expect_operand:
                raise ValueError("Missing operand")
            while operators and operators[-1] != "(":
                apply_operator()
            if not operators:
                raise ValueError("Unbalanced parentheses")
            operators.pop()
        elif char in "+-*/%^":
            if expect_operand:
                if char != "-":
                    raise ValueError("Expected operand")
                # Prefix minus must not reduce a pending exponentiation.
                operators.append("~")
            else:
                while operators and operators[-1] != "(":
                    top = operators[-1]
                    if precedence[top] < precedence[char]:
                        break
                    if precedence[top] == precedence[char] and char == "^":
                        break
                    apply_operator()
                operators.append(char)
                expect_operand = True
        else:
            raise ValueError(f"Unexpected character: {char!r}")

        i += 1

    if expect_operand:
        raise ValueError("Missing operand")
    if "(" in operators:
        raise ValueError("Unbalanced parentheses")
    while operators:
        apply_operator()
    if len(values) != 1:
        raise ValueError("Malformed expression")
    return float(values[0])
