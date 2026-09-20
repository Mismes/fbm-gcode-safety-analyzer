"""Evaluate supported commands and safety rules against modal state."""

from __future__ import annotations

from ..config import MachineProfile
from ..diagnostics import Diagnostic, Severity
from ..modal_state import ModalState, to_profile_units
from ..parser import Block, Word

_SUPPORTED_G = {0, 1, 2, 3, 20, 21, 90, 91}
_SUPPORTED_M = {3, 4, 5}
_AXES = {"X", "Y", "Z"}
_ARC_WORDS = {"I", "J", "K", "R"}


def _unknown(
    profile: MachineProfile,
    line: int,
    message: str,
    column: int | None = None,
) -> Diagnostic | None:
    if profile.unknown_code == "ignore":
        return None
    severity = Severity.ERROR if profile.unknown_code == "error" else Severity.WARNING
    return Diagnostic("GSA005", severity, line, message, column)


def _codes(block: Block, address: str) -> list[tuple[Word, int | None]]:
    return [(word, word.code()) for word in block.words if word.address == address]


def _report_unsupported(
    block: Block,
    profile: MachineProfile,
    diagnostics: list[Diagnostic],
) -> bool:
    g_codes = _codes(block, "G")
    m_codes = _codes(block, "M")
    unsupported_g = False
    for word, code in [*g_codes, *m_codes]:
        supported = _SUPPORTED_G if word.address == "G" else _SUPPORTED_M
        if code is None or code not in supported:
            unsupported_g = unsupported_g or word.address == "G"
            item = _unknown(
                profile,
                block.line,
                f"Unsupported command {word.address}{word.raw_value}",
                word.column,
            )
            if item:
                diagnostics.append(item)

    known_addresses = {"N", "G", "M", "S", "F", *_AXES, *_ARC_WORDS}
    for word in block.words:
        if word.address not in known_addresses:
            item = _unknown(
                profile,
                block.line,
                f"Unsupported word {word.address}{word.raw_value}",
                word.column,
            )
            if item:
                diagnostics.append(item)
    return unsupported_g


def _apply_modes(
    block: Block,
    state: ModalState,
    diagnostics: list[Diagnostic],
) -> tuple[set[int | None], set[int | None], dict[str, float]] | None:
    g_codes = _codes(block, "G")
    unit_codes = {code for _, code in g_codes if code in {20, 21}}
    positioning_codes = {code for _, code in g_codes if code in {90, 91}}
    motion_codes = [code for _, code in g_codes if code in {0, 1, 2, 3}]
    if len(unit_codes) > 1:
        diagnostics.append(
            Diagnostic("GSA006", Severity.ERROR, block.line, "Conflicting unit modes in one block")
        )
    if len(positioning_codes) > 1:
        diagnostics.append(
            Diagnostic(
                "GSA006",
                Severity.ERROR,
                block.line,
                "Conflicting positioning modes in one block",
            )
        )
    if len(set(motion_codes)) > 1:
        diagnostics.append(
            Diagnostic(
                "GSA004", Severity.ERROR, block.line, "Conflicting motion modes in one block"
            )
        )
    if any(item.severity == Severity.ERROR for item in diagnostics):
        return None

    axes = {word.address: word.value for word in block.words if word.address in _AXES}
    if axes and (unit_codes or positioning_codes):
        diagnostics.append(
            Diagnostic(
                "GSA006",
                Severity.WARNING,
                block.line,
                "Unit or positioning mode changes on a motion block",
            )
        )
    if unit_codes:
        state.units = "inch" if 20 in unit_codes else "mm"
    if positioning_codes:
        state.positioning = "absolute" if 90 in positioning_codes else "incremental"
    if motion_codes:
        state.motion = motion_codes[-1]
    return unit_codes, positioning_codes, axes


def _apply_spindle_and_feed(block: Block, state: ModalState) -> None:
    for word in block.words:
        if word.address == "S":
            state.spindle_speed = word.value
        elif word.address == "F":
            state.feed_rate = word.value
    for _, code in _codes(block, "M"):
        if code == 3:
            state.spindle = "clockwise"
        elif code == 4:
            state.spindle = "counterclockwise"
        elif code == 5:
            state.spindle = "stopped"


def _check_cutting(
    block: Block,
    state: ModalState,
    profile: MachineProfile,
    diagnostics: list[Diagnostic],
    has_motion: bool,
) -> None:
    if not has_motion or state.motion not in {1, 2, 3}:
        return
    if profile.require_spindle_for_cutting and (
        state.spindle == "stopped" or state.spindle_speed is None or state.spindle_speed <= 0
    ):
        diagnostics.append(
            Diagnostic(
                "GSA002",
                Severity.ERROR,
                block.line,
                "Cutting move encountered without an active spindle and positive speed",
            )
        )
    if profile.require_feed_for_cutting and (state.feed_rate is None or state.feed_rate <= 0):
        diagnostics.append(
            Diagnostic(
                "GSA003",
                Severity.ERROR,
                block.line,
                "Cutting move encountered without a positive modal feed rate",
            )
        )


def _update_position(
    block: Block,
    state: ModalState,
    profile: MachineProfile,
    diagnostics: list[Diagnostic],
    axes: dict[str, float],
    has_motion: bool,
) -> None:
    target = dict(state.position)
    if axes and state.units is not None and state.positioning is not None:
        for axis, value in axes.items():
            converted = to_profile_units(value, state.units, profile.units)
            if state.positioning == "absolute":
                target[axis] = converted
            elif state.position[axis] is None:
                diagnostics.append(
                    Diagnostic(
                        "GSA006",
                        Severity.ERROR,
                        block.line,
                        f"Incremental {axis} move has no known starting position",
                    )
                )
            else:
                target[axis] = state.position[axis] + converted

    if has_motion and state.motion == 0 and "Z" in axes and target["Z"] is not None:
        if target["Z"] < profile.safe_rapid_z:
            diagnostics.append(
                Diagnostic(
                    "GSA001",
                    Severity.WARNING,
                    block.line,
                    f"Rapid target Z {target['Z']:g} {profile.units} is below "
                    f"clearance {profile.safe_rapid_z:g} {profile.units}",
                )
            )
    state.position.update(target)


def evaluate_block(
    block: Block,
    state: ModalState,
    profile: MachineProfile,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if _report_unsupported(block, profile, diagnostics):
        # Axis words on an unsupported G-code block may be parameters rather
        # than motion, so never inherit a previous motion for this block.
        return diagnostics

    modes = _apply_modes(block, state, diagnostics)
    if modes is None:
        return diagnostics
    _, _, axes = modes
    _apply_spindle_and_feed(block, state)

    has_motion = bool(axes) and state.motion in {0, 1, 2, 3}
    if has_motion and state.units is None:
        diagnostics.append(
            Diagnostic(
                "GSA006",
                Severity.ERROR,
                block.line,
                "Motion units are indeterminate; set G20 or G21",
            )
        )
    if has_motion and state.positioning is None:
        diagnostics.append(
            Diagnostic(
                "GSA006",
                Severity.ERROR,
                block.line,
                "Positioning mode is indeterminate; set G90 or G91",
            )
        )

    _check_cutting(block, state, profile, diagnostics, has_motion)
    _update_position(block, state, profile, diagnostics, axes, has_motion)
    return diagnostics
