"""Big jig flipper: head-stock / tail-stock lifts and clamps, E-stop, and jog.

Each lift and clamp runs to its own prox. Flip still waits for both up proxes.
Robot commands and status travel on EtherNet/IP words.
DS1-DS4 are inputs to the scanner. DS5, DS6, and DS8 are outputs from the scanner.
DS9-DS20 are pendant jog commands from the scanner. DS20 links the lifts. DS7 is spare.
"""

from pyrung import And, Bool, Int, Or, Program, Timer, comment, copy, on_delay, out, rung, system

SETTLE_MS = 1000
PLACE_TIMEOUT_S = 40

AfterClamp1 = Timer.clone("AfterClamp1")
AfterClamp2 = Timer.clone("AfterClamp2")
AfterLift = Timer.clone("AfterLift")
AfterRotate = Timer.clone("AfterRotate")
AfterDown = Timer.clone("AfterDown")
PlaceTimeout = Timer.clone("PlaceTimeout")

AProx = Bool("AProx")
BProx = Bool("BProx")
ClampedProx1 = Bool("ClampedProx1")
ClampedProx2 = Bool("ClampedProx2")
UnclampedProx1 = Bool("UnclampedProx1")
UnclampedProx2 = Bool("UnclampedProx2")
LiftUpProx1 = Bool("LiftUpProx1")
LiftUpProx2 = Bool("LiftUpProx2")
JigPlaced = Bool("JigPlaced")

FlipToARbt = Bool("FlipToARbt")
FlipToBRbt = Bool("FlipToBRbt")
ErrorAck = Bool("ErrorAck")
PlaceError = Bool("PlaceError")

RobotReady = Int("RobotReady")
RobotError = Int("RobotError")
RobotAtA = Int("RobotAtA")
RobotAtB = Int("RobotAtB")
RobotFlipA = Int("RobotFlipA")
RobotFlipB = Int("RobotFlipB")
RobotErrorAck = Int("RobotErrorAck")
RobotJogMode = Int("RobotJogMode")
RobotJogLift1Up = Int("RobotJogLift1Up")
RobotJogLift1Dn = Int("RobotJogLift1Dn")
RobotJogLift2Up = Int("RobotJogLift2Up")
RobotJogLift2Dn = Int("RobotJogLift2Dn")
RobotJogClamp1In = Int("RobotJogClamp1In")
RobotJogClamp1Out = Int("RobotJogClamp1Out")
RobotJogClamp2In = Int("RobotJogClamp2In")
RobotJogClamp2Out = Int("RobotJogClamp2Out")
RobotJogRotateA = Int("RobotJogRotateA")
RobotJogRotateB = Int("RobotJogRotateB")
RobotJogLink = Int("RobotJogLink")

Holding = Bool("Holding")
AStartCheck = Bool("AStartCheck")
BStartCheck = Bool("BStartCheck")
SlideClampsIn1 = Bool("SlideClampsIn1")
SlideClampsIn2 = Bool("SlideClampsIn2")
Lift1 = Bool("Lift1")
Lift2 = Bool("Lift2")
FlipDirection = Bool("FlipDirection")
FlipToA = Bool("FlipToA")
FlipToB = Bool("FlipToB")
SetDown = Bool("SetDown")
SlideClampsOut1 = Bool("SlideClampsOut1")
SlideClampsOut2 = Bool("SlideClampsOut2")
ResetToHold = Bool("ResetToHold")

Estop = Bool("Estop")
EstopHold = Bool("EstopHold")
JogMode = Bool("JogMode")
JogLift1Up = Bool("JogLift1Up")
JogLift1Dn = Bool("JogLift1Dn")
JogLift2Up = Bool("JogLift2Up")
JogLift2Dn = Bool("JogLift2Dn")
JogClamp1In = Bool("JogClamp1In")
JogClamp1Out = Bool("JogClamp1Out")
JogClamp2In = Bool("JogClamp2In")
JogClamp2Out = Bool("JogClamp2Out")
JogRotateA = Bool("JogRotateA")
JogRotateB = Bool("JogRotateB")

