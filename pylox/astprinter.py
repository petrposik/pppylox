from .ast import *
from .lexer import *


class ASTPrinter(ExprVisitor):
    def print(self, expr: Expr):
        return expr.accept(self)

    def parenthesize(self, name: str, *exprs: list[Expr]):
        parts = [f"({name} "]
        parts.append(" ".join(expr.accept(self) for expr in exprs))
        parts.append(")")
        return "".join(parts)

    def visit_binary_expr(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal):
        return "nil" if expr.value == None else str(expr.value)

    def visit_unary_expr(self, expr: Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)


if __name__ == "__main__":
    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )
    print(ASTPrinter().print(expression))
