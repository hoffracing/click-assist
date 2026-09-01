# Click addressing

Build a fresh `ClickBlocks()` in each `io_map.py`. Do not share blocks across machines.

```
from pyrung.click import ClickBlocks, TagMap

x, y, c, t, ct, sc, ds, dd, dh, df, xd, yd, xd0u, yd0u, td, ctd, sd, txt = ClickBlocks()
```

## Banks

| Bank | Block | Type | Range |
| --- | --- | --- | --- |
| X | `x` | BOOL | sparse 1-816 |
| Y | `y` | BOOL | sparse 1-816 |
| C | `c` | BOOL | 1-2000 |
| DS | `ds` | INT | 1-4500 |
| DD | `dd` | DINT | 1-1000 |
| DH | `dh` | WORD | 1-500 |
| DF | `df` | REAL | 1-500 |
| T / TD | `t` / `td` | BOOL / INT | 1-500 |
| CT / CTD | `ct` / `ctd` | BOOL / DINT | 1-250 |
| SC / SD | `sc` / `sd` | BOOL / INT | 1-1000 |
| TXT | `txt` | CHAR | 1-1000 |

X and Y valid ranges:

```
1-16, 21-36, 101-116, 201-216, 301-316,
401-416, 501-516, 601-616, 701-716, 801-816
```

`x[17]` is invalid. `x.select(1, 21)` skips the gap.

## Mapping

```
mapping = TagMap({
    StartButton: x[1],   # X001
    Motor: y[1],         # Y001
    Speed: df[1],        # DF1
})
```

Types must match. Mapping an INT tag to a C bit fails at map time.

Timers: `Timer.clone("Oven")`, then `Oven.Done` / `Oven.Acc` map to T/TD automatically unless you override.

## Allocation

Keep a written I/O list in comments at the top of `io_map.py` when the map grows. Do not silently reuse an address. Physical inputs stay on X. Physical outputs stay on Y. Internals go to C / DS / DF.