Lift1UpValve = Bool("Lift1UpValve")
Lift1DnValve = Bool("Lift1DnValve")
Lift2UpValve = Bool("Lift2UpValve")
Lift2DnValve = Bool("Lift2DnValve")
Clamp1Valve = Bool("Clamp1Valve")
Unclamp1Valve = Bool("Unclamp1Valve")
Clamp2Valve = Bool("Clamp2Valve")
Unclamp2Valve = Bool("Unclamp2Valve")
RotateToAValve = Bool("RotateToAValve")
RotateToBValve = Bool("RotateToBValve")
AllowJigSense = Bool("AllowJigSense")

with Program() as logic:
    comment("Flip to A from the robot. DS5, any non-zero value.")
    with rung(RobotFlipA > 0):
        out(FlipToARbt)

    comment("Flip to B from the robot. DS6, any non-zero value.")
    with rung(RobotFlipB > 0):
        out(FlipToBRbt)

    comment("Robot acknowledges a place error. DS8, any non-zero value.")
    with rung(RobotErrorAck > 0):
        out(ErrorAck)

    comment("Jog mode from the pendant. DS9, any non-zero value. Auto valves stay off while this is on.")
    with rung(RobotJogMode > 0):
        out(JogMode)

    comment("Head-stock lift up from the pendant. DS10. With DS20 on, the tail up button raises this side too.")
    with rung(Or(RobotJogLift1Up > 0, And(RobotJogLink > 0, RobotJogLift2Up > 0))):
        out(JogLift1Up)

    comment("Head-stock lift down from the pendant. DS11. With DS20 on, the tail down button lowers this side too.")
    with rung(Or(RobotJogLift1Dn > 0, And(RobotJogLink > 0, RobotJogLift2Dn > 0))):
        out(JogLift1Dn)

    comment("Tail-stock lift up from the pendant. DS12. With DS20 on, the head up button raises this side too.")
    with rung(Or(RobotJogLift2Up > 0, And(RobotJogLink > 0, RobotJogLift1Up > 0))):
        out(JogLift2Up)

    comment("Tail-stock lift down from the pendant. DS13. With DS20 on, the head down button lowers this side too.")
    with rung(Or(RobotJogLift2Dn > 0, And(RobotJogLink > 0, RobotJogLift1Dn > 0))):
        out(JogLift2Dn)

    comment("Head-stock clamp in from the pendant. DS14.")
    with rung(RobotJogClamp1In > 0):
        out(JogClamp1In)

    comment("Head-stock unclamp from the pendant. DS15.")
    with rung(RobotJogClamp1Out > 0):
        out(JogClamp1Out)

    comment("Tail-stock clamp in from the pendant. DS16.")
    with rung(RobotJogClamp2In > 0):
        out(JogClamp2In)

    comment("Tail-stock unclamp from the pendant. DS17.")
    with rung(RobotJogClamp2Out > 0):
        out(JogClamp2Out)

    comment("Rotate to A from the pendant. DS18.")
    with rung(RobotJogRotateA > 0):
        out(JogRotateA)

    comment("Rotate to B from the pendant. DS19.")
    with rung(RobotJogRotateB > 0):
        out(JogRotateB)

    comment("Holding seals on first scan, reset-to-hold, E-stop, or a place error. Drops when a start check latches.")
    with rung(
        Or(system.sys.first_scan, ResetToHold, Estop, PlaceError, Holding),
        ~AStartCheck,
        ~BStartCheck,
    ):
        out(Holding)

    comment("E-stop seals until both robot requests are off, so releasing it does not start another cycle.")
    with rung(Or(Estop, And(EstopHold, Or(FlipToARbt, FlipToBRbt)))):
        out(EstopHold)

    comment("Robot asks flip to A while holding and the jig is still on B. Already on A stays in wait. Drops when either clamp-in bit latches.")
    with rung(
        Or(
            And(Holding, FlipToARbt, BProx, ~AProx, ~EstopHold, ~PlaceError),
            And(AStartCheck, ~Holding, BProx, ~AProx),
        ),
        ~SlideClampsIn1,
        ~SlideClampsIn2,
        ~Estop,
    ):
        out(AStartCheck)

    comment("Robot asks flip to B while holding and the jig is still on A. Already on B stays in wait. Drops when either clamp-in bit latches.")
    with rung(
        Or(
            And(Holding, FlipToBRbt, AProx, ~BProx, ~EstopHold, ~PlaceError),
            And(BStartCheck, ~Holding, AProx, ~BProx),
        ),
        ~SlideClampsIn1,
        ~SlideClampsIn2,
        ~Estop,
    ):
        out(BStartCheck)

    comment("Head-stock clamp in. Independent of tail stock. Drops when this side starts lifting.")
    with rung(
        Or(And(AStartCheck, BProx), And(BStartCheck, AProx), SlideClampsIn1),
        ~Lift1,
        ~Estop,
    ):
        out(SlideClampsIn1)

    comment("Tail-stock clamp in. Independent of head stock. Drops when this side starts lifting.")
    with rung(
        Or(And(AStartCheck, BProx), And(BStartCheck, AProx), SlideClampsIn2),
        ~Lift2,
        ~Estop,
    ):
        out(SlideClampsIn2)

    comment("Lull after head-stock clamp prox before that side lifts.")
    with rung(ClampedProx1):
        on_delay(AfterClamp1, SETTLE_MS)

    comment("Lull after tail-stock clamp prox before that side lifts.")
    with rung(ClampedProx2):
        on_delay(AfterClamp2, SETTLE_MS)

    comment("Head-stock lift after this side is clamped and settled. Drops when flip-direction latches or E-stop hits.")
    with rung(
        Or(And(SlideClampsIn1, ClampedProx1, AfterClamp1.Done), Lift1),
        ~FlipDirection,
        ~Estop,
    ):
        out(Lift1)

    comment("Tail-stock lift after this side is clamped and settled. Drops when flip-direction latches or E-stop hits.")
    with rung(
        Or(And(SlideClampsIn2, ClampedProx2, AfterClamp2.Done), Lift2),
        ~FlipDirection,
        ~Estop,
    ):
        out(Lift2)

    comment("Lull after both lift-up proxes before rotate.")
    with rung(LiftUpProx1, LiftUpProx2):
        on_delay(AfterLift, SETTLE_MS)

    comment("Flip direction after both lifts are up and settled. Drops when a rotate bit latches.")
    with rung(
        Or(
            And(
                Lift1,
                Lift2,
                LiftUpProx1,
                LiftUpProx2,
                AfterLift.Done,
                ClampedProx1,
                ClampedProx2,
            ),
            FlipDirection,
        ),
        ~FlipToA,
        ~FlipToB,
        ~Estop,
    ):
        out(FlipDirection)

    comment("Rotate toward A while still seeing B. Drops on set-down or E-stop.")
    with rung(Or(And(FlipDirection, BProx), FlipToA), ~SetDown, ~Estop):
        out(FlipToA)

    comment("Rotate toward B while still seeing A. Drops on set-down or E-stop.")
    with rung(Or(And(FlipDirection, AProx), FlipToB), ~SetDown, ~Estop):
        out(FlipToB)

    comment("Lull after the destination rotate prox before set-down.")
    with rung(Or(And(FlipToA, AProx), And(FlipToB, BProx))):
        on_delay(AfterRotate, SETTLE_MS)

    comment("Set down after the destination prox and settle. Drops when either unclamp bit latches.")
    with rung(
        Or(
            And(FlipToA, AProx, AfterRotate.Done),
            And(FlipToB, BProx, AfterRotate.Done),
            SetDown,
        ),
        ~SlideClampsOut1,
        ~SlideClampsOut2,
        ~Estop,
        ~PlaceError,
    ):
        out(SetDown)

    comment("Lull after set-down before unclamp. Also the jig-placed window.")
    with rung(SetDown):
        on_delay(AfterDown, SETTLE_MS)

    comment("40 seconds to see the jig placed, starting when set-down turns on.")
    with rung(SetDown, ~JigPlaced):
        on_delay(PlaceTimeout, PLACE_TIMEOUT_S, "s")

    comment("Jig was not placed within 40 seconds. Stays on until the robot acknowledges.")
    with rung(Or(And(SetDown, PlaceTimeout.Done, ~JigPlaced), And(PlaceError, ~ErrorAck))):
        out(PlaceError)

    comment("Unclamp after set-down settle when the placed prox is on. Drops on reset-to-hold or E-stop.")
    with rung(
        Or(And(SetDown, AfterDown.Done, JigPlaced), SlideClampsOut1),
        ~ResetToHold,
        ~Estop,
    ):
        out(SlideClampsOut1)

    comment("Second unclamp bit. Original CSV sealed this on clamp-out 1, not on itself.")
    with rung(
        Or(And(SetDown, AfterDown.Done, JigPlaced), SlideClampsOut1),
        ~ResetToHold,
        ~Estop,
    ):
        out(SlideClampsOut2)

    comment("Reset to hold once both unclamp proxes prove the clamps are out. Pulses Holding back on.")
    with rung(SlideClampsOut1, SlideClampsOut2, UnclampedProx1, UnclampedProx2, ~Estop):
        out(ResetToHold)

    comment("Head-stock lift up until its own up prox. Jog or auto. Dead on E-stop.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogLift1Up, ~JogLift1Dn),
            And(~JogMode, Lift1, ~LiftUpProx1, ~SetDown),
        ),
    ):
        out(Lift1UpValve)

    comment("Head-stock lift down during jog or set-down. Off while waiting in hold. Dead on E-stop.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogLift1Dn, ~JogLift1Up),
            And(~JogMode, SetDown, ~PlaceError),
        ),
    ):
        out(Lift1DnValve)

    comment("Tail-stock lift up until its own up prox. Does not drop when the other side arrives.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogLift2Up, ~JogLift2Dn),
            And(~JogMode, Lift2, ~LiftUpProx2, ~SetDown),
        ),
    ):
        out(Lift2UpValve)

    comment("Tail-stock lift down during jog or set-down. Off while waiting in hold. Dead on E-stop.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogLift2Dn, ~JogLift2Up),
            And(~JogMode, SetDown, ~PlaceError),
        ),
    ):
        out(Lift2DnValve)

    comment("Head-stock clamp in until its own clamped prox.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogClamp1In, ~JogClamp1Out),
            And(~JogMode, SlideClampsIn1, ~ClampedProx1, ~SlideClampsOut1),
        ),
    ):
        out(Clamp1Valve)

    comment("Head-stock unclamp until its own unclamped prox.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogClamp1Out, ~JogClamp1In),
            And(~JogMode, SlideClampsOut1, ~UnclampedProx1),
        ),
    ):
        out(Unclamp1Valve)

    comment("Tail-stock clamp in until its own clamped prox.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogClamp2In, ~JogClamp2Out),
            And(~JogMode, SlideClampsIn2, ~ClampedProx2, ~SlideClampsOut2),
        ),
    ):
        out(Clamp2Valve)

    comment("Tail-stock unclamp until its own unclamped prox.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogClamp2Out, ~JogClamp2In),
            And(~JogMode, SlideClampsOut2, ~UnclampedProx2),
        ),
    ):
        out(Unclamp2Valve)

    comment("Rotate to A only while both clamps are proven in. Jog or auto. Dead on E-stop.")
    with rung(
        ~Estop,
        ClampedProx1,
        ClampedProx2,
        Or(
            And(JogMode, JogRotateA, ~JogRotateB),
            And(~JogMode, FlipToA, ~FlipToB),
        ),
    ):
        out(RotateToAValve)

    comment("Rotate to B only while both clamps are proven in. Jog or auto. Dead on E-stop.")
    with rung(
        ~Estop,
        ClampedProx1,
        ClampedProx2,
        Or(
            And(JogMode, JogRotateB, ~JogRotateA),
            And(~JogMode, FlipToB, ~FlipToA),
        ),
    ):
        out(RotateToBValve)

    comment("Allow jig sense while setting down. Off in wait, on a place error, and on E-stop.")
    with rung(~Estop, SetDown, ~PlaceError):
        out(AllowJigSense)

    comment("DS1 ready is 1 only while waiting with no place error.")
    with rung(Or(~Holding, PlaceError)):
        copy(0, RobotReady)
    with rung(Holding, ~PlaceError):
        copy(1, RobotReady)

    comment("DS2 is 1 while the jig-placed timeout is latched.")
    with rung(~PlaceError):
        copy(0, RobotError)
    with rung(PlaceError):
        copy(1, RobotError)

    comment("DS3 follows the A position prox.")
    with rung(~AProx):
        copy(0, RobotAtA)
    with rung(AProx):
        copy(1, RobotAtA)

    comment("DS4 follows the B position prox.")
    with rung(~BProx):
        copy(0, RobotAtB)
    with rung(BProx):
        copy(1, RobotAtB)
