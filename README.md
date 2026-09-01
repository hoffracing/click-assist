# click-assist

Describe Click PLC logic in English (or edit the Python). This repo turns that into a reviewable ladder listing and a paste bundle for **CLICK Programming Software**.

Click still owns the `.ckp` and the download. There is no public way to write a complete Click project file.

## Setup

Python 3.12+ (3.14 works). From this directory:

```
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Optional, only if you want ClickNick's window lookup during clipboard paste:

```
pip install -e ".[clipboard]"
```

## Commands

```
click-assist list
click-assist check starter_motor
click-assist export starter_motor
click-assist clipboard starter_motor
```

`check` runs Click constraint validation, then pytest. `export` writes `machines/<name>/export/` (`main.csv`, `nicknames.csv`, `REVIEW.md`). `clipboard` encodes `main.csv` for paste into Click.

## Author a machine

Each folder under `machines/` is one program:

- `logic.py` exports a pyrung `Program` as `logic`
- `io_map.py` exports a `TagMap` as `mapping`
- `tests/` holds pytest scenarios

The Cursor skill `.cursor/skills/click-author/` tells the agent to write those files, run check/export, and stop at `REVIEW.md` until you accept the rungs.

The starter example is a seal-in motor with stop, E-stop, guard, and overload dropouts. See `docs/paste-into-click.md` for the last mile in Click.
