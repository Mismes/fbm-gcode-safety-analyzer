"""Comment-aware tokenizer for a bounded Fanuc-style word syntax."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .diagnostics import Diagnostic, Severity

_NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)")


@dataclass(frozen=True, slots=True)
class Word:
    address: str
    value: float
    raw_value: str
    column: int

    def code(self) -> int | None:
        if self.value.is_integer():
            return int(self.value)
        return None


@dataclass(frozen=True, slots=True)
class Block:
    line: int
    source: str
    words: tuple[Word, ...]


def _remove_comments(source: str, line: int) -> tuple[str, list[Diagnostic]]:
    output: list[str] = []
    diagnostics: list[Diagnostic] = []
    depth = 0
    for column, char in enumerate(source, 1):
        if char == ";" and depth == 0:
            break
        if char == "(":
            if depth:
                diagnostics.append(
                    Diagnostic("GSA004", Severity.ERROR, line, "Nested comment", column)
                )
            depth += 1
            continue
        if char == ")":
            if depth == 0:
                diagnostics.append(
                    Diagnostic("GSA004", Severity.ERROR, line, "Unmatched closing comment", column)
                )
            else:
                depth -= 1
            continue
        output.append(" " if depth else char)
    if depth:
        diagnostics.append(Diagnostic("GSA004", Severity.ERROR, line, "Unclosed comment"))
    return "".join(output), diagnostics


def parse_line(source: str, line: int) -> tuple[Block | None, list[Diagnostic]]:
    cleaned, diagnostics = _remove_comments(source.rstrip("\r\n"), line)
    if diagnostics:
        return None, diagnostics
    if not cleaned.strip() or cleaned.strip() == "%":
        return Block(line, source.rstrip("\r\n"), ()), []

    words: list[Word] = []
    position = 0
    while position < len(cleaned):
        char = cleaned[position]
        if char.isspace():
            position += 1
            continue
        if not char.isalpha():
            diagnostics.append(
                Diagnostic(
                    "GSA004", Severity.ERROR, line, f"Unexpected character {char!r}", position + 1
                )
            )
            position += 1
            continue
        address = char.upper()
        number = _NUMBER.match(cleaned, position + 1)
        if number is None:
            diagnostics.append(
                Diagnostic(
                    "GSA004",
                    Severity.ERROR,
                    line,
                    f"Word {address} has no valid numeric value",
                    position + 1,
                )
            )
            position += 1
            while position < len(cleaned) and not cleaned[position].isspace():
                position += 1
            continue
        raw_value = number.group(0)
        words.append(Word(address, float(raw_value), raw_value, position + 1))
        position = number.end()

    if diagnostics:
        return None, diagnostics
    line_numbers = [word for word in words if word.address == "N"]
    if len(line_numbers) > 1:
        diagnostics.append(
            Diagnostic("GSA004", Severity.ERROR, line, "Multiple line numbers in one block")
        )
    elif line_numbers:
        word = line_numbers[0]
        if words[0] is not word or word.code() is None or word.value < 0:
            diagnostics.append(
                Diagnostic(
                    "GSA004",
                    Severity.ERROR,
                    line,
                    "Line number must be one non-negative integer at the start of a block",
                    word.column,
                )
            )
    if diagnostics:
        return None, diagnostics
    return Block(line, source.rstrip("\r\n"), tuple(words)), []


def parse_text(source: str) -> tuple[list[Block], list[Diagnostic]]:
    blocks: list[Block] = []
    diagnostics: list[Diagnostic] = []
    for line_number, line in enumerate(source.splitlines(), 1):
        block, line_diagnostics = parse_line(line, line_number)
        diagnostics.extend(line_diagnostics)
        if block is not None:
            blocks.append(block)
    return blocks, diagnostics
