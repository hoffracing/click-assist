"""click-assist command line."""

from __future__ import annotations

import argparse
import subprocess
import sys

from click_assist.clipboard import copy_click_clipboard, encode_csv
from click_assist.export import export_machine, validate_machine
from click_assist.machines import REPO_ROOT, list_machine_names, load_machine


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="click-assist",
        description="Write Click ladder in Python, review it, then paste into Click.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List machine packages")

    check = sub.add_parser("check", help="Validate Click constraints and run pytest")
    check.add_argument("machine", nargs="?", help="Machine name under machines/")

    export = sub.add_parser("export", help="Write ladder CSV, nicknames, and REVIEW.md")
    export.add_argument("machine", nargs="?", help="Machine name under machines/")

    clip = sub.add_parser("clipboard", help="Encode main.csv onto the Click clipboard")
    clip.add_argument("machine", nargs="?", help="Machine name under machines/")
    clip.add_argument(
        "--require-click",
        action="store_true",
        help="Fail if CLICK Programming Software is not running",
    )

    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            return _cmd_list()
        machine = load_machine(_resolve_machine(getattr(args, "machine", None)))
        if args.command == "check":
            return _cmd_check(machine)
        if args.command == "export":
            return _cmd_export(machine)
        if args.command == "clipboard":
            return _cmd_clipboard(machine, require_click=args.require_click)
    except (FileNotFoundError, AttributeError, RuntimeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


def _resolve_machine(name: str | None) -> str:
    names = list_machine_names()
    if name:
        return name
    if len(names) == 1:
        return names[0]
    if not names:
        raise FileNotFoundError("No machines found under machines/")
    listed = ", ".join(names)
    raise FileNotFoundError(f"Pick a machine: {listed}")


def _cmd_list() -> int:
    names = list_machine_names()
    if not names:
        print("No machines found.")
        return 1
    for name in names:
        print(name)
    return 0


def _cmd_check(machine) -> int:
    notes = validate_machine(machine)
    for note in notes:
        if note:
            print(note)
    print(f"{machine.name}: Click validation passed")
    test_dir = machine.tests_dir
    if not test_dir.is_dir():
        print(f"{machine.name}: no tests directory")
        return 0
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_dir)],
        cwd=REPO_ROOT,
    )
    return result.returncode


def _cmd_export(machine) -> int:
    out = export_machine(machine)
    review = out / "REVIEW.md"
    print(f"Wrote {out}")
    print(review.read_text(encoding="utf-8"))
    return 0


def _cmd_clipboard(machine, *, require_click: bool) -> int:
    export_dir = machine.export_dir
    if not (export_dir / "main.csv").is_file():
        export_machine(machine)
    csv_path = export_dir / "main.csv"
    data = encode_csv(csv_path)
    bin_path = export_dir / "main.bin"
    bin_path.write_bytes(data)
    via = copy_click_clipboard(data, require_click=require_click)
    print(f"Encoded {csv_path} ({len(data)} bytes) via {via}")
    print("Paste into the Click ladder editor. Import nicknames first. See docs/paste-into-click.md.")
    return 0
