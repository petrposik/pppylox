from .lexer import Token
from .errors import LoxRuntimeError


class Environment:
    def __init__(self, enclosing: "Environment" = None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name: str, value):
        self.values[name] = value

    def assign(self, name: Token, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return None
        if self.enclosing:
            self.enclosing.assign(name, value)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
