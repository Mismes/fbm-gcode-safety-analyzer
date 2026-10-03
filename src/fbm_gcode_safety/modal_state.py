"""Modal machine state for the documented G-code subset."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ModalState:
    motion: int | None = None
    units: str | None = None
    positioning: str | None = None
    spindle: str = "stopped"
    spindle_speed: float | None = None
    feed_rate: float | None = None
    position: dict[str, float | None] = field(
        default_factory=lambda: {"X": None, "Y": None, "Z": None}
    )


def to_profile_units(value: float, active_units: str, profile_units: str) -> float:
    if active_units == profile_units:
        return value
    if active_units == "inch" and profile_units == "mm":
        return value * 25.4
    return value / 25.4
