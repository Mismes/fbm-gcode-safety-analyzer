"""Coordinate parsing, modal state, and rule evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import MachineProfile, default_profile
from .diagnostics import Diagnostic, Severity
from .modal_state import ModalState
from .parser import parse_text
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
    blocks, diagnostics = parse_text(source)
    state = ModalState()
    for block in blocks:
        diagnostics.extend(evaluate_block(block, state, active_profile))
    return AnalysisResult(source_name, tuple(diagnostics))


def analyze_file(path: str | Path, profile: MachineProfile | None = None) -> AnalysisResult:
    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")
    return analyze_text(text, profile, str(source_path))
