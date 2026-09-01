from pathlib import Path

from click_assist.clipboard import encode_csv
from click_assist.export import export_machine
from click_assist.machines import load_machine
from click_assist.review import format_csv, load_nicknames


def test_export_review_lists_seal_in_rung(tmp_path: Path):
    machine = load_machine("starter_motor")
    out = export_machine(machine, tmp_path)
    listing = format_csv(out / "main.csv", load_nicknames(out / "nicknames.csv"))
    assert "Seal-in motor" in listing
    assert "StartButton (X001)" in listing
    assert "Motor (Y001)" in listing
    assert "out(Y001)" in listing
    assert "(comment only)" not in listing
    payload = encode_csv(out / "main.csv")
    assert payload.startswith(b"CLICK")
    assert len(payload) > 32
