#
#   Create/src/evaluator.py
#
#   Creator: Aleksander Sapieha (sourceguy68@gmail.com)
#
#   Contributors:
#   Aleksander Sapieha (sourceguy68@gmail.com)
#


import operator

from lexer import Lexer
from parser import Parser
from errors import PyCreateNameError, PyCreateRuntimeError


BINARY_OPERATORS = {
    "+": operator.add, "-": operator.sub, "*": operator.mul,
    "/": operator.truediv, "//": operator.floordiv, "%": operator.mod,
    "==": operator.eq, "!=": operator.ne, "<": operator.lt,
    "<=": operator.le, ">": operator.gt, ">=": operator.ge,
}


class PyCreateInterpreter:
    """Executes the supported PyCreate language."""

    def __init__(self, commands_module):
        self.variables = {}
        self.api = {"print": print}

        allowed_commands = (
            "pycreate_init", "set_script", "add_file",
            "set_name", "set_onefile", "set_console", "build",
        )

        for name in allowed_commands:
            function = getattr(commands_module, name, None)
            if callable(function):
                self.api[name] = function

    def run(self, source, filename="<string>"):
        statements = Parser(Lexer(source).tokenize()).parse()
        self._execute_statements(statements, filename)

    def _execute_statements(self, statements, filename):
        for statement in statements:
            try:
                self._execute_statement(statement, filename)
            except Exception as error:
                line = statement[-1]
                raise PyCreateRuntimeError(
                    f"{filename}:{line}: {error}"
                ) from error

    def _execute_statement(self, statement, filename):
        kind = statement[0]

        if kind == "assign":
            _, name, expression, _line = statement
            self.variables[name] = self._evaluate(expression)
            return

        if kind == "expression":
            self._evaluate(statement[1])
            return

        if kind == "if":
            _, branches, else_body, _line = statement

            for condition, body in branches:
                if self._evaluate(condition):
                    self._execute_statements(body, filename)
                    return

            if else_body is not None:
                self._execute_statements(else_body, filename)
            return

        raise PyCreateRuntimeError(f"Unknown statement type: {kind}")

    def _evaluate(self, node):
        kind = node[0]

        if kind == "literal":
            return node[1]

        if kind == "variable":
            name = node[1]
            if name not in self.variables:
                raise PyCreateNameError(f"Undefined variable: {name}")
            return self.variables[name]

        if kind == "list":
            return [self._evaluate(item) for item in node[1]]

        if kind == "tuple":
            return tuple(self._evaluate(item) for item in node[1])

        if kind == "dict":
            return {
                self._evaluate(key): self._evaluate(value)
                for key, value in node[1]
            }

        if kind == "call":
            _, name, arguments, keywords, _line = node
            if name not in self.api:
                raise PyCreateNameError(
                    f"Function is not available in PyCreate: {name}"
                )
            args = [self._evaluate(argument) for argument in arguments]
            kwargs = {key: self._evaluate(value) for key, value in keywords}
            return self.api[name](*args, **kwargs)

        if kind == "unary":
            _, operation, expression, _line = node
            value = self._evaluate(expression)
            if operation == "-":
                return -value
            if operation == "+":
                return +value
            if operation == "not":
                return not value

        if kind == "binary":
            _, operation, left_node, right_node, _line = node
            left = self._evaluate(left_node)

            if operation == "and":
                return self._evaluate(right_node) if left else left
            if operation == "or":
                return left if left else self._evaluate(right_node)

            right = self._evaluate(right_node)
            if operation not in BINARY_OPERATORS:
                raise PyCreateRuntimeError(f"Unsupported operator: {operation}")
            return BINARY_OPERATORS[operation](left, right)

        raise PyCreateRuntimeError(f"Unknown expression type: {kind}")
