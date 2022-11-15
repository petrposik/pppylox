from .lexer import Token
from .errors import LoxRuntimeError


class Environment:
    def __init__(self):
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
