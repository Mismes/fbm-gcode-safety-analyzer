"""Stable diagnostic types and rule metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    WARNING = "warning"
    ERROR = "error"


RULE_DESCRIPTIONS = {
    "GSA001": "Rapid clearance violation",
    "GSA002": "Cutting move without an active spindle",
    "GSA003": "Cutting move without a valid feed rate",
    "GSA004": "Malformed or structurally invalid input",
    "GSA005": "Unsupported or unrecognized command",
    "GSA006": "Unsafe or indeterminate modal transition",
}


@dataclass(frozen=True, slots=True)
class Diagnostic:
    rule: str
    severity: Severity
    line: int
    message: str
    column: int | None = None

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "rule": self.rule,
            "severity": self.severity.value,
            "line": self.line,
            "message": self.message,
        }
        if self.column is not None:
            result["column"] = self.column
        return result
