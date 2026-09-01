# Paste a bundle into Click

Click Programming Software is still the thing that saves the `.ckp` and downloads to the PLC. This project only prepares the ladder and nicknames.

You need Windows, a Click project for the right CPU family, and optionally [ClickNick](https://github.com/ssweber/clicknick) if you want Guided Paste.

## 1. Export here

```
click-assist check starter_motor
click-assist export starter_motor
```

Read `machines/starter_motor/export/REVIEW.md` before you touch Click. If a rung looks wrong, fix the Python and export again.

## 2. Open Click

Open or create a `.ckp` for the CPU you actually have (classic Click vs Click PLUS). Set I/O modules, Ethernet, and ports in Click. Those settings are not in this repo.

## 3. Import nicknames

In Click: **File → Import** (or File → Import → Nicknames, depending on software version) and choose `export/nicknames.csv`.

If Click is already open and ClickNick is connected with ODBC, you can push nicknames through ClickNick instead. They still only become permanent when you save in Click.

## 4. Paste ladder

**Guided Paste (preferred).** In ClickNick: **Ladder → Open in Guided Paste**, point it at `machines/<name>/export/`, and walk through each CSV. Import nicknames in that flow if you have not already.

**Clipboard.** With Click running:

```
click-assist clipboard starter_motor
```

Then paste in the Click ladder editor (`Ctrl+V`). This writes Click's private clipboard format (id 522), not plain text. If paste does nothing, Click is not the foreground editor or the software version drifted from laddercodec.

You can also run `clicknick-rung load machines/starter_motor/export/main.csv` if that CLI is installed.

## 5. Finish in Click

1. Confirm the rungs match `REVIEW.md`
2. Finish PID, MQTT, comms, and I/O in the Click dialogs
3. Save the `.ckp`
4. Download from Click

Do not treat the Python simulation as a certified factory acceptance test. Run it on the hardware.

## If paste breaks after a Click update

Keep the CSV. That is the portable artifact. Update `laddercodec` / ClickNick and run `click-assist export` again. Do not hand-edit `.ckp` files.
