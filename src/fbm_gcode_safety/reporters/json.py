from __future__ import annotations

import json

from ..analyzer import AnalysisResult


def render(result: AnalysisResult) -> str:
    return json.dumps(
        {
            "status": result.status,
            "source": result.source,
            "diagnostics": [item.to_dict() for item in result.diagnostics],
        },
        indent=2,
        ensure_ascii=False,
    )
