from .ast import *
from .lexer import *
from .errors import *


class Interpreter(Visitor):
    def __init__(self, lox):
        self.lox = lox

    def interpret(self, expression: Expr):
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except LoxRuntimeError as e:
            self.lox.runtime_error(e)

    def evaluate(self, expr: Expr):
        return expr.accept(self)

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

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal):
        return expr.value

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
