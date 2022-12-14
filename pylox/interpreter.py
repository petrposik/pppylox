from abc import ABC, abstractmethod
import time

from .ast import *
from .lexer import *
from .errors import *
from .environment import *


class ReturnException(LoxRuntimeError):
    """Lox internal exception used when handling return statement"""

    def __init__(self, value):
        super().__init__(self, None)
        self.value = value


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter: "Interpreter", arguments: list):
        pass

    @abstractmethod
    def arity(self) -> int:
        pass


class Clock(LoxCallable):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: list):
        return time.time()

    def __str__(self):
        return "<native fn>"


class LoxFunction(LoxCallable):
    def __init__(
        self,
        declaration: FunctionStmt,
        closure: Environment,
        is_initializer: bool = False,
    ):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def call(self, interpreter: "Interpreter", arguments: list):
        environment = Environment(self.closure)
        for par, arg in zip(self.declaration.params, arguments):
            environment.define(par.lexeme, arg)
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def bind(self, instance: "LoxInstance") -> "LoxFunction":
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"


class LoxClass(LoxCallable):
    def __init__(
        self, name: str, superclass: "LoxClass", methods: dict[str, LoxFunction]
    ):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def find_method(self, name: str) -> LoxFunction | None:
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.find_method(name)
        return None

    def __str__(self):
        return self.name

    def call(self, interpreter: "Interpreter", arguments: list):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self):
        initializer = self.find_method("init")
        if initializer:
            return initializer.arity()
        return 0


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields = {}

    def __str__(self):
        return f"{self.klass.name} instance"

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method = self.klass.find_method(name.lexeme)
        if method:
            return method.bind(self)
        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value):
        self.fields[name.lexeme] = value


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, lox):
        self.lox = lox
        self.globals = Environment()
        self.environment = self.globals
        self.globals.define("clock", Clock())
        self.locals = {}

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as error:
            self.lox.runtime_error(error)

    # def interpret(self, expression: Expr):
    #     try:
    #         value = self.evaluate(expression)
    #         print(self.stringify(value))
    #     except LoxRuntimeError as e:
    #         self.lox.runtime_error(e)

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def resolve(self, expr: Expr, depth: int) -> None:
        # Expr is mutable, cannot be used as key!!!
        self.locals[expr] = depth

    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def visit_block_stmt(self, stmt: BlockStmt):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_class_stmt(self, stmt: ClassStmt):
        superclass = None
        if stmt.superclass:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise LoxRuntimeError(
                    stmt.superclass.name, "Superclass must be a class."
                )
        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            function = LoxFunction(
                method, self.environment, method.name.lexeme == "init"
            )
            methods[method.name.lexeme] = function
        klass = LoxClass(stmt.name.lexeme, superclass, methods)

        if stmt.superclass:
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, klass)
        return None

    def visit_expr_stmt(self, stmt: ExprStmt) -> None:
        _ = self.evaluate(stmt.expr)
        return None

    def visit_function_stmt(self, stmt: FunctionStmt) -> None:
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visit_if_stmt(self, stmt: IfStmt):
        if self.truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch:
            self.execute(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt: PrintStmt) -> None:
        value = self.evaluate(stmt.expr)
        print(self.stringify(value))
        return None

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        raise ReturnException(value)

    def visit_var_stmt(self, stmt: VarStmt) -> None:
        value = None
        if stmt.initializer:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        while self.truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_assign_expr(self, expr: Assign):
        value = self.evaluate(expr.value)
        distance = self.locals.get(expr, None)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    # def parenthesize(self, name: str, *exprs: list[Expr]):
    #     parts = [f"({name} "]
    #     parts.append(" ".join(expr.accept(self) for expr in exprs))
    #     parts.append(")")
    #     return "".join(parts)

    def visit_binary_expr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        match expr.operator.type:
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(right, str) and isinstance(left, str):
                    return str(left) + str(right)
                raise LoxRuntimeError(
                    expr.operator, "Both operands must be strings or numbers."
                )
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
        # Unreachable.
        return None

    def visit_call_expr(self, expr: Call):
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]
        # Interface LoxCallable? See section 10.1.2
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(
                expr.paren, "Only functions and classes can be called."
            )
        if len(arguments) != callee.arity():
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {callee.arity()} arguments, but got {len(arguments)}.",
            )

        return callee.call(self, arguments)

    def visit_get_expr(self, expr: Get):
        obj = self.evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal):
        return expr.value

    def visit_logical_expr(self, expr: Logical):
        left = self.evaluate(expr.left)
        # Short-circuit if we can
        if expr.operator.type == TokenType.OR:
            if self.truthy(left):
                return left
        elif expr.operator.type == TokenType.AND:
            if not self.truthy(left):
                return left
        else:
            assert False, "Unreachable"
        # Evaluate the second operand if needed
        right = self.evaluate(expr.right)
        return right

    def visit_set_expr(self, expr: Set):
        obj = self.evaluate(expr.obj)
        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")
        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: Super):
        distance = self.locals.get(expr, None)
        superclass: LoxClass = self.environment.get_at(distance, "super")
        obj: LoxInstance = self.environment.get_at(distance - 1, "this")
        method: LoxFunction = superclass.find_method(expr.method.lexeme)
        if not method:
            raise LoxRuntimeError(
                expr.method, f"Undefined property '{expr.method.lexeme}'."
            )
        return method.bind(obj)

    def visit_this_expr(self, expr: This):
        return self.lookup_variable(expr.keyword, expr)

    def visit_unary_expr(self, expr: Unary):
        right = self.evaluate(expr.right)
        match expr.operator.type:
            case TokenType.BANG:
                return not self.truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -right
        # Unreachable.
        return None

    def visit_variable_expr(self, expr: Variable):
        return self.lookup_variable(expr.name, expr)  # self.environment.get(expr.name)

    def lookup_variable(self, name: Token, expr: Expr):
        distance = self.locals.get(expr, None)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def truthy(self, value) -> bool:
        """In Lox, None and False are False, everything else is True."""
        if value is None:
            return False
        if isinstance(value, bool):
            return bool(value)
        return True

    def is_equal(self, a, b) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def stringify(self, value):
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(value)

    def check_number_operand(self, operator: Token, operand):
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be a numbers.")


if __name__ == "__main__":
    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )
    expression = Literal(45.67)
    print(Interpreter().evaluate(expression))
