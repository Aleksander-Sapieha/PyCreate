#
#   Create/src/lexer.py
#
#   Creator: Aleksander Sapieha (sourceguy68@gmail.com)
#
#   Contributors:
#   Aleksander Sapieha (sourceguy68@gmail.com)
#


from dataclasses import dataclass

from errors import PyCreateSyntaxError


@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int


KEYWORDS = {
    "True": "TRUE",
    "False": "FALSE",
    "None": "NONE",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
}


class Lexer:
    """Turns PyCreate source text into tokens, including indentation."""

    TWO_CHAR = {"==", "!=", "<=", ">=", "//"}
    SINGLE_CHAR = set("+-*/%()[]{}:,;=<>")

    def __init__(self, source):
        self.source = source
        self.index = 0
        self.line = 1
        self.column = 1
        self.indents = [0]
        self.at_line_start = True

    def _peek(self, offset=0):
        position = self.index + offset
        if position >= len(self.source):
            return ""
        return self.source[position]

    def _advance(self):
        char = self._peek()
        if char:
            self.index += 1
            if char == "\n":
                self.line += 1
                self.column = 1
                self.at_line_start = True
            else:
                self.column += 1
        return char

    def _token(self, kind, value, line, column):
        return Token(kind, value, line, column)

    def tokenize(self):
        tokens = []

        while self._peek():
            if self.at_line_start:
                self._handle_indentation(tokens)
                if not self._peek():
                    break

            char = self._peek()

            if char in " \t\r":
                self._advance()
                continue

            if char == "\n":
                line, column = self.line, self.column
                self._advance()
                tokens.append(self._token("NEWLINE", "\n", line, column))
                continue

            if char == "#":
                while self._peek() and self._peek() != "\n":
                    self._advance()
                continue

            line, column = self.line, self.column

            if char.isdigit():
                tokens.append(self._number(line, column))
                continue

            if char.isalpha() or char == "_":
                tokens.append(self._identifier(line, column))
                continue

            if char in "\"'":
                tokens.append(self._string(line, column))
                continue

            pair = char + self._peek(1)
            if pair in self.TWO_CHAR:
                self._advance()
                self._advance()
                tokens.append(self._token("OP", pair, line, column))
                continue

            if char in self.SINGLE_CHAR:
                self._advance()
                kind = "PUNCT" if char in "()[]{}:,;" else "OP"
                tokens.append(self._token(kind, char, line, column))
                continue

            raise PyCreateSyntaxError(
                f"Unexpected character {char!r} at line {line}, column {column}"
            )

        while len(self.indents) > 1:
            self.indents.pop()
            tokens.append(self._token("DEDENT", None, self.line, self.column))

        tokens.append(self._token("EOF", None, self.line, self.column))
        return tokens

    def _handle_indentation(self, tokens):
        line, column = self.line, self.column
        width = 0

        while self._peek() in (" ", "\t"):
            char = self._advance()
            width += 1 if char == " " else 4

        # Blank and comment-only lines do not affect indentation.
        if self._peek() in ("", "\n", "#"):
            self.at_line_start = False
            return

        self.at_line_start = False
        current = self.indents[-1]

        if width > current:
            self.indents.append(width)
            tokens.append(self._token("INDENT", width, line, column))
        elif width < current:
            while len(self.indents) > 1 and width < self.indents[-1]:
                self.indents.pop()
                tokens.append(self._token("DEDENT", width, line, column))

            if width != self.indents[-1]:
                raise PyCreateSyntaxError(
                    f"Inconsistent indentation at line {line}"
                )

    def _number(self, line, column):
        start = self.index
        while self._peek().isdigit():
            self._advance()

        is_float = False
        if self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()

        raw = self.source[start:self.index]
        value = float(raw) if is_float else int(raw)
        return self._token("NUMBER", value, line, column)

    def _identifier(self, line, column):
        start = self.index
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        value = self.source[start:self.index]
        kind = KEYWORDS.get(value, "IDENT")
        return self._token(kind, value, line, column)

    def _string(self, line, column):
        quote = self._advance()
        chars = []

        while self._peek() and self._peek() != quote:
            char = self._advance()

            if char == "\n":
                raise PyCreateSyntaxError(
                    f"Unterminated string at line {line}, column {column}"
                )

            if char == "\\":
                escaped = self._advance()
                escapes = {
                    "n": "\n", "t": "\t", "r": "\r",
                    "\\": "\\", "'": "'", '"': '"',
                }
                if escaped not in escapes:
                    raise PyCreateSyntaxError(
                        f"Unsupported escape sequence at line {self.line}"
                    )
                chars.append(escapes[escaped])
            else:
                chars.append(char)

        if self._peek() != quote:
            raise PyCreateSyntaxError(
                f"Unterminated string at line {line}, column {column}"
            )

        self._advance()
        return self._token("STRING", "".join(chars), line, column)
