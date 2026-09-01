# click-assist

Describe Click PLC logic in English, or edit the Python. This repo turns that into a reviewable ladder listing and a paste bundle for CLICK Programming Software.

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

The Cursor skill `.cursor/skills/click-author/` is a project skill. It travels with this repo. Open this folder in Cursor and describe a machine in English. The agent writes those files, runs check/export, and stops at `REVIEW.md` until you accept the rungs.

The starter example is a seal-in motor with stop, E-stop, guard, and overload dropouts.

## Get the rungs into Click

Guided Paste is **not** in Click Programming Software and **not** in this repo. It is a ClickNick window.

1. Export here and read the listing first:

   ```
   click-assist check starter_motor
   click-assist export starter_motor
   ```

   Open `machines/starter_motor/export/REVIEW.md`. If a rung is wrong, fix the Python and export again.

2. Open your `.ckp` in CLICK Programming Software. Set I/O modules, Ethernet, and ports there. Those settings are not in this repo.

3. Install ClickNick 0.19 or newer if you do not have it:

   ```
   pip install "clicknick>=0.19"
   clicknick
   ```

   ClickNick attaches to the Click project you already have open.

4. In the **ClickNick** window (not Click), open the **Ladder** menu and choose **Open in Guided Paste**. Some builds label it **Guided Paste**.

5. Point that panel at the export folder, for example:

   `C:\Users\aaronh\Projects\click-assist\machines\starter_motor\export`

   Walk through each CSV. Import `nicknames.csv` in that flow if you have not already imported nicknames in Click (File → Import).

If there is no Ladder menu, the ClickNick build is too old. Upgrade to 0.19+.

### Clipboard if you skip ClickNick

With Click running and the ladder editor focused:

```
click-assist clipboard starter_motor
```

Then Ctrl+V in Click. That is Click's private clipboard format, not plain text. If paste does nothing, Click is not the foreground editor or the software version drifted from laddercodec.

You can also run `clicknick-rung load machines/starter_motor/export/main.csv` if that CLI is installed.

### Finish in Click

Confirm the rungs match `REVIEW.md`. Finish PID, MQTT, comms, and I/O in the Click dialogs. Save the `.ckp` and download from Click.

The Python tests are a logic check, not a factory acceptance test. Run it on the hardware.

If paste breaks after a Click update, keep the CSV and re-export. Do not hand-edit `.ckp` files.

More detail: [docs/paste-into-click.md](docs/paste-into-click.md)
