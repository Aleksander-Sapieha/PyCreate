#
#   Create/src/pycreate.py
#
#   Creator: Aleksander Sapieha (sourceguy68@gmail.com)
#
#   Contributors:
#   Aleksander Sapieha (sourceguy68@gmail.com)
#

from errors import PyCreateSyntaxError
import commands
from lexer import Lexer
import sys
import os
import commands

from evaluator import PyCreateInterpreter


class Create:
    """Parser for PyCreate statements and expressions."""

    PRECEDENCE = {
        "or": 1, "and": 2,
        "==": 3, "!=": 3, "<": 3, "<=": 3, ">": 3, ">=": 3,
        "+": 4, "-": 4,
        "*": 5, "/": 5, "//": 5, "%": 5,
    }

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def _current(self):
        return self.tokens[self.position]

    def _advance(self):
        token = self._current()
        if token.kind != "EOF":
            self.position += 1
        return token

    def _match(self, kind, value=None):
        token = self._current()
        if token.kind == kind and (value is None or token.value == value):
            self._advance()
            return True
        return False

    def _expect(self, kind, value=None):
        token = self._current()
        if token.kind != kind or (value is not None and token.value != value):
            expected = value if value is not None else kind
            raise PyCreateSyntaxError(
                f"Expected {expected!r} at line {token.line}, column {token.column}"
            )
        return self._advance()

    def parse(self):
        statements = self._parse_statements(until="EOF")
        self._expect("EOF")
        return statements

    def _parse_statements(self, until):
        statements = []
        while self._current().kind != until:
            if self._current().kind == "EOF":
                token = self._current()
                raise PyCreateSyntaxError(
                    f"Unexpected end of file at line {token.line}"
                )
            if self._match("NEWLINE") or self._match("PUNCT", ";"):
                continue
            statements.append(self._statement())
            if self._current().kind not in ("NEWLINE", "DEDENT", "EOF"):
                if not self._match("PUNCT", ";"):
                    token = self._current()
                    raise PyCreateSyntaxError(
                        f"Expected end of statement at line {token.line}, "
                        f"column {token.column}"
                    )
        return statements

    def _parse_block(self):
        self._expect("PUNCT", ":")
        self._expect("NEWLINE")
        self._expect("INDENT")
        body = self._parse_statements("DEDENT")
        self._expect("DEDENT")
        return body

    def _statement(self):
        token = self._current()

        if token.kind == "IDENT" and token.value == "if":
            return self._if_statement()

        if (
            token.kind == "IDENT"
            and self.tokens[self.position + 1].kind == "OP"
            and self.tokens[self.position + 1].value == "="
        ):
            name = self._advance()
            self._advance()
            expression = self._expression()
            return ("assign", name.value, expression, name.line)

        expression = self._expression()
        return ("expression", expression, token.line)

    def _if_statement(self):
        start = self._expect("IDENT", "if")
        condition = self._expression()
        body = self._parse_block()
        branches = [(condition, body)]
        else_body = None

        while self._current().kind == "IDENT" and self._current().value in ("elif", "else"):
            keyword = self._advance()

            if keyword.value == "elif":
                condition = self._expression()
                body = self._parse_block()
                branches.append((condition, body))
            else:
                else_body = self._parse_block()
                break

        return ("if", branches, else_body, start.line)

    def _expression(self, minimum_precedence=0):
        left = self._prefix()

        while True:
            token = self._current()
            operator = token.value if token.kind in ("OP", "AND", "OR") else token.kind
            precedence = self.PRECEDENCE.get(operator, -1)

            if precedence < minimum_precedence:
                break

            self._advance()
            right = self._expression(precedence + 1)
            left = ("binary", operator, left, right, token.line)

        return left

    def _prefix(self):
        token = self._advance()

        if token.kind in ("NUMBER", "STRING"):
            node = ("literal", token.value, token.line)
        elif token.kind == "TRUE":
            node = ("literal", True, token.line)
        elif token.kind == "FALSE":
            node = ("literal", False, token.line)
        elif token.kind == "NONE":
            node = ("literal", None, token.line)
        elif token.kind == "IDENT":
            node = ("variable", token.value, token.line)
        elif token.kind == "NOT":
            node = ("unary", "not", self._expression(6), token.line)
        elif token.kind == "OP" and token.value in ("+", "-"):
            node = ("unary", token.value, self._expression(6), token.line)
        elif token.kind == "PUNCT" and token.value == "(":
            node = self._parenthesized(token)
        elif token.kind == "PUNCT" and token.value == "[":
            node = self._list(token)
        elif token.kind == "PUNCT" and token.value == "{":
            node = self._dict(token)
        else:
            raise PyCreateSyntaxError(
                f"Unexpected token {token.value!r} at line {token.line}, "
                f"column {token.column}"
            )

        while self._match("PUNCT", "("):
            if node[0] != "variable":
                current = self._current()
                raise PyCreateSyntaxError(
                    f"Only named functions can be called at line {current.line}"
                )
            node = self._call(node)

        return node

    def _parenthesized(self, opening):
        if self._match("PUNCT", ")"):
            return ("tuple", [], opening.line)
        first = self._expression()
        if not self._match("PUNCT", ","):
            self._expect("PUNCT", ")")
            return first
        values = [first]
        while True:
            if self._match("PUNCT", ")"):
                break
            values.append(self._expression())
            if not self._match("PUNCT", ","):
                self._expect("PUNCT", ")")
                break
        return ("tuple", values, opening.line)

    def _list(self, opening):
        values = []
        if self._match("PUNCT", "]"):
            return ("list", values, opening.line)
        while True:
            values.append(self._expression())
            if self._match("PUNCT", "]"):
                break
            self._expect("PUNCT", ",")
            if self._match("PUNCT", "]"):
                break
        return ("list", values, opening.line)

    def _dict(self, opening):
        pairs = []
        if self._match("PUNCT", "}"):
            return ("dict", pairs, opening.line)
        while True:
            key = self._expression()
            self._expect("PUNCT", ":")
            value = self._expression()
            pairs.append((key, value))
            if self._match("PUNCT", "}"):
                break
            self._expect("PUNCT", ",")
            if self._match("PUNCT", "}"):
                break
        return ("dict", pairs, opening.line)

    def _call(self, function_node):
        arguments = []
        keywords = []

        if self._match("PUNCT", ")"):
            return ("call", function_node[1], arguments, keywords, function_node[2])

        while True:
            if (
                self._current().kind == "IDENT"
                and self.tokens[self.position + 1].kind == "OP"
                and self.tokens[self.position + 1].value == "="
            ):
                name = self._advance().value
                self._advance()
                keywords.append((name, self._expression()))
            else:
                if keywords:
                    token = self._current()
                    raise PyCreateSyntaxError(
                        f"Positional argument follows keyword argument at line {token.line}"
                    )
                arguments.append(self._expression())

            if self._match("PUNCT", ")"):
                break
            self._expect("PUNCT", ",")

        return ("call", function_node[1], arguments, keywords, function_node[2])


def main():
    if len(sys.argv) < 2:
        print("Usage: pycreate <file.pym>")
        return 1

    path = sys.argv[1]

    if not os.path.isfile(path):
        print(f"Error: File not found: {path}")
        return 1

    if not path.endswith(".pym"):
        print("Error: Expected a .pym file")
        return 1

    try:
        with open(path, "r", encoding="utf-8") as file:
            source = file.read()

        interpreter = PyCreateInterpreter(commands)
        interpreter.run(source, filename=path)

        return 0

    except Exception as error:
        print(f"PyCreate Error: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())