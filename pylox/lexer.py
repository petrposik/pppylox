# print("pylox/lexer.py")

from io import StringIO

from .exceptions import LoxLexerError


class Token:
    pass


class Lexer:
    def __init__(self, chars):
        self.chars = StringIO(chars)
        self.had_error = False

    def error(self, line: int, where: str, message: str) -> None:
        self.had_error = True
        raise LoxLexerError(f"[line {line}] Error {where}: {message}")

    def __iter__(self):  # -> Iterator[Token]:
        return self

    def __next__(self):  # -> Token:
        # if self.exhausted:
        #     raise StopIteration
        return self.next_token()

    def next_token(self):
        ch = self.chars.read(1)
        if ch:
            return ch
        else:
            raise StopIteration
