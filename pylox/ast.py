from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from abc import ABC, abstractmethod

from .lexer import Token


# Expressions
class Expr(ABC):
    @abstractmethod
    def accept(visitor: ExprVisitor):
        pass


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_binary_expr(self)


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_unary_expr(self)


@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_grouping_expr(self)


@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_literal_expr(self)


class ExprVisitor(ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: Binary):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: Unary):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping):
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: Literal):
        pass


# Statements


class Stmt(ABC):
    @abstractmethod
    def accept(visitor: StmtVisitor):
        pass


@dataclass
class PrintStmt(Stmt):
    expr: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print_stmt(self)


@dataclass
class ExprStmt(Stmt):
    expr: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expr_stmt(self)


class StmtVisitor(ABC):
    @abstractmethod
    def visit_print_stmt(self, stmt: PrintStmt):
        pass

    @abstractmethod
    def visit_expr_stmt(self, expr: ExprStmt):
        pass
