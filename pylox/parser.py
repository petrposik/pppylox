from .lexer import Lexer, TokenType, error_at
from .utils import Peekable
from .ast import *
from .errors import *


class Parser:
    """A recursive descent parser for Lox langugae"""

    def __init__(self, lexer: Lexer):
        self.lexer = Peekable(lexer)
        self.had_error = False

    @property
    def exhausted(self):
        return self.lexer.peek().type == TokenType.EOF

    def error(self, token: Token, message: str) -> LoxParserError:
        self.had_error = True
        error_at(token, message)
        return LoxParserError(message)

    def synchronize(self):
        while not self.exhausted:
            if self.peek().type == TokenType.SEMICOLON:
                self.consume()
                return
            if self.peek().type in {
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            }:
                return
            self.consume()

    def consume(self):
        if self.exhausted:
            return self.lexer.peek()
        return self.lexer.consume()

    def accept(self, *types: list[TokenType]):
        """Return next token if its type matches; otherwise return None"""
        if self.lexer.peek().type in types:
            return self.consume()

    def expect(self, *types: list[TokenType], message):
        """Return next token if its type matches; otherwise return None"""
        if self.lexer.peek().type in types:
            return self.consume()
        raise self.error(self.lexer.peek(), message)

    def parse(self) -> Expr:
        try:
            return self.expression()
        except LoxParserError as e:
            return None

    def expression(self) -> Expr:
        return self.equality()

    def equality(self) -> Expr:
        """Parse using the equality rule of the grammar
        equality       → comparison ( ( "!=" | "==" ) comparison )* ;
        """
        expr: Expr = self.comparison()
        while operator := self.accept(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        """Parse using the comparion rule of the grammar
        comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
        """
        expr: Expr = self.term()
        required = (
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        )
        while operator := self.accept(*required):
            right: Expr = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        """Parse using the term rule of the grammar
        term            → factor ( ( "-" | "+" ) factor )* ;
        """
        expr: Expr = self.factor()
        required = (TokenType.MINUS, TokenType.PLUS)
        while operator := self.accept(*required):
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        """Parse using the factor rule of the grammar
        factor          → unary ( ( "/" | "*" ) unary )* ;
        """
        expr: Expr = self.unary()
        required = (TokenType.STAR, TokenType.SLASH)
        while operator := self.accept(*required):
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        """Parse using the unary rule of the grammar
        unary           → ( "!" | "-" ) unary | primary;
        """
        if operator := self.accept(TokenType.BANG, TokenType.MINUS):
            right: Expr = self.unary()
            return Unary(operator, right)
        return self.primary()

    def primary(self) -> Expr:
        """Parse using the primary rule of the grammar
        primary         → NUMBER | STRING | "true" | "false" | "nil"
                        | "(" expression ")" ;
        """
        if self.accept(TokenType.FALSE):
            return Literal(False)
        if self.accept(TokenType.TRUE):
            return Literal(True)
        if self.accept(TokenType.NIL):
            return Literal(None)

        if token := self.accept(TokenType.NUMBER, TokenType.STRING):
            return Literal(token.literal)

        if self.accept(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.expect(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)

        raise self.error(self.lexer.peek(), "Expression expected.")
