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


@dataclass(frozen=True)
class Assign(ABC):
    "Assign   : Token name, Expr value",
    name: Token
    value: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_assign_expr(self)


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_binary_expr(self)


@dataclass(frozen=True)
class Logical(Expr):
    # "Logical  : Expr left, Token operator, Expr right"
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_logical_expr(self)


@dataclass(frozen=True)
class Set(Expr):
    # "Set      : Expr object, Token name, Expr value"
    obj: Expr
    name: Token
    value: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_set_expr(self)


@dataclass(frozen=True)
class Super(Expr):
    # "Super    : Token keyword, Token method"
    keyword: Token
    method: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_super_expr(self)


@dataclass(frozen=True)
class This(Expr):
    # "This     : Token keyword"
    keyword: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_this_expr(self)


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_unary_expr(self)


@dataclass(frozen=True)
class Call(Expr):
    # "Call     : Expr callee, Token paren, List<Expr> arguments",
    callee: Expr
    paren: Token
    arguments: list[Expr]

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_call_expr(self)


@dataclass(frozen=True)
class Get(Expr):
    # "Get      : Expr object, Token name"
    obj: Expr
    name: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_get_expr(self)


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_grouping_expr(self)


@dataclass(frozen=True)
class Literal(Expr):
    value: Any

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_literal_expr(self)


# "Variable : Token name"
@dataclass(frozen=True)
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
    def visit_set_expr(self, expr: Set):
        pass

    @abstractmethod
    def visit_super_expr(self, expr: Super):
        pass

    @abstractmethod
    def visit_this_expr(self, expr: This):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: Unary):
        pass

    @abstractmethod
    def visit_call_expr(self, expr: Call):
        pass

    @abstractmethod
    def visit_get_expr(self, expr: Get):
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


@dataclass(frozen=True)
class PrintStmt(Stmt):
    expr: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print_stmt(self)


@dataclass(frozen=True)
class ExprStmt(Stmt):
    expr: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expr_stmt(self)


@dataclass(frozen=True)
class VarStmt(Stmt):
    # "Var        : Token name, Expr initializer"
    name: Token
    initializer: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_var_stmt(self)


@dataclass(frozen=True)
class ClassStmt(Stmt):
    # "Class      : Token name, Expr.Variable superclass, List<Stmt.Function> methods"
    name: Token
    superclass: Variable  # The superclass identifier is evaluated as variable access
    methods: list[FunctionStmt]

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_class_stmt(self)


@dataclass(frozen=True)
class FunctionStmt(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_function_stmt(self)


@dataclass(frozen=True)
class IfStmt(Stmt):
    # "If         : Expr condition, Stmt thenBranch, Stmt elseBranch"
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_if_stmt(self)


@dataclass(frozen=True)
class ReturnStmt(Stmt):
    # "Return     : Token keyword, Expr value"
    keyword: Token
    value: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_return_stmt(self)


@dataclass(frozen=True)
class WhileStmt(Stmt):
    # "While      : Expr condition, Stmt body"
    condition: Expr
    body: Stmt

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_while_stmt(self)


@dataclass(frozen=True)
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

    @abstractmethod
    def visit_class_stmt(self, stmt: ClassStmt):
        pass

    @abstractmethod
    def visit_function_stmt(self, stmt: FunctionStmt):
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt: ReturnStmt):
        pass
