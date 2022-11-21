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
class Assign(ABC):
    "Assign   : Token name, Expr value",
    name: Token
    value: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_assign_expr(self)


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_binary_expr(self)


@dataclass
class Logical(Expr):
    # "Logical  : Expr left, Token operator, Expr right"
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_logical_expr(self)


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


# "Variable : Token name"
@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_variable_expr(self)


class ExprVisitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: Assign):
        pass

    @abstractmethod
    def visit_binary_expr(self, expr: Binary):
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: Logical):
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

    @abstractmethod
    def visit_variable_expr(self, expr: Variable):
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


@dataclass
class VarStmt(Stmt):
    # "Var        : Token name, Expr initializer"
    name: Token
    initializer: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_var_stmt(self)


@dataclass
class IfStmt(Stmt):
    # "If         : Expr condition, Stmt thenBranch, Stmt elseBranch"
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_if_stmt(self)


@dataclass
class WhileStmt(Stmt):
    # "While      : Expr condition, Stmt body"
    condition: Expr
    body: Stmt

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_while_stmt(self)


@dataclass
class BlockStmt(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_block_stmt(self)


class StmtVisitor(ABC):
    @abstractmethod
    def visit_print_stmt(self, stmt: PrintStmt):
        pass

    @abstractmethod
    def visit_expr_stmt(self, stmt: ExprStmt):
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: VarStmt):
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt: BlockStmt):
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: IfStmt):
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: WhileStmt):
        pass
