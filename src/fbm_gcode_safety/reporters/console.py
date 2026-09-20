from __future__ import annotations

from ..analyzer import AnalysisResult


def render(result: AnalysisResult) -> str:
    return "\n".join(
        f"{result.source}:{item.line}: {item.rule} {item.severity.value.upper()} {item.message}"
        for item in result.diagnostics
    )
