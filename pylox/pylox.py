# print("pylox/pylox.py")

import sys
from pathlib import Path
from io import StringIO
from pprint import pprint

from .lexer import Lexer, Token, TokenType
from .parser import Parser
from .resolver import Resolver
from .interpreter import Interpreter
from .errors import *


class Lox:
    def __init__(self):
        self.interpreter = Interpreter(self)
        self.had_error = False
        self.had_runtime_error = False

    def error_on(self, line: int, message: str) -> None:
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error {where}: {message}")
        self.had_error = True

    def error_at(self, token: Token, message: str):
        if token.type == TokenType.EOF:
            self.report(token.loc.row, " at end", message)
        else:
            self.report(token.loc.row, f" at '{token.lexeme}'", message)

    def runtime_error(self, error: LoxRuntimeError):
        print(f"{error}\n[line {error.token.loc.row}]", file=sys.stderr)
        self.had_runtime_error = True

    def run_file(self, fpath):
        """Load Lox source code from a file and execute it"""
        code = Path(fpath).read_text(encoding="utf-8")
        self.run(code)
        if self.had_error:
            sys.exit(65)
        if self.had_runtime_error:
            sys.exit(70)

    def run(self, code: str):
        lexer = Lexer(self, StringIO(code))
        parser = Parser(self, lexer)
        statements = parser.parse()
        # Stop if there was a syntax error.
        if parser.had_error:
            return
        resolver = Resolver(self, self.interpreter)
        resolver.resolve(statements)
        if self.had_error:
            return
        self.interpreter.interpret(statements)
