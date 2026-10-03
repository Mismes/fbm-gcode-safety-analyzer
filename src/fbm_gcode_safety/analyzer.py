"""Coordinate parsing, modal state, and rule evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import MachineProfile, default_profile
from .diagnostics import Diagnostic, Severity
from .modal_state import ModalState
from .parser import parse_line
from .rules import evaluate_block


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    source: str
    diagnostics: tuple[Diagnostic, ...]

    @property
    def status(self) -> str:
        has_error = any(item.severity == Severity.ERROR for item in self.diagnostics)
        return "failed" if has_error else "passed"


def analyze_text(
    source: str,
    profile: MachineProfile | None = None,
    source_name: str = "<memory>",
) -> AnalysisResult:
    active_profile = profile or default_profile()
    diagnostics: list[Diagnostic] = []
    state = ModalState()
    has_words = False
    for number, line in enumerate(source.splitlines(), 1):
        block, errors = parse_line(line, number)
        diagnostics.extend(errors)
        if block is None:
            state = ModalState()
            continue
        has_words = has_words or any(word.address != "N" for word in block.words)
        diagnostics.extend(evaluate_block(block, state, active_profile))
    if not has_words and not diagnostics:
        diagnostics.append(
            Diagnostic("GSA004", Severity.ERROR, 1, "Input contains no executable words")
        )
    return AnalysisResult(source_name, tuple(diagnostics))


def analyze_file(path: str | Path, profile: MachineProfile | None = None) -> AnalysisResult:
    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8-sig")
    return analyze_text(text, profile, str(source_path))
