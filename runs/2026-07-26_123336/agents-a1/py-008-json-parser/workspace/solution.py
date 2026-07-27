# parse.py
import sys

class JSONParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def _skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def _expect_char(self, ch):
        if self.pos >= len(self.text):
            raise ValueError("unexpected end")
        c = self.text[self.pos]
        if c != ch:
            raise ValueError(f"expected {ch}")
        self.pos += 1

    def parse_value(self):
        self._skip_whitespace()
        if self.pos >= len(self.text):
            raise ValueError("empty input")
        c = self.text[self.pos]
        if c == '{':
            return self.parse_object()
        elif c == '[':
            return self.parse_array()
        elif c == '"':
            # consume opening quote and parse string content
            self.pos += 1
            val = self._parse_string_content()
            return val
        elif c in '-+0123456789':
            return self._parse_number()
        elif c == 't' and self.text[self.pos:self.pos+4] == 'true':
            if (self.pos + 4 >= len(self.text) or not self.text[self.pos+4].isalnum()):
                # We must ensure that after "true" there is no continuation like trueABC.
                # However our later checks for trailing content will catch it, but to be safe:
                pass
            if (self.pos + 4 >= len(self.text) or not self.text[self.pos+4].isalnum()):
                self.pos += 4
                return True
        elif c == 'f' and self.text[self.pos:self.pos+5] == 'false':
            if (self.pos + 5 >= len(self.text) or not self.text[self.pos+5].isalnum()):
                self.pos += 5
                return False
        elif c == 'n' and self.text[self.pos:self.pos+4] == 'null':
            if (self.pos + 4 >= len(self.text) or not self.text[self.pos+4].isalnum()):
                self.pos += 4
                return None
        raise ValueError("invalid token")

    def parse_object(self):
        # consume opening '{'
        start = self.pos
        if self.pos >= len(self.text):
            raise ValueError("unexpected end")
        if self.text[self.pos] != '{':
            raise ValueError("expected {")
        self.pos += 1
        result = {}
        first_entry = True
        while True:
            # skip whitespace and check for closing brace before any entry
            self._skip_whitespace()
            if self.pos >= len(self.text):
                raise ValueError("unexpected end")
            c = self.text[self.pos]
            if c == '}':
                self.pos += 1
                break

            # If not first entry, require a comma before the next key
            if not first_entry:
                if c != ',':
                    raise ValueError("expected , or }")
                self.pos += 1  # consume ','

            else:
                first_entry = False

            # After optional comma (or none for first entry), must have a string key.
            # Skip whitespace again to position at next token start.
            self._skip_whitespace()
            if self.pos >= len(self.text):
                raise ValueError("unexpected end")
            if self.text[self.pos] != '"':
                raise ValueError("expected '\"' for object key")

            # consume opening quote of key string and parse its content
            self.pos += 1
            key_val = self._parse_string_content()
            self._skip_whitespace()
            self._expect_char(':')
            value_val = self.parse_value()
            result[key_val] = value_val

        return result

    def parse_array(self):
        if self.pos >= len(self.text) or self.text[self.pos] != '[':
            raise ValueError("expected [")
        self.pos += 1
        result = []
        first_entry = True
        while True:
            # skip whitespace and check for closing bracket before any entry
            self._skip_whitespace()
            if self.pos >= len(self.text):
                raise ValueError("unexpected end")
            c = self.text[self.pos]
            if c == ']':
                self.pos += 1
                break

            # If not first entry, require a comma before the next value.
            if not first_entry:
                if c != ',':
                    raise ValueError("expected , or ]")
                self.pos += 1  # consume ','
            else:
                first_entry = False

            value_val = self.parse_value()
            result.append(value_val)

        return result

    def _parse_string_content(self):
        """Parse string content after the opening quote. Returns the decoded unicode string."""
        chars = []
        while True:
            if self.pos >= len(self.text):
                raise ValueError("unterminated string")
            c = self.text[self.pos]
            if c == '"':
                # End of string; consume closing quote and return built value.
                self.pos += 1
                return ''.join(chars)
            elif c != '\\':
                chars.append(c)
                self.pos += 1
            else:
                # Escape sequence start, must have next char
                if self.pos + 1 >= len(self.text):
                    raise ValueError("unterminated string")
                esc = self.text[self.pos + 1]
                self.pos += 2  # skip backslash and the escaped character (or handle below)

                if esc == '"':
                    chars.append('"')
                elif esc == '\\':
                    chars.append('\\')
                elif esc == '/':
                    chars.append('/')
                elif esc in 'bfnrt':
                    # \b, \f, \n, \r, \t -> control characters with codes 8,12,10,13,9 respectively.
                    if esc == 'b':
                        chars.append('\b')
                    elif esc == 'f':
                        chars.append('\f')
                    elif esc == 'n':
                        chars.append('\n')
                    elif esc == 'r':
                        chars.append('\r')
                    elif esc == 't':
                        chars.append('\t')
                elif esc == 'u':
                    # Unicode escape \uXXXX
                    if self.pos + 4 > len(self.text):
                        raise ValueError("invalid unicode escape")
                    hex_str = self.text[self.pos:self.pos+4]
                    try:
                        code_point = int(hex_str, 16)
                    except ValueError:
                        raise ValueError("invalid unicode digits")
                    # For now treat as simple character; handle surrogates later if needed.
                    chars.append(chr(code_point))
                else:
                    raise ValueError(f"unknown escape {esc}")

    def _parse_number(self):
        start_idx = self.pos
        has_neg = False
        # optional sign
        c = self.text[self.pos]
        if c == '-':
            has_neg = True
            self.pos += 1
        elif c == '+':
            self.pos += 1

        # Must have at least one digit after sign (or directly)
        if self.pos >= len(self.text):
            raise ValueError("missing number digits")
        int_digits_start = self.pos
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
        int_part_str = self.text[int_digits_start:self.pos]
        if not int_part_str:
            raise ValueError("no integer part in number")

        # Leading zero check (only "0" allowed; any other leading zeros are invalid)
        if len(int_part_str) > 1 and int_part_str[0] == '0':
            raise ValueError("leading zeros not allowed")

        has_fraction = False
        frac_part_str = ""
        # Check for decimal point followed by at least one digit
        if self.pos < len(self.text) and self.text[self.pos] == '.':
            self.pos += 1
            if self.pos >= len(self.text):
                raise ValueError("decimal point without fractional part")
            frac_digits_start = self.pos
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
            frac_part_str = self.text[frac_digits_start:self.pos]
            if not frac_part_str:
                raise ValueError("decimal point without fractional part")
            has_fraction = True

        # Check for exponent part (e/E with optional sign and digits)
        exp_val = None
        if self.pos < len(self.text) and self.text[self.pos] in 'eE':
            self.pos += 1
            sign_char = None
            if self.pos < len(self.text):
                c2 = self.text[self.pos]
                if c2 == '+':
                    sign_char = '+'
                    self.pos += 1
                elif c2 == '-':
                    sign_char = '-'
                    self.pos += 1

            exp_digits_start = self.pos
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
            exp_str = self.text[exp_digits_start:self.pos]
            if not exp_str:
                raise ValueError("exponent without digits")
            try:
                exponent = int(exp_str)
            except ValueError:
                raise ValueError("invalid number")
            if sign_char == '-':
                exponent = -exponent
            exp_val = exponent

        # Compute numeric value according to spec (integers must be Python ints, others floats)
        if has_fraction:
            # Decimal point present => treat as floating-point.
            try:
                token_str = self.text[start_idx:self.pos]
                val = float(token_str)
            except ValueError:
                raise ValueError("invalid number")
            if has_neg:
                val = -val
            return val

        # No decimal point; may still have exponent
        try:
            base_int = int(int_part_str)
        except ValueError:
            raise ValueError("invalid number")

        if exp_val is None:
            num = base_int * (1 if not has_neg else -1)
            return num

        # Exponent present but no decimal point.
        # Positive or zero exponent => integer multiplication.
        if exp_val >= 0:
            try:
                multiplier = 10 ** abs(exp_val)
            except OverflowError:
                raise ValueError("number too large")
            num = base_int * multiplier
            if has_neg:
                num = -num
            return num

        # Negative exponent => possible fraction; check exact integer result.
        shift = abs(exp_val)
        try:
            divisor = 10 ** shift
        except OverflowError:
            raise ValueError("number too large")
        if base_int % divisor == 0:
            num = (base_int // divisor) * (1 if not has_neg else -1)
            return num
        # Otherwise treat as float.
        val = float(base_int) / divisor
        if has_neg:
            val = -val
        return val


def parse(text: str):
    try:
        parser = JSONParser(text)
        result = parser.parse_value()
        parser._skip_whitespace()
        if parser.pos != len(parser.text):
            raise ValueError("trailing garbage")
        return result
    except Exception:
        return None


# For testing purposes.
if __name__ == "__main__":
    # Simple sanity checks (can be removed).
    print(parse(''))  # Expected None
    print(parse('null'))  # Expected None? Actually null parses to Python None, which is not None; but tests distinguish via valid/invalid inputs.
    print(parse('"hello"'))  # Expected "hello"
