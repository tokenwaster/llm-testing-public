def match(pattern: str, text: str) -> bool:
    """
    Reports whether `pattern` matches the ENTIRE `text` (not a substring),
    supporting exactly this regex subset:

    - literal characters (match themselves)
    - `.` — any single character
    - `*` — zero or more of the preceding element
    - `+` — one or more of the preceding element
    - `?` — zero or one of the preceding element
    - character classes `[abc]`, ranges `[a-z0-9]`, and negation `[^abc]`
      (`*`/`+`/`?` may follow a class)

    Rules:
    - Do not use the `re` module or any other regex library — build the matcher
      yourself (recursive backtracking is the expected approach).
    - Malformed patterns (e.g. an unclosed `[`, or `*` with nothing before it)
      should raise `ValueError`.
    - An empty pattern matches only the empty text.
    """

    def _match_recursive(pattern: str, text: str) -> bool:
        if not pattern:
            return not text

        if not text:
            if all(c == '*' for c in pattern):
                return True
            else:
                return False

        if len(pattern) >= 3 and pattern[0] == '*' and pattern[1] == '*':
           if _match_recursive(pattern[2:],text):
               return True
           else:
                return False

        if len(pattern) >= 2 and pattern[0] == '*' and pattern[1] != '*':
            if _match_recursive(pattern[2:], text):
                return True
            elif (len(pattern)>2 and pattern[2]==" "):
              return _match_recursive(pattern[3:], text)

            else: return False


        if len(pattern) >= 2 and pattern[0] == '+' and pattern[1] != '+':
           if _match_recursive(pattern[2:],text):
               return True
           else:
                return False



        if len(pattern) >= 2 and pattern[0] == '?' and pattern[1] != '?':
            if _match_recursive(pattern[2:],text):
                return True
            elif text and (text[0]==pattern[2] or pattern[2]=="."):
                return _match_recursive(pattern[3:],text[:])
            else: return False

        if len(pattern) >= 2 and pattern[0] == '?' and pattern[1] == '?':
              if _match_recursive(pattern[2:], text):
                  return True
              elif text and (text[0]==pattern[2] or pattern[2]=="."):
                return _match_recursive(pattern[3:],text[:])

              else: return False



        if pattern[0] == '.':
            return _match_recursive(pattern[1:], text[1:])

        if pattern[0] == '[':
            end = pattern.find(']')
            if end == -1:
                raise ValueError("Unclosed character class")
            char_class = pattern[1:end]
            if len(char_class) == 0:
                raise ValueError("Empty character class")

            for char in text[:len(char_class)]:
                if char not in char_class:
                    return False
            if len(text) > len(char_class):
                 return _match_recursive(pattern[end+1:], text[len(char_class):])
            else: return True


        if pattern[0] == '-':
          if len(pattern) >=2 and pattern[1]=="-" :
              raise ValueError("Invalid range")

          if len(text)>=1 and (text[0]>pattern[1] or text[0]<pattern[1]):
            return False
          else:
             return _match_recursive(pattern[1:],text[1:])



        if pattern[0] == '^':
           if len(text) >= 1 and (text[0]==pattern[1] or pattern[1]=="."):
                return _match_recursive(pattern[2:], text[1:])

           else: return False


        if text[0] == pattern[0]:
            return _match_recursive(pattern[1:], text[1:])

        return False

    return _match_recursive(pattern, text)
