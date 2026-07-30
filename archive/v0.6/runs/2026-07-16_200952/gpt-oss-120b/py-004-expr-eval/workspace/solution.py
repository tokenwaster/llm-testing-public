# solution.py
from __future__ import annotations
from typing import List, Tuple, Union, Dict

Token = Tuple[str, Union[str, float, None]]  # (type, value)


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluate an arithmetic expression without using eval/exec/ast.

    Supported:
        - numbers (int, float)
        - binary operators: + - * / % ^   (^ is right‑associative)
        - unary minus (repeatable)
        - parentheses
        - variables (identifiers) from the supplied dict
        - whitespace anywhere

    Errors raise ValueError.
    """
    if variables is None:
        variables = {}

    # --------------------------------------------------------------------- #
    # Tokenizer
    # --------------------------------------------------------------------- #
    def tokenize(s: str) -> List[Token]:
        tokens: List[Token] = []
        i = 0
        n = len(s)

        while i < n:
            ch = s[i]

            # skip whitespace
            if ch.isspace():
                i += 1
                continue

            # number (must start with a digit)
            if ch.isdigit():
                start = i
                while i < n and s[i].isdigit():
                    i += 1
                if i < n and s[i] == '.':
                    i += 1
                    while i < n and s[i].isdigit():
                        i += 1
                num_str = s[start:i]
                try:
                    num_val = float(num_str)
                except ValueError:
                    raise ValueError(f"Invalid number literal: {num_str}")
                tokens.append(("NUMBER", num_val))
                continue

            # identifier / variable name
            if ch.isalpha() or ch == "_":
                start = i
                while i < n and (s[i].isalnum() or s[i] == "_"):
                    i += 1
                ident = s[start:i]
                tokens.append(("IDENT", ident))
                continue

            # operators and parentheses
            if ch in "+-*/%^()":
                if ch == '(':
                    tokens.append(("LPAREN", ch))
                elif ch == ')':
                    tokens.append(("RPAREN", ch))
                else:
                    tokens.append(("OP", ch))
                i += 1
                continue

            raise ValueError(f"Invalid character at position {i}: '{ch}'")

        tokens.append(("EOF", None))
        return tokens

    # --------------------------------------------------------------------- #
    # Parser (recursive descent)
    # --------------------------------------------------------------------- #
    class Parser:
        def __init__(self, tokens: List[Token]):
            self.tokens = tokens
            self.pos = 0

        @property
        def cur(self) -> Token:
            return self.tokens[self.pos]

        def eat(self, typ: str, val: Union[str, None] = None) -> None:
            t_type, t_val = self.cur
            if t_type != typ or (val is not None and t_val != val):
                raise ValueError(f"Unexpected token {self.cur}, expected {typ} {val}")
            self.pos += 1

        # entry point
        def parse(self) -> float:
            result = self.expr()
            if self.cur[0] != "EOF":
                raise ValueError("Unexpected trailing characters")
            return result

        # expr -> add_sub
        def expr(self) -> float:
            return self.add_sub()

        # add_sub -> mul_div (('+'|'-') mul_div)*
        def add_sub(self) -> float:
            left = self.mul_div()
            while self.cur[0] == "OP" and self.cur[1] in ("+", "-"):
                op = self.cur[1]
                self.eat("OP", op)
                right = self.mul_div()
                if op == "+":
                    left = left + right
                else:
                    left = left - right
            return left

        # mul_div -> unary (('*'|'/'|'%') unary)*
        def mul_div(self) -> float:
            left = self.unary()
            while self.cur[0] == "OP" and self.cur[1] in ("*", "/", "%"):
                op = self.cur[1]
                self.eat("OP", op)
                right = self.unary()
                if op == "*":
                    left = left * right
                elif op == "/":
                    if right == 0:
                        raise ValueError("Division by zero")
                    left = left / right
                else:  # '%'
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            return left

        # unary -> '-' unary | power
        def unary(self) -> float:
            if self.cur[0] == "OP" and self.cur[1] == "-":
                self.eat("OP", "-")
                operand = self.unary()
                return -operand
            return self.power()

        # power -> atom ('^' power)?
        # right‑associative
        def power(self) -> float:
            left = self.atom()
            if self.cur[0] == "OP" and self.cur[1] == "^":
                self.eat("OP", "^")
                right = self.power()
                left = left ** right
            return left

        # atom -> NUMBER | IDENT | '(' expr ')'
        def atom(self) -> float:
            t_type, t_val = self.cur
            if t_type == "NUMBER":
                self.eat("NUMBER")
                return float(t_val)  # type: ignore
            if t_type == "IDENT":
                name = t_val  # type: ignore
                self.eat("IDENT")
                if name not in variables:
                    raise ValueError(f"Unknown variable: {name}")
                return float(variables[name])
            if t_type == "LPAREN":
                self.eat("LPAREN")
                val = self.expr()
                if self.cur[0] != "RPAREN":
                    raise ValueError("Unbalanced parentheses")
                self.eat("RPAREN")
                return val
            raise ValueError(f"Unexpected token: {self.cur}")

    # --------------------------------------------------------------------- #
    # Run parser
    # --------------------------------------------------------------------- #
    token_list = tokenize(expr)
    parser = Parser(token_list)
    return parser.parse()
