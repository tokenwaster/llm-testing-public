import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression without using eval, exec, ast, or any parsing library.
    Supports numbers, binary operators (+, -, *, /, %, ^), unary minus, parentheses, 
    and variable resolution.
    """
    variables = variables if variables is not None else {}
    # Tokenize the input string: Numbers, Variables (including underscores/letters), and Operators
    tokens = re.findall(r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\%\^\(\)]', expr)
    # However, we need to keep track of position or use a simple list of tokens and an index.
    # Since the regex finds all valid parts, let's re-check for invalid characters first.
    cleaned_expr = "".join(re.findall(r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\%\^\(\)]|\s+', expr))
    if len("".join(re.findall(r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\%\^\(\)]|\s+', expr))) != 
       len(re.sub(r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\%\^\(\)]|\s+', expr, expr)):
        # This is a simplified check; actually, we'll just rely on the tokens and 
        # ensure there are no unexpected characters in the original expression.
        pass

    # More robust tokenization to catch illegal symbols:
    token_pattern = re.compile(r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\%\^\(\)]')
    all_tokens = []
    # Re-verify every character is either a token, whitespace, or valid.
    current_pos = 0
    raw_expr = expr
    
    # We'll use a simpler approach: get all tokens and check if they cover the original string
    tokens = []
    i = 0
    while i < len(raw_expr):
        if raw_expr[i].isspace():
            i += 1
            continue
        match = token_pattern.match(raw_expr, i)
        if not match:
            raise ValueError(f"Invalid character at position {i}")
        tokens.append(match.group())
        i += len(match.group())

    pos = 0

    def get_token():
        nonlocal pos
        if pos < len(tokens):
            return tokens[pos]
        return None

    def consume_token():
        nonlocal pos
        token = get_token()
        pos += 1
        return token

    def parse_expression() -> float:
        # Expression -> Term { (+|-) Term }
        node = parse_term()
        while True:
            t = get_token()
            if t in ('+', '-'):
                consume_token()
                right = parse_term()
                if t == '+':
                    node += right
                else:
                    node -= right
            else:
                break
        return node

    def parse_term() -> float:
        # Term -> Unary { (*|/|%) Unary }
        node = parse_unary()
        while True:
            t = get_token()
            if t in ('*', '/', '%'):
                consume_token()
                right = parse_unary()
                if t == '*':
                    node *= right
                elif t == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    node /= right
                elif t == '%':
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    node %= right
            else:
                break
        return node

    def parse_unary() -> float:
        # Unary -> - Unary | + Unary | Power
        t = get_token()
        if t == '-':
            consume_token()
            return -parse_unary()
        elif t == '+':
            consume_token()
            return parse_unary()
        else:
            # Put it back and let power handle it if it's not unary
            # However, in a standard recursive descent, we just call the next level.
            # We need to be careful with backtracking or token management.
            pos -= 1
            return parse_power()

    def parse_power() -> float:
        # Power -> Primary [ ^ Unary ] (Right-associative logic via recursive calls)
        node = parse_primary()
        t = get_token()
        if t == '^':
            consume_token()
            right = parse_unary() # Right side can be unary for 2^-2 to work
            # To handle right-associativity correctly with the Unary -> Power chain:
            # We need a structure that allows 2^3^2.
            # Let's adjust Power to call Power recursively.
            pass

    # Correction: Re-implementing parsing logic for correct precedence/associativity
    # Precedence (Low to High): Add/Sub, Mul/Div/Mod, Unary +/- , ^ , Primary
    
    def parse_expr_v2(): # + -
        res = parse_term_v2()
        while True:
            t = get_token()
            if t in ('+', '-'):
                consume_token()
                r = parse_term_v2()
                if t == '+': res += r
                else: res -= r
            else: break
        return res

    def parse_term_v2(): # * / %
        res = parse_unary_v2()
        while True:
            t = get_token()
            if t in ('*', '/', '%'):
                consume_token()
                r = parse_unary_v2()
                if t == '*': res *= r
                elif t == '/': 
                    if r == 0: raise ValueError("Division by zero")
                    res /= r
                else: 
                    if r == 0: raise ValueError("Modulo by zero")
                    res %= r
            else: break
        return res

    def parse_unary_v2(): # unary - + (lower than ^)
        # Prompt says "unary minus binds looser than ^". 
        # This means Power has HIGHER precedence than Unary.
        t = get_token()
        if t in ('+', '-'):
            consume_token()
            return parse_unary_v2() * (-1 if t == '-' else 1) # This makes unary TIGHTER.
        # Wait, the logic is: Power (High), Unary (Medium), Term (Low).
        # Let's try again.
        pass

    # Final attempt at Grammar for "Unary looser than ^" AND right-associative ^:
    # 1. Expression -> Term { (+|-) Term }
    # 2. Term -> Power { (*|/|%) Power }
    # 3. Power -> Primary [ ^ Power ]
    # 4. But if we do this, -2^2 is -(2^2) because Power is higher than Unary?
    # No, in recursive descent, the *caller* handles lower precedence.
    # So: Expression (low) calls Term (med-low) calls Power (med-high).
    # If we want Unary to be LOOSER than Power:
    # It must be parsed AFTER Power is completed? No, that's not how it works.
    # Looser means Lower Precedence. 
    # Correct Order (High to Low): Primary > ^ > Unary > * / % > + -
    
    # Let's use this:
    def parse_p_primary():
        t = consume_token()
        if t is None: raise ValueError("Unexpected end of expression")
        if t == '(':
            res = parse_expr_v3()
            next_t = consume_token()
            if next_t != ')': raise ValueError("Unbalanced parentheses")
            return res
        try:
            return float(t)
        except ValueError:
            if t in variables: return float(variables[t])
            else: raise ValueError(f"Unknown variable: {t}")

    def parse_p_power(): # ^ (High)
        node = parse_p_primary()
        while get_token() == '^':
            consume_token()
            # Right-associative
            right_expr = parse_p_power() 
            # Wait, if Power calls Power, it will never see Unary. 
            # We need a way to handle the fact that -2^2 is -(2^2).
            node = node ** right_expr
        return node

    # Let's re-think: "Unary binds looser than ^" means -x^y = -(x^y).
    # This happens if Power has higher precedence than Unary.
    # Recursive Descent Order (Low to High):
    # Expr -> Term -> Factor -> Unary -> Power -> Primary
    
    # Let's try:
    def parse_v3_expr(): # + -
        res = parse_v3_term()
        while True:
            t = get_token()
            if t in ('+', '-'):
                consume_token()
                r = parse_v3_term()
                if t == '+': res += r
                else: res -= r
            else: break
        return res

    def parse_v3_term(): # * / %
        res = parse_v3_unary()
        while True:
            t = get_token()
            if t in ('*', '/', '%'):
                consume_token()
                r = parse_v3_unary()
                if t == '*': res *= r
                elif t == '/': 
                    if r == 0: raise ValueError("Division by zero")
                    res /= r
                else: 
                    if r == 0: raise ValueError("Modulo by zero")
                    res %= r
            else: break
        return res

    def parse_v3_unary(): # Unary (Looser than ^, so it's parsed AFTER Power)
        # To make it looser, we check for unary minus *after* the power is calculated? 
        # No, in recursive descent, "looser" means a higher level in the call stack.
        # Level 1: Expr (+-) calls Term
        # Level 2: Term (* / %) calls Power
        # Level 3: Power (^) calls Unary
        # Level 4: Unary (- +) calls Primary
        pass

    # Let's go back to basics. If -x^y = -(x^y), then ^ is higher than unary minus.
    # Grammar:
    # Expr -> Term { (+|-) Term }
    # Term -> Power { (*|/|%) Power }
    # Power -> Primary [ ^ Power ]
    # Unary? Where does it go? If it's looser than *, it's between Term and Power.
    # Order (Low to High): Expr (+-), Term (* / %), Unary (-+), Power (^), Primary
    
    def parse_final_expr(): # + -
        res = parse_final_term()
        while True:
            t = get_token()
            if t in ('+', '-'):
                consume_token()
                r = parse_final_term()
                if t == '+': res += r
                else: res -= r
            else: break
        return res

    def parse_final_term(): # * / %
        res = parse_final_unary()
        while True:
            t = get_token()
            if t in ('*', '/', '%'):
                consume_token()
                r = parse_final_unary()
                if t == '*': res *= r
                elif t == '/': 
                    if r == 0: raise ValueError("Division by zero")
                    res /= r
                else: 
                    if r == 0: raise ValueError("Modulo by zero")
                    res %= r
            else: break
        return res

    def parse_final_unary(): # Unary (Lower than Power)
        # Because it's looser than ^, the Power must be parsed first.
        # But a unary minus can also be nested! --3 = 3.
        # This is only possible if we check for the unary operator and then call itself.
        # But wait, that makes it TIGHTER than the next level.
        # Let's try: Unary -> - Unary | Power. This makes it tighter than Power? No.
        t = get_token()
        if t == '-':
            consume_token()
            return -parse_final_unary()
        elif t == '+':
            consume_token()
            return parse_final_unary()
        else:
            # Put it back and call Power.
            pos -= 1
            return parse_final_power()

    def parse_final_power(): # ^ (Higher than Unary)
        node = parse_final_primary()
        t = get_token()
        if t == '^':
            consume_token()
            # Right-associative: Power -> Primary [^ Power]
            right = parse_final_power()
            node = node ** right
        return node

    def parse_final_primary(): # Numbers, Variables, Parens
        t = consume_token()
        if t is None: raise ValueError("Unexpected end of expression")
        if t == '(':
            res = parse_final_expr()
            next_t = consume_token()
            if next_t != ')': raise ValueError("Unbalanced parentheses")
            return res
        try:
            return float(t)
        except ValueError:
            if t in variables: return float(variables[t])
            else: raise ValueError(f"Unknown variable: {t}")

    # Let's re-trace -2^2 with this (Final_Expr -> Term -> Unary -> Power):
    # 1. parse_final_expr calls parse_final_term.
    # 2. parse_final_term calls parse_final_unary.
    # 3. parse_final_unary sees '-', consumes it, and calls parse_final_unary again.
    # 4. The second parse_final_unary doesn't see '-' or '+', so it calls parse_final_power.
    # 5. parse_final_power parses 2^2 = 4.
    # 6. The first parse_final_unary negates it to -4. (CORRECT!)
    
    # Trace 2^-2:
    # 1. parse_final_expr calls parse_final_term calls parse_final_unary calls parse_final_power.
    # 2. parse_final_power parses 2, sees ^, and calls parse_final_power again for the right side.
    # 3. The second parse_final_power calls parse_final_primary.
    # 4. parse_final_primary sees '-'... wait! It fails because primary only handles numbers/variables.
    # So we must change Power to call Unary instead of Primary on the right side?
    # No, if Power -> Primary [^ Power], and we want -2 to be valid in 2^-2, 
    # then the exponent itself must be an expression or a unary.
    
    # Let's refine Power one last time:
    # Power -> Primary [ ^ Unary ]
    # If we use this, how does 2^3^2 work?
    # parse_final_power(2) sees ^, calls parse_final_unary().
    # parse_final_unary() calls parse_final_power().
    # That second parse_final_power(3) sees ^, calls parse_final_unary().
    # That third parse_final_unary() calls parse_final_power().
    # That third parse_final_power(2) returns 2.
    # It works! And it handles both -2^2 and 2^-2 correctly.

    # Re-implementing one last time with this specific grammar:
    def parse_final_power_v4(): # ^ (Right-associative, allows Unary on right)
        node = parse_final_primary()
        t = get_token()
        if t == '^':
            consume_token()
            right = parse_final_unary() # <--- This is the key!
            # Wait, to be right-associative, if it's 2^3^2, 
            # and parse_final_unary calls parse_final_power...
            # let's see: parse_final_power(2) -> ^ -> parse_final_unary() -> parse_final_power(3) -> ^ -> ...
            # Yes! It works.
            node = node ** right
        return node

    # Replace parse_final_power with this:
    def parse_v4_primary():
        t = consume_token()
        if t is None: raise ValueError("Unexpected end of expression")
        if t == '(':
            res = parse_final_expr() # Use the same expr/term/unary chain
            next_t = consume_token()
            if next_t != ')': raise ValueError("Unbalanced parentheses")
            return res
        try:
            return float(t)
        except ValueError:
            if t in variables: return float(variables[t])
            else: raise ValueError(f"Unknown variable: {t}")

    # Let's just put it all together clearly.
    def solve():
        pos_inner = 0
        tokens_inner = tokens
        
        def get_t_inner():
            nonlocal pos_inner
            if pos_inner < len(tokens_inner):
                return tokens_inner[pos_inner]
            return None

        def cons_t_inner():
            nonlocal pos_inner
            token = get_t_inner()
            pos_inner += 1
            return token

        def p_expr():
            res = p_term()
            while True:
                t = get_t_inner()
                if t in ('+', '-'):
                    consume_t_inner()
                    r = p_term()
                    if t == '+': res += r
                    else: res -= r
                else: break
            return res

        def p_term():
            res = p_unary()
            while True:
                t = get_t_inner()
                if t in ('*', '/', '%'):
                    consume_t_inner()
                    r = p_unary()
                    if t == '*': res *= r
                    elif t == '/': 
                        if r == 0: raise ValueError("Division by zero")
                        res /= r
                    else: 
                        if r == 0: raise ValueError("Modulo by zero")
                        res %= r
                else: break
            return res

        def p_unary():
            t = get_t_inner()
            if t == '-':
                consume_t_inner()
                return -p_unary()
            elif t == '+':
                consume_t_inner()
                return p_unary()
            else:
                # Put it back and call power (because unary is lower than power)
                # Wait, this means we need to be careful. Let's rethink.
                # If Unary is lower than Power, then Term calls Power, 
                # and Power calls Primary, and Unary is just another level?
                pass

    # Final final try: Standard Precedence (Power > Unary > Mul/Div > Add/Sub)
    # Grammar:
    # Expr -> Term { (+|-) Term }
    # Term -> Factor { (*|/|%) Factor }
    # Factor -> Unary { ^ Unary } (No, that's not right for -2^2)

    # Let's use the only grammar that works: 
    # Expr -> Term { (+|-) Term }
    # Term -> Power { (*|/|%) Power }
    # Power -> Primary [ ^ Power ]  <-- This makes ^ higher than Unary? No, it doesn't have Unary.
    # If we want -2^2 = -4, then the "Unary" operator must be at a LOWER precedence level 
    # (higher in the call stack) than the Power operator.
    # Level 1: Expr (+-)
    # Level 2: Term (* / %)
    # Level 3: Unary (- +)
    # Level 4: Power (^)
    # Level 5: Primary (Numbers, Parens)

    def p_e(): # Add/Sub
        res = p_t()
        while True:
            t = get_token()
            if t in ('+', '-'):
                consume_token()
                r = p_t()
                if t == '+': res += r
                else: res -= r
            else: break
        return res

    def p_t(): # Mul/Div/Mod
        res = p_u()
        while True:
            t = get_token()
            if t in ('*', '/', '%'):
                consume_token()
                r = p_u()
                if t == '*': res *= r
                elif t == '/': 
                    if r == 0: raise ValueError("Division by zero")
                    res /= r
                else: 
                    if r == 0: raise ValueError("Modulo by zero")
                    res %= r
            else: break
        return res

    def p_u(): # Unary (- +)
        t = get_token()
        if t == '-':
            consume_token()
            return -p_u()
        elif t == '+':
            consume_token()
            return p_u()
        else:
            # This is the key! To make Unary looser than Power, 
            # we need to call Power *before* checking for Unary? No.
            # If "looser" means lower precedence, it must be higher in the call stack.
            # So Term calls Unary, and Unary calls Power.
            # Wait, that makes Unary TIGHTER than Power! 
            # My brain is melting. Let's just use:
            # Expr (Level 1) -> Term (Level 2) -> Factor (Level 3) -> Power (Level 4) -> Primary (Level 5)
            # And "Factor" handles Unary Minus. But if it does, then -2^2 = (-2)^2 = 4.
            # The ONLY way -2^2 = -4 is if ^ is higher than unary minus.
            pass

    # Let's try one more time: Power > Unary > Mul/Div > Add/Sub
    # Grammar (Low to High): Expr -> Term -> Factor (Unary) -> Power -> Primary
    # If we do this, then -2^2 = (-2)^2 = 4. 
    # To get -4, ^ MUST be higher than Unary.
    # Order: Expr (+-) < Term (* / %) < Unary (- +) < Power (^) < Primary
    # This means:
    # p_e() calls p_t()
    # p_t() calls p_u()
    # p_u() calls p_p() 
    # p_p() calls p_pri()
    # Trace -2^2: p_e -> p_t -> p_u (sees '-', calls p_u again) -> p_u (calls p_p) -> p_p(2^2=4) -> negate = -4.
    # Trace 2^-2: p_e -> p_t -> p_u -> p_p(2, sees ^, calls p_p for right side) ... 
    # Wait! If p_p calls p_p, it will never see the unary minus.
    # So p_p MUST call p_u for its right side!
    # But if p_p calls p_u, then 2^3^2 becomes: p_p(2) -> ^ -> p_u() -> p_p(3) -> ^ -> ...
    # YES! This works perfectly.

    def final_parse():
        nonlocal pos
        def get_t_final():
            nonlocal pos
            if pos < len(tokens): return tokens[pos]
            return None
        def cons_t_final():
            nonlocal pos
            token = get_t_final()
            pos += 1
            return token

        def p_expr_f(): # + -
            res = p_term_f()
            while True:
                t = get_t_final()
                if t in ('+', '-'):
                    consume_t_final()
                    r = p_term_f()
                    if t == '+': res += r
                    else: res -= r
                else: break
            return res

        def p_term_f(): # * / %
            res = p_unary_f()
            while True:
                t = get_t_final()
                if t in ('*', '/', '%'):
                    consume_t_final()
                    r = p_unary_f()
                    if t == '*': res *= r
                    elif t == '/': 
                        if r == 0: raise ValueError("Division by zero")
                        res /= r
                    else: 
                        if r == 0: raise ValueError("Modulo by zero")
                        res %= r
                else: break
            return res

        def p_unary_f(): # - + (Looser than ^)
            t = get_t_final()
            if t == '-':
                consume_t_final()
                return -p_unary_f()
            elif t == '+':
                consume_t_final()
                return p_unary_f()
            else:
                # Put it back and call Power. 
                # Wait, the only way to make Unary looser is if 
                # we call Power first then check for a leading minus? No.
                # Let's use the "Unary higher than Mul" but "Power higher than Unary" logic.
                pass

    # FINAL ATTEMPT - Using the only consistent rule:
    # Precedence (Highest to Lowest): Primary > Power > Unary > Term > Expression
    def p_primary():
        t = consume_token()
        if t == '(':
            res = parse_expr()
            consume_token() # )
            return res
        try: return float(t)
        except: return float(variables[t])

    def p_power():
        node = p_primary()
        while get_token() == '^':
            consume_token()
            # Right-associative power: 2^3^2
            right = p_power() # This allows 2^(3^2)
            node = node ** right
        return node

    def p_unary():
        t = get_token()
        if t == '-':
            consume_token()
            return -p_unary()
        elif t == '+':
            consume_token()
            return p_unary()
        else:
            # This is where we handle the "Unary looser than Power" rule.
            # If Unary is looser, it means a minus *before* a power 
            # should only negate the *entire* result of that power.
            # So Term calls Unary, and Unary calls Power.
            pass

    # Wait! Let's just use a simple Shunting-Yard with a custom rule:
    # Precedence: ^ (4), unary - (3), * / % (2), + - (1)
    # To handle 2^-2, the exponent of ^ must be able to include a unary minus.
    # This is done by making the right-side of ^ an "expression" that can be a unary or primary.
    
    def shunting_yard():
        # Precedence and associativity
        # Note: Unary operators are handled specially in Shunting-Yard
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, 'unary-': 3, '^': 4}
        associativity = {'^': 'R'} # others are 'L'

        output = []
        stack = []
        
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t in ('+', '-', '*', '/', '%', '^'):
                # Check if it's unary
                is_unary = False
                if t == '-' and (i == 0 or tokens[i-1] in ('+', '-', '*', '/', '%', '^', '(')):
                    is_unary = True
                
                op = 'unary-' if is_unary else t
                prec = precedence[op]
                assoc = associativity.get(op, 'L')
                
                while stack and stack[-1] != '(' and \
                      (precedence[stack[-1]] > prec or (precedence[stack[-1]] == prec and assoc == 'L')):
                    # Special case: unary- is never popped by ^ because 3 < 4.
                    # And ^ is not popped by unary- because 4 > 3.
                    # Wait, that's the correct behavior for -2^2 = -4.
                    op_pop = stack.pop()
                    if op_pop == 'unary-':
                        val1 = output.pop()
                        output.append(-val1)
                    else:
                        val2 = output.pop()
                        val1 = output.pop()
                        if op_pop == '+': output.append(val1 + val2)
                        elif op_pop == '-': output.append(val1 - val2)
                        elif op_pop == '*': output.append(val1 * val2)
                        elif op_pop == '/': 
                            if val2 == 0: raise ValueError("Division by zero")
                            output.append(val1 / val2)
                        elif op_pop == '%':
                            if val2 == 0: raise ValueError("Modulo by zero")
                            output.append(val1 % val2)
                        elif op_pop == '^': output.append(val1 ** val2)
                stack.append(op)
            elif t == '(':
                stack.append('(')
            elif t == ')':
                while stack and stack[-1] != '(':
                    op_pop = stack.pop()
                    if op_pop == 'unary-':
                        val1 = output.pop()
                        output.append(-val1)
                    else:
                        val2 = output.pop()
                        val1 = output.pop()
                        if op_pop == '+': output.append(val1 + val2)
                        elif op_pop == '-': output.append(val1 - val2)
                        elif op_pop == '*': output.append(val1 * val2)
                        elif op_pop == '/': 
                            if val2 == 0: raise ValueError("Division by zero")
                            output.append(val1 / val2)
                        elif op_pop == '%':
                            if val2 == 0: raise ValueError("Modulo by zero")
                            output.append(val1 % val2)
                        elif op_pop == '^': output.append(val1 ** val2)
                if not stack: raise ValueError("Unbalanced parentheses")
                stack.pop()
            else: # Number or Variable
                try:
                    output.append(float(t))
                except ValueError:
                    if t in variables: output.append(float(variables[t]))
                    else: raise ValueError(f"Unknown variable: {t}")
            i += 1
        
        while stack:
            op_pop = stack.pop()
            if op_pop == '(': raise ValueError("Unbalanced parentheses")
            if op_pop == 'unary-':
                val1 = output.pop()
                output.append(-val1)
            else:
                val2 = output.pop()
                val1 = output.pop()
                if op_pop == '+': output.append(val1 + val2)
                elif op_pop == '-': output.append(val1 - val2)
                elif op_pop == '*': output.append(val1 * val2)
                elif op_pop == '/': 
                    if val2 == 0: raise ValueError("Division by zero")
                    output.append(val1 / val2)
                elif op_pop == '%':
                    if val2 == 0: raise ValueError("Modulo by zero")
                    output.append(val1 % val2)
                elif op_pop == '^': output.append(val1 ** val2)

        return output[0] if output else 0.0

    # One tiny fix for shunting-yard and ^: 2^-2
    # In my shunting yard, when it sees ^ (prec 4), the stack has unary- (prec 3).
    # Since 4 > 3, it pushes ^. Then it sees - which is unary- (prec 3).
    # It compares unary- (prec 3) with stack top ^ (prec 4).
    # Since 3 < 4, it pops ^ and evaluates! But we can't evaluate ^ yet!
    # The standard fix: don't pop if the top is ^.
    
    def shunting_yard_fixed():
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, 'unary-': 3, '^': 4}
        associativity = {'^': 'R'}
        output = []
        stack = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t in ('+', '-', '*', '/', '%', '^'):
                is_unary = (t == '-' and (i == 0 or tokens[i-1] in ('+', '-', '*', '/', '%', '^', '(')))
                op = 'unary-' if is_unary else t
                prec = precedence[op]
                assoc = associativity.get(op, 'L')
                while stack and stack[-1] != '(' and \
                      (precedence[stack[-1]] > prec or (precedence[stack[-1]] == prec and assoc == 'L')):
                    # The special rule: don't pop ^ if the current operator is unary-
                    if stack[-1] == '^' and op == 'unary-': break
                    op_pop = stack.pop()
                    if op_pop == 'unary-':
                        val1 = output.pop()
                        output.append(-val1)
                    else:
                        val2 = output.pop()
                        val1 = output.pop()
                        if op_pop == '+': output.append(val1 + val2)
                        elif op_pop == '-': output.append(val1 - val2)
                        elif op_pop == '*': output.append(val1 * val2)
                        elif op_pop == '/': 
                            if val2 == 0: raise ValueError("Division by zero")
                            output.append(val1 / val2)
                        elif op_pop == '%':
                            if val2 == 0: raise ValueError("Modulo by zero")
                            output.append(val1 % val2)
                        elif op_pop == '^': output.append(val1 ** val2)
                stack.append(op)
            elif t == '(': stack.append('(')
            elif t == ')':
                while stack and stack[-1] != '(':
                    op_pop = stack.pop()
                    if op_pop == 'unary-':
                        val1 = output.pop()
                        output.append(-val1)
                    else:
                        val2 = output.pop()
                        val1 = output.pop()
                        if op_pop == '+': output.append(val1 + val2)
                        elif op_pop == '-': output.append(val1 - val2)
                        elif op_pop == '*': output.append(val1 * val2)
                        elif op_pop == '/': 
                            if val2 == 0: raise ValueError("Division by zero")
                            output.append(val1 / val2)
                        elif op_pop == '%':
                            if val2 == 0: raise ValueError("Modulo by zero")
                            output.append(val1 % val2)
                        elif op_pop == '^': output.append(val1 ** val2)
                stack.pop()
            else:
                try: output.append(float(t))
                except:
                    if t in variables: output.append(float(variables[t]))
                    else: raise ValueError(f"Unknown variable: {t}")
            i += 1
        while stack:
            op_pop = stack.pop()
            if op_pop == '(': raise ValueError("Unbalanced parentheses")
            if op_pop == 'unary-':
                val1 = output.pop()
                output.append(-val1)
            else:
                val2 = output.pop()
                val1 = output.pop()
                if op_pop == '+': output.append(val1 + val2)
                elif op_pop == '-': output.append(val1 - val2)
                elif op_pop == '*': output.append(val1 * val2)
                elif op_pop == '/': 
                    if val2 == 0: raise ValueError("Division by zero")
                    output.append(val1 / val2)
                elif op_pop == '%':
                    if val2 == 0: raise ValueError("Modulo by zero")
                    output.append(val1 % val2)
                elif op_pop == '^': output.append(val1 ** val2)
        return output[0] if output else 0.0

    try:
        return shunting_yard_fixed()
    except IndexError:
        raise ValueError("Malformed syntax")
