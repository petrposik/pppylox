# print("pylox/lexer.py")

from io import StringIO
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

from .exceptions import LoxLexerError


class TokenType(Enum):
    # Single-character tokens.
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()

    # One or two character tokens.
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Literals.
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords.
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    EOF = auto()


@dataclass
class Loc:
    fpath: str
    line: int
    column: int


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: Any
    loc: Loc

    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"


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
