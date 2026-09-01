# Click instruction tokens

Click Programming Software has a small ladder set. Stay inside it.

## Conditions

```
with rung(Tag):                 # NO
with rung(~Tag):                # NC
with rung(rise(Tag)):           # one-shot rising
with rung(fall(Tag)):           # one-shot falling
with rung(A, B, C):             # AND
with rung(Or(A, B)):            # OR
with rung(DS1 > 100):           # compare. INT tags cannot be bare truthy
```

Do not write `(A + B) > 100` on a contact. Use `calc(A + B, Sum)` on a prior rung, then `with rung(Sum > 100)`.

## Coils and memory

| Click | pyrung |
| --- | --- |
| OUT | `out(Tag)` |
| SET | `latch(Tag)` |
| RST | `reset(Tag)` |
| COPY | `copy(src, dest)` |
| MATH | `calc(expr, dest)` |
| TON | `on_delay(Timer, preset, unit="ms")` |
| TOF | `off_delay(Timer, preset)` |
| CTU / CTD | `count_up` / `count_down` |
| FOR / NEXT | `forloop` |
| CALL / RET / END | `call` / `return_early` / exported automatically |
| SEND / RECEIVE | `send` / `receive` |
| SHIFT / SEARCH / DRUM | `shift` / `search` / `event_drum` / `time_drum` |

CSV export renames `calc` to `math`, `return_early` to `return`, `forloop` to `for`.

## Illegal in v1

- Home, Email, Velocity, Position. These come through as raw blobs if imported. Do not invent them.
- PID, MQTT, EtherNet/IP, I/O module setup. Those are Click dialogs, not rungs.

## Constraints the validator already flags

- Pointer/`copy` source must be a DS address, no arithmetic
- Immediate I/O only on contacts and Y coils
- Timer preset overflow (`CLK_TIMER_PRESET_OVERFLOW`)
- Mixed WORD / non-WORD in one `calc()`
