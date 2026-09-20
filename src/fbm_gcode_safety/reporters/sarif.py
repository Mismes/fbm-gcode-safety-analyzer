"""SARIF 2.1.0 reporter suitable for GitHub code scanning upload."""

from __future__ import annotations

import json
from pathlib import Path

from .. import __version__
from ..analyzer import AnalysisResult
from ..diagnostics import RULE_DESCRIPTIONS, Severity


def _uri(source: str) -> str:
    path = Path(source)
    try:
        return path.resolve().as_uri()
    except (OSError, ValueError):
        return source.replace("\\", "/")


def render(result: AnalysisResult) -> str:
    used_rules = sorted({item.rule for item in result.diagnostics})
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "FBM G-code Safety Analyzer",
                        "version": __version__,
                        "informationUri": "https://github.com/Mismes/fbm-gcode-safety-analyzer",
                        "rules": [
                            {
                                "id": rule,
                                "shortDescription": {"text": RULE_DESCRIPTIONS[rule]},
                            }
                            for rule in used_rules
                        ],
                    }
                },
                "results": [
                    {
                        "ruleId": item.rule,
                        "level": "error" if item.severity == Severity.ERROR else "warning",
                        "message": {"text": item.message},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": _uri(result.source)},
                                    "region": {
                                        "startLine": item.line,
                                        **({"startColumn": item.column} if item.column else {}),
                                    },
                                }
                            }
                        ],
                    }
                    for item in result.diagnostics
                ],
            }
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
