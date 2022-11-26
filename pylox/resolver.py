from enum import Enum

from .ast import *
from .interpreter import Interpreter


class FunctionType(Enum):
    NONE = 0
    FUNCTION = 1
    METHOD = 2
    INITIALIZER = 3


class ClassType(Enum):
    NONE = 0
    CLASS = 1


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, lox, interpreter: Interpreter):
        self.lox = lox
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def resolve(self, what):
        if isinstance(what, list):
            for stmt in what:
                self.resolve(stmt)
        elif isinstance(what, Stmt):
            what.accept(self)
        elif isinstance(what, Expr):
            what.accept(self)
        else:
            assert False, "Unreachable"

    def visit_block_stmt(self, stmt: BlockStmt):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def visit_class_stmt(self, stmt: ClassStmt):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        self.begin_scope()
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)
        self.end_scope()
        self.current_class = enclosing_class
        return None

    def visit_var_stmt(self, stmt: VarStmt):
        self.declare(stmt.name)
        if stmt.initializer:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
        return None

    def declare(self, name: Token):
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.lox.error_at(name, "This name is already used in this scope.")
        scope[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def visit_variable_expr(self, expr: Variable):
        if (
            self.scopes
            and expr.name.lexeme in self.scopes[-1]
            and self.scopes[-1][expr.name.lexeme] == False
        ):
            self.lox.error_at(
                expr.name, "Can't read local variable in its own initializer."
            )
        self.resolve_local(expr, expr.name)
        return None

    def resolve_local(self, expr: Expr, name: Token):
        for i, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, i)
                return None

    # private void resolveLocal(Expr expr, Token name) {
    #     for (int i = scopes.size() - 1; i >= 0; i--) {
    #       if (scopes.get(i).containsKey(name.lexeme)) {
    #         interpreter.resolve(expr, scopes.size() - 1 - i);
    #         return;
    #       }
    #     }
    #   }

    def visit_assign_expr(self, expr: Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
        return None

    def visit_function_stmt(self, stmt: FunctionStmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)
        return None

    def resolve_function(self, function: FunctionStmt, type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def visit_expr_stmt(self, stmt: ExprStmt):
        self.resolve(stmt.expr)
        return None

    def visit_if_stmt(self, stmt: IfStmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch:
            self.resolve(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt: PrintStmt):
        self.resolve(stmt.expr)
        return None

    def visit_return_stmt(self, stmt: ReturnStmt):
        if self.current_function == FunctionType.NONE:
            self.lox.error(stmt.keyword, "Can't return from top-level code.")
        if stmt.value:
            if self.current_function == FunctionType.INITIALIZER:
                self.lox.error_at(
                    stmt.keyword, "Can't return a value from an initializer."
                )
            self.resolve(stmt.value)
        return None

    def visit_while_stmt(self, stmt: WhileStmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None

    def visit_binary_expr(self, expr: Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visit_call_expr(self, expr: Call):
        self.resolve(expr.callee)
        for arg in expr.arguments:
            self.resolve(arg)
        return None

    def visit_get_expr(self, expr: Get):
        self.resolve(expr.obj)
        return None

    def visit_grouping_expr(self, expr: Grouping):
        self.resolve(expr.expression)
        return None

    def visit_literal_expr(self, expr: Literal):
        return None

    def visit_logical_expr(self, expr: Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visit_set_expr(self, expr: Set):
        self.resolve(expr.value)
        self.resolve(expr.obj)
        return None

    def visit_this_expr(self, expr: This):
        if self.current_class == ClassType.NONE:
            self.lox.error(expr.keyword, "Can't you 'this' outside of a class.")
        self.resolve_local(expr, expr.keyword)
        return None

    def visit_unary_expr(self, expr: Unary):
        self.resolve(expr.right)
        return None
