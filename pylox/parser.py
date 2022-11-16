from .ast import *
from .errors import *
from .lexer import Lexer, TokenType
from .utils import Peekable


class Parser:
    """A recursive descent parser for Lox langugae"""

    def __init__(self, lox, lexer: Lexer):
        self.lox = lox
        self.lexer = Peekable(lexer)
        self.had_error = False

    @property
    def exhausted(self):
        return self.lexer.peek().type == TokenType.EOF

    def error(self, token: Token, message: str) -> LoxParserError:
        self.had_error = True
        self.lox.error_at(token, message)
        return LoxParserError(message)

    def synchronize(self):
        """Skip tokens until the next statement starts"""
        while not self.exhausted:
            if self.lexer.peek().type == TokenType.SEMICOLON:
                self.consume()
                return
            if self.lexer.peek().type in {
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

    def accept(self, types: list[TokenType]):
        """Return next token if its type matches; otherwise return None"""
        if self.lexer.peek().type in types:
            return self.consume()

    def expect(self, types: list[TokenType], message):
        """Return next token if its type matches; otherwise return None"""
        if self.lexer.peek().type in types:
            return self.consume()
        raise self.error(self.lexer.peek(), message)

    def parse(self) -> list[Expr]:
        statements = []
        while not self.exhausted:
            statements.append(self.declaration())
        return statements

        # try:
        #     return self.expression()
        # except LoxParserError as e:
        #     return None

    def expression(self) -> Expr:
        return self.assignment()

    def statement(self) -> Stmt:
        if self.accept((TokenType.PRINT,)):
            return self.print_stmt()
        return self.expr_stmt()

    def declaration(self) -> Stmt:
        try:
            if self.accept((TokenType.VAR,)):
                return self.var_declaration_stmt()
            return self.statement()
        except LoxParserError:
            self.synchronize()
            return None

    def print_stmt(self) -> Stmt:
        value: Expr = self.expression()
        self.expect((TokenType.SEMICOLON,), "Expected ';' after value.")
        return PrintStmt(value)

    def var_declaration_stmt(self) -> Stmt:
        name: Token = self.expect((TokenType.IDENTIFIER,), "Variable name expected.")
        initializer: Expr = None
        if self.accept((TokenType.EQUAL,)):
            initializer = self.expression()
        self.expect((TokenType.SEMICOLON,), "Expected ';' after variable declaration.")
        return VarStmt(name, initializer)

    def expr_stmt(self) -> Stmt:
        expr: Expr = self.expression()
        self.expect((TokenType.SEMICOLON,), "Expected ';' after expression.")
        return ExprStmt(expr)

    def assignment(self) -> Expr:
        expr: Expr = self.equality()
        if equals := self.accept((TokenType.EQUAL,)):
            value: Expr = self.assignment()
            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def equality(self) -> Expr:
        """Parse using the equality rule of the grammar
        equality       → comparison ( ( "!=" | "==" ) comparison )* ;
        """
        expr: Expr = self.comparison()
        while operator := self.accept((TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL)):
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
        while operator := self.accept(required):
            right: Expr = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        """Parse using the term rule of the grammar
        term            → factor ( ( "-" | "+" ) factor )* ;
        """
        expr: Expr = self.factor()
        required = (TokenType.MINUS, TokenType.PLUS)
        while operator := self.accept(required):
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        """Parse using the factor rule of the grammar
        factor          → unary ( ( "/" | "*" ) unary )* ;
        """
        expr: Expr = self.unary()
        required = (TokenType.STAR, TokenType.SLASH)
        while operator := self.accept(required):
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        """Parse using the unary rule of the grammar
        unary           → ( "!" | "-" ) unary | primary;
        """
        if operator := self.accept((TokenType.BANG, TokenType.MINUS)):
            right: Expr = self.unary()
            return Unary(operator, right)
        return self.primary()

    def primary(self) -> Expr:
        """Parse using the primary rule of the grammar
        primary         → NUMBER | STRING | "true" | "false" | "nil"
                        | "(" expression ")" ;
        """
        if self.accept((TokenType.FALSE,)):
            return Literal(False)
        if self.accept((TokenType.TRUE,)):
            return Literal(True)
        if self.accept((TokenType.NIL,)):
            return Literal(None)

        if token := self.accept((TokenType.NUMBER, TokenType.STRING)):
            return Literal(token.literal)

        if token := self.accept((TokenType.IDENTIFIER,)):
            return Variable(token)

        if self.accept((TokenType.LEFT_PAREN,)):
            expr: Expr = self.expression()
            self.expect((TokenType.RIGHT_PAREN,), "Expected ')' after expression.")
            return Grouping(expr)

        raise self.error(self.lexer.peek(), "Expression expected.")
