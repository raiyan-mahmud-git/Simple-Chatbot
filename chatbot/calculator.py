"""A small, safe calculator.

It parses the math with Python's `ast` module and only accepts numbers and
basic operators, so it never calls eval() on user input.
"""

import ast
import math
import operator

MAX_EXPRESSION_LENGTH = 200
MAX_EXPONENT = 100


class CalculatorError(Exception):
    """Raised with a friendly message when a calculation can't be done."""


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def calculate(expression):
    """Evaluate a math expression such as '2 + 3 * (4 - 1)' and return a number."""
    expression = expression.replace("^", "**").strip()
    if not expression or len(expression) > MAX_EXPRESSION_LENGTH:
        raise CalculatorError("That doesn't look like a valid calculation.")
    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        raise CalculatorError("That doesn't look like a valid calculation.") from None
    return _evaluate(tree.body)


def _evaluate(node):
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    ):
        return node.value

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise CalculatorError("That exponent is too big for me.")
        try:
            result = _BINARY_OPERATORS[type(node.op)](left, right)
        except ZeroDivisionError:
            raise CalculatorError("I can't divide by zero.") from None
        except OverflowError:
            raise CalculatorError("That number is too big for me.") from None
        if isinstance(result, complex):
            raise CalculatorError("I can only work with real numbers.")
        return result

    raise CalculatorError("I can only do basic math: + - * / % ^ and parentheses.")


def format_number(value):
    """Show 2.0 as '2' and 0.1 + 0.2 as '0.3' instead of '0.30000000000000004'."""
    if isinstance(value, float):
        if math.isinf(value) or math.isnan(value):
            raise CalculatorError("That number is too big for me.")
        if value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        return str(round(value, 6))
    return str(value)
