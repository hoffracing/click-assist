"""Turn exported Click CSV into a readable rung listing."""

from __future__ import annotations

import csv
from pathlib import Path

CONDITION_COLUMNS = 31
WIRE_TOKENS = {"-", "|", "T", ""}


def load_nicknames(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    nicknames: dict[str, str] = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return {}
        address_key = _first_field(reader.fieldnames, ("address", "addr"))
        nick_key = _first_field(reader.fieldnames, ("nickname", "nick", "name"))
        if address_key is None or nick_key is None:
            return {}
        for row in reader:
            address = (row.get(address_key) or "").strip()
            nick = (row.get(nick_key) or "").strip()
            if address and nick:
                nicknames[address] = nick
    return nicknames


def _first_field(fieldnames: list[str], aliases: tuple[str, ...]) -> str | None:
    lowered = {name.lower(): name for name in fieldnames}
    for alias in aliases:
        if alias in lowered:
            return lowered[alias]
    return None


def _label(token: str, nicknames: dict[str, str]) -> str:
    if token in WIRE_TOKENS:
        return token
    bare = token
    prefix = ""
    if token.startswith("T:"):
        prefix = "T:"
        bare = token[2:]
    negated = bare.startswith("~")
    if negated:
        bare = bare[1:]
    nick = nicknames.get(bare)
    shown = f"{nick} ({bare})" if nick else bare
    if negated:
        shown = f"/{shown}"
    return prefix + shown


def format_csv(path: Path, nicknames: dict[str, str] | None = None) -> str:
    nicknames = nicknames or {}
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        return "(empty csv)"

    header = rows[0]
    body = rows[1:]
    lines: list[str] = []
    rung_index = 0
    pending_comments: list[str] = []
    current_comments: list[str] = []
    current_cells: list[list[str]] = []

    def flush() -> None:
        nonlocal rung_index, current_comments, current_cells
        if not current_cells and not current_comments:
            return
        rung_index += 1
        lines.append(f"Rung {rung_index}")
        for comment in current_comments:
            lines.append(f"  # {comment}")
        if not current_cells:
            lines.append("  (comment only)")
        else:
            for row_cells in current_cells:
                lines.append("  " + _format_row(row_cells, nicknames))
        lines.append("")
        current_comments = []
        current_cells = []

    for row in body:
        if not row:
            continue
        marker = row[0]
        if marker == "#":
            if current_cells:
                flush()
            pending_comments.append(row[1] if len(row) > 1 else "")
            continue
        if marker.startswith("R"):
            if current_cells:
                flush()
            current_comments = pending_comments
            pending_comments = []
            current_cells.append(_pad_row(row, header))
            continue
        if current_cells:
            current_cells.append(_pad_row(row, header))
    flush()
    return "\n".join(lines).rstrip() + "\n"


def _pad_row(row: list[str], header: list[str]) -> list[str]:
    width = max(len(header), 2 + CONDITION_COLUMNS)
    padded = list(row) + [""] * (width - len(row))
    return padded[:width]


def _format_row(row: list[str], nicknames: dict[str, str]) -> str:
    cells = row[1 : 1 + CONDITION_COLUMNS]
    af = row[1 + CONDITION_COLUMNS] if len(row) > 1 + CONDITION_COLUMNS else ""
    shown: list[str] = []
    for cell in cells:
        if cell == "" or cell == "-":
            continue
        if cell == "T":
            shown.append("+")
            continue
        if cell == "|":
            shown.append("|")
            continue
        shown.append(_label(cell, nicknames))
    rail = " -- ".join(shown) if shown else "(empty rail)"
    coil = f"  ({_label(af, nicknames)})" if af else ""
    return rail + coil


def write_review(export_dir: Path) -> Path:
    nicknames = load_nicknames(export_dir / "nicknames.csv")
    parts: list[str] = []
    main = export_dir / "main.csv"
    if main.is_file():
        parts.append("# main")
        parts.append("")
        parts.append(format_csv(main, nicknames))
    subdir = export_dir / "subroutines"
    if subdir.is_dir():
        for csv_path in sorted(subdir.glob("*.csv")):
            parts.append(f"# subroutine {csv_path.stem}")
            parts.append("")
            parts.append(format_csv(csv_path, nicknames))
    text = "\n".join(parts).rstrip() + "\n"
    out = export_dir / "REVIEW.md"
    out.write_text(text, encoding="utf-8")
    return out
