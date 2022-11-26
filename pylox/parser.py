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
        if self.accept((TokenType.FOR,)):
            return self.for_stmt()
        if self.accept((TokenType.IF,)):
            return self.if_stmt()
        if self.accept((TokenType.PRINT,)):
            return self.print_stmt()
        if self.lexer.peek().type == TokenType.RETURN:  # Intentionally different
            return self.return_stmt()
        if self.accept((TokenType.WHILE,)):
            return self.while_stmt()
        if self.accept((TokenType.LEFT_BRACE,)):
            return self.block_stmt()
        return self.expr_stmt()

    def for_stmt(self) -> Stmt:
        # Parse the for loop, but return the equivalent while loop AST
        self.expect((TokenType.LEFT_PAREN,), "Expected '(' after 'for'.")
        initializer: Stmt = None
        if self.accept((TokenType.SEMICOLON,)):
            initializer = None
        elif self.accept((TokenType.VAR,)):
            initializer = self.var_declaration()
        else:
            initializer = self.expr_stmt()

        condition: Expr = None
        if not self.lexer.peek().type == TokenType.SEMICOLON:
            condition = self.expression()
        self.expect((TokenType.SEMICOLON,), "Expected ';' after loop contition.")

        increment: Expr = None
        if not self.lexer.peek().type == TokenType.RIGHT_PAREN:
            increment = self.expression()
        self.expect((TokenType.RIGHT_PAREN,), "Expected ')' after for clauses.")

        body = self.statement()

        # The for loop is parsed, start building the 'while' AST

        if increment:
            body = BlockStmt([body, ExprStmt(increment)])
        if not condition:
            condition = Literal(True)
        body = WhileStmt(condition, body)
        if initializer:
            body = BlockStmt([initializer, body])

        return body

    def if_stmt(self) -> Stmt:
        self.expect((TokenType.LEFT_PAREN,), "Expected '(' after 'if'.")
        condition = self.expression()
        self.expect((TokenType.RIGHT_PAREN,), "Expected ')' after if contidion.")
        then_branch = self.statement()
        else_branch = None
        if self.accept((TokenType.ELSE,)):
            else_branch = self.statement()
        return IfStmt(condition, then_branch, else_branch)

    def declaration(self) -> Stmt:
        try:
            if self.accept((TokenType.CLASS,)):
                return self.class_declaration()
            if self.accept((TokenType.FUN,)):
                return self.function_declaration("function")
            if self.accept((TokenType.VAR,)):
                return self.var_declaration()
            return self.statement()
        except LoxParserError:
            self.synchronize()
            return None

    def class_declaration(self) -> ClassStmt:
        name = self.expect((TokenType.IDENTIFIER,), "Expected class name.")
        self.expect((TokenType.LEFT_BRACE,), "Expected '{' after class name.")
        methods = []
        while self.lexer.peek().type != TokenType.RIGHT_BRACE and not self.exhausted:
            methods.append(self.function_declaration("method"))
        self.expect((TokenType.RIGHT_BRACE,), "Expected '}' after class body.")
        return ClassStmt(name, methods)

    def print_stmt(self) -> Stmt:
        value: Expr = self.expression()
        self.expect((TokenType.SEMICOLON,), "Expected ';' after value.")
        return PrintStmt(value)

    def return_stmt(self) -> ReturnStmt:
        keyword: Token = self.accept((TokenType.RETURN,))
        value: Expr = None
        if self.lexer.peek().type != TokenType.SEMICOLON:
            value = self.expression()
        self.expect((TokenType.SEMICOLON,), "Expected ';' after return value.")
        return ReturnStmt(keyword, value)

    def var_declaration(self) -> Stmt:
        name: Token = self.expect((TokenType.IDENTIFIER,), "Variable name expected.")
        initializer: Expr = None
        if self.accept((TokenType.EQUAL,)):
            initializer = self.expression()
        self.expect((TokenType.SEMICOLON,), "Expected ';' after variable declaration.")
        return VarStmt(name, initializer)

    def while_stmt(self) -> Stmt:
        self.expect((TokenType.LEFT_PAREN,), "Expected '(' after 'while'.")
        condition = self.expression()
        self.expect((TokenType.RIGHT_PAREN,), "Expected ')' after condition.")
        body = self.statement()
        return WhileStmt(condition, body)

    def expr_stmt(self) -> Stmt:
        expr: Expr = self.expression()
        self.expect((TokenType.SEMICOLON,), "Expected ';' after expression.")
        return ExprStmt(expr)

    def function_declaration(self, kind: str) -> FunctionStmt:
        name: Token = self.expect((TokenType.IDENTIFIER,), f"Expected {kind} name.")
        self.expect((TokenType.LEFT_PAREN,), f"Expected '(' after {kind} name.")
        parameters = []
        if not self.lexer.peek().type == TokenType.RIGHT_PAREN:
            while True:
                if len(parameters) >= 255:
                    self.error(
                        self.lexer.peek(), "Can't have more than 255 parameters."
                    )
                parameters.append(
                    self.expect((TokenType.IDENTIFIER,), "Expected parameter name.")
                )
                if not self.accept((TokenType.COMMA,)):
                    break
        self.expect((TokenType.RIGHT_PAREN,), "Expected ')' after parameters.")
        self.expect((TokenType.LEFT_BRACE,), f"Expected '{{' before {kind} body.")
        body = self.block_stmt()
        return FunctionStmt(name, parameters, body.statements)

    def block_stmt(self) -> BlockStmt:
        statements: list[Stmt] = []
        while not self.exhausted and self.lexer.peek().type != TokenType.RIGHT_BRACE:
            statements.append(self.declaration())
        self.expect((TokenType.RIGHT_BRACE,), "Expected '}' after block.")
        return BlockStmt(statements)

    def assignment(self) -> Expr:
        expr: Expr = self.logical_or()
        if equals := self.accept((TokenType.EQUAL,)):
            value: Expr = self.assignment()
            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.obj, expr.name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def logical_or(self) -> Expr:
        expr = self.logical_and()
        while operator := self.accept((TokenType.OR,)):
            right = self.logical_and()
            expr = Logical(expr, operator, right)
        return expr

    def logical_and(self) -> Expr:
        expr = self.equality()
        while operator := self.accept((TokenType.AND,)):
            right = self.equality()
            expr = Logical(expr, operator, right)
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
        return self.call()

    def call(self) -> Expr:
        expr = self.primary()
        while True:
            if self.accept((TokenType.LEFT_PAREN,)):
                expr = self.finish_call(expr)
            elif self.accept((TokenType.DOT,)):
                name = self.expect(
                    (TokenType.IDENTIFIER,), "Expected property name after '.'."
                )
                expr = Get(expr, name)
            else:
                break
        return expr

    def finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self.lexer.peek().type == TokenType.RIGHT_PAREN:
            while True:
                if len(arguments) >= 255:
                    self.error(self.lexer.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.accept((TokenType.COMMA,)):
                    break
        paren = self.expect((TokenType.RIGHT_PAREN,), "Expected ')' after arguments.")
        return Call(callee, paren, arguments)

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
