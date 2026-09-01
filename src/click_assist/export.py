"""Validate a machine and write the paste bundle."""

from __future__ import annotations

from pathlib import Path

from click_assist.machines import Machine
from click_assist.review import write_review


def validate_machine(machine: Machine) -> list[str]:
    report = machine.mapping.validate(machine.logic, mode="strict")
    lines: list[str] = []
    summary = getattr(report, "summary", None)
    if callable(summary):
        text = summary()
        if text:
            lines.append(text)
    errors = list(getattr(report, "errors", ()) or ())
    warnings = list(getattr(report, "warnings", ()) or ())
    hints = list(getattr(report, "hints", ()) or ())
    findings = list(getattr(report, "findings", ()) or ())
    if errors:
        raise RuntimeError(_format_findings("Click validation failed", errors))
    for finding in warnings + hints + findings:
        lines.append(_format_finding(finding))
    return lines


def export_machine(machine: Machine, export_dir: Path | None = None) -> Path:
    from pyrung.click import pyrung_to_ladder

    validate_machine(machine)
    out = export_dir or machine.export_dir
    out.mkdir(parents=True, exist_ok=True)
    bundle = pyrung_to_ladder(machine.logic, machine.mapping)
    bundle.write(out)
    machine.mapping.to_nickname_file(str(out / "nicknames.csv"))
    write_review(out)
    return out


def _format_findings(title: str, findings) -> str:
    parts = [title]
    for finding in findings:
        parts.append("  " + _format_finding(finding))
    return "\n".join(parts)


def _format_finding(finding) -> str:
    if isinstance(finding, str):
        return finding
    level = getattr(finding, "severity", None) or getattr(finding, "level", "")
    code = getattr(finding, "code", "")
    message = getattr(finding, "message", str(finding))
    location = getattr(finding, "location", "")
    bits = [str(part) for part in (level, code, location, message) if part]
    return ": ".join(bits)
