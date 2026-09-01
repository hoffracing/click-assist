---
name: click-author
description: Author AutomationDirect Click PLC ladder as pyrung Python, validate it, and export a paste bundle for Click Programming Software. Use when the user describes Click logic, ladder rungs, I/O maps, nicknames, or wants to paste into Click.
---

# Click author

Click is ladder only. There is no structured text compiler. Do not write `.ckp` files or download to a PLC.

Source of truth is Python under `machines/<name>/`. The CLI compiles that into CSV that Click can paste.

## Workflow

Copy this checklist and complete it in order:

```
- [ ] Write or edit machines/<name>/logic.py
- [ ] Write or edit machines/<name>/io_map.py
- [ ] Write pytest scenarios that match the English request
- [ ] click-assist check <name>
- [ ] click-assist export <name>
- [ ] Show REVIEW.md to the user
- [ ] Wait for user OK
- [ ] click-assist clipboard <name> only after they accept the listing
```

Never skip the review listing. Never treat CSV as the thing the user should read first.

## Machine layout

```
machines/<name>/
  logic.py      # Program + semantic Bool/Int/Timer tags
  io_map.py     # TagMap to Click banks
  tests/        # pytest
  export/       # generated. do not hand-edit
```

`logic.py` exports `logic`. `io_map.py` exports `mapping`.

## Authoring rules

- Use semantic tag names (`StartButton`, not `X001`) in `logic.py`
- Map addresses only in `io_map.py`
- Comment every rung with `comment("...")` immediately before `with rung(...)`
- Put E-stop and interlocks on the rung as explicit contacts. Do not hide them in a latch with no dropout path
- Do not reuse a Click address for two meanings
- No inline expressions in contacts. Compute first with `calc(...)`, then compare
- Timer presets must fit in 32767 for the chosen unit
- Click-legal condition tokens only. See [reference-instructions.md](reference-instructions.md)
- Address banks and sparse X/Y ranges are in [reference-addressing.md](reference-addressing.md)
- A worked motor example is in [examples.md](examples.md)

## Refuse

- Downloading or flashing a PLC
- Writing or patching `.ckp` / `SC_.mdb`
- Inventing Click PLUS Home / Email / Velocity / Position instructions
- Configuring PID, MQTT, EtherNet/IP, Wi-Fi, or I/O modules. Tell the user those stay in Click
- Pasting to the clipboard before the user has seen `REVIEW.md`

## After export

Print `machines/<name>/export/REVIEW.md`. Ask the user to confirm before `click-assist clipboard`. Paste steps are in `docs/paste-into-click.md`.
