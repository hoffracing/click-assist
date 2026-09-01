# Example: starter motor

English request:

> Seal-in motor starter. Start is momentary. Stop, E-stop, open guard, or overload must drop the motor.

`machines/starter_motor/logic.py`:

```
from pyrung import Bool, Or, Program, comment, out, rung

StartButton = Bool("StartButton")
StopPressed = Bool("StopPressed")
EstopOk = Bool("EstopOk")
GuardClosed = Bool("GuardClosed")
OverloadOk = Bool("OverloadOk")
Motor = Bool("Motor")

with Program() as logic:
    comment("Seal-in motor. Drops out on stop, E-stop, open guard, or overload.")
    with rung(Or(StartButton, Motor), ~StopPressed, EstopOk, GuardClosed, OverloadOk):
        out(Motor)
```

`io_map.py` maps those tags to X001-X005 and Y001.

Tests must cover start/seal, each dropout, and "cannot start when a permissive is false."

After `click-assist export starter_motor`, `REVIEW.md` should show one rung plus the exported `end()` tail. Show that file to the user before clipboard.
