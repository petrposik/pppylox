# print("pylox/lexer.py")

import os
import sys
from copy import deepcopy
from io import StringIO
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Union

from .errors import LoxLexerError
from .utils import PeekableIO
from .logger import logger


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


token_type_from_identifier = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


@dataclass(frozen=True)
class Location:
    fpath: str | os.PathLike
    row: int
    col: int

    def __str__(self) -> str:
        if self.fpath:
            return f"{self.fpath}:{self.row}:{self.col}"
        return f"{self.row}:{self.col}"


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: Any
    loc: Location

    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"


class Lexer:
    def __init__(self, lox, chars, fpath=""):
        self.lox = lox
        self.chars = PeekableIO(chars, lookahead=2)
        self.had_error = False
        self.exhausted = False
        self.fpath: str | os.PathLike = fpath
        self.lnum: int = 0
        self.bol: int = 0

    def error(self, where: str, message: str, raise_ex: bool = False) -> None:
        self.had_error = True
        msg = f"{self.loc()} Error {where}: {message}"
        logger.error(msg)
        if raise_ex:
            raise LoxLexerError(msg)
        else:
            print(msg, file=sys.stderr)

    def loc(self):
        """Create a Location object from the current state of Lexer"""
        return Location(
            deepcopy(self.fpath), self.lnum + 1, self.chars.tell() - self.bol
        )

    def token(self, type: TokenType, lexeme: str, literal=None) -> Token:
        """Create a Token object"""
        return Token(type, lexeme, literal, self.loc())

    def __iter__(self):  # -> Iterator[Token]:
        return self

    def __next__(self):  # -> Token:
        if self.exhausted:
            raise StopIteration
        return self.next_token()

    def next_token(self):
        while self.chars.peek():
            # We are at the beginning of the next lexeme
            if t := self.scan_token():
                return t
        self.exhausted = True
        return Token(TokenType.EOF, "", None, self.loc())

    def scan_token(self):
        ch: str = next(self.chars)
        match ch:
            case "(":
                return self.token(TokenType.LEFT_PAREN, ch)
            case ")":
                return self.token(TokenType.RIGHT_PAREN, ch)
            case "{":
                return self.token(TokenType.LEFT_BRACE, ch)
            case "}":
                return self.token(TokenType.RIGHT_BRACE, ch)
            case ",":
                return self.token(TokenType.COMMA, ch)
            case ".":
                return self.token(TokenType.DOT, ch)
            case "-":
                return self.token(TokenType.MINUS, ch)
            case "+":
                return self.token(TokenType.PLUS, ch)
            case ";":
                return self.token(TokenType.SEMICOLON, ch)
            case "*":
                return self.token(TokenType.STAR, ch)
            case "!":
                if self.chars.accept("="):
                    return self.token(TokenType.BANG_EQUAL, "!=")
                else:
                    return self.token(TokenType.BANG, ch)
            case "=":
                if self.chars.accept("="):
                    return self.token(TokenType.EQUAL_EQUAL, "==")
                else:
                    return self.token(TokenType.EQUAL, ch)
            case "<":
                if self.chars.accept("="):
                    return self.token(TokenType.LESS_EQUAL, "<=")
                else:
                    return self.token(TokenType.LESS, ch)
            case ">":
                if self.chars.accept("="):
                    return self.token(TokenType.GREATER_EQUAL, ">=")
                else:
                    return self.token(TokenType.GREATER, ch)
            case "/":
                if self.chars.accept("/"):
                    # A comment goes until the end of the line.
                    while self.chars.peek() != "\n" and not self.chars.exhausted:
                        next(self.chars)
                else:
                    return self.token(TokenType.SLASH, ch)
            case " ":
                pass
            case "\r":
                pass
            case "\t":
                pass
            case "\n":
                self.lnum += 1
                self.bol = self.chars.tell()
            case '"':
                return self.scan_string_literal()
            case _:
                if ch.isdigit():
                    return self.scan_number_literal(ch)
                elif ch.isidentifier():
                    return self.scan_identifier(ch)
                else:
                    self.error("", f"Unexpected character: `{ch}`")

    def scan_string_literal(self):
        string_chars = []
        string_start_loc = self.loc()
        while self.chars.peek() != '"' and not self.chars.exhausted:
            if self.chars.peek() == "\n":
                self.lnum += 1
                self.bol = self.chars.tell() + 1
            string_chars.append(next(self.chars))

        if self.chars.exhausted:
            self.error(f"Unterminated string. String started at {string_start_loc}.")
            return

        # The closing ".
        next(self.chars)
        # String literal token
        value = "".join(string_chars)
        return self.token(TokenType.STRING, value, literal=value)

    def scan_number_literal(self, starting_char):
        number_chars = [starting_char]
        while self.chars.peek().isdigit():
            number_chars.append(next(self.chars))
        # Is there a fractional part?
        if self.chars.peek() == "." and self.chars.peek(1).isdigit():
            number_chars.append(next(self.chars))  # Consume '.'
            while self.chars.peek().isdigit():
                number_chars.append(next(self.chars))
        number_str = "".join(number_chars)
        value = float(number_str)
        return self.token(TokenType.NUMBER, number_str, literal=value)

    def scan_identifier(self, starting_char):
        ident_chars = [starting_char]
        while self.chars.peek().isidentifier() or self.chars.peek().isdigit():
            ident_chars.append(next(self.chars))
        ident_str = "".join(ident_chars)
        token_type = token_type_from_identifier.get(ident_str, TokenType.IDENTIFIER)
        return self.token(token_type, ident_str)
