from dataclasses import dataclass
from typing import Any

from .lexer import Token


class Expr:
    def accept(visitor: Visitor):
        raise NotImplementedError


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_binary_expr(self)


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_unary_expr(self)


@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_grouping_expr(self)


@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor: Visitor):
        return visitor.visit_literal_expr(self)


class Visitor:
    def visit_binary_expr(self, expr: Binary):
        raise NotImplementedError

    def visit_unary_expr(self, expr: Unary):
        raise NotImplementedError

    def visit_grouping_expr(self, expr: Grouping):
        raise NotImplementedError

    def visit_literal_expr(self, expr: Literal):
        raise NotImplementedError
