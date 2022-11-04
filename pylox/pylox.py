# print("pylox/pylox.py")

import sys
from pathlib import Path
from io import StringIO

from .lexer import Lexer


class LoxException(BaseException):
    pass


def error(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error {where}: {message}")


class Lox:
    def exec(self, fpath):
        """Load Lox source code from a file and execute it"""
        code = Path(fpath).read_text(encoding="utf-8")
        try:
            self.exec_code(code)
        except LoxException as e:
            print(e.message, file=sys.STDERR)
            sys.exit(65)

    def exec_code(self, code):
        for line in code.split("\n"):
            self.exec_line(line)

    def exec_line(self, line):
        lexer = Lexer(StringIO(line))
        print(list(lexer))
