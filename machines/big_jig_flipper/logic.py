"""Big jig flipper: head-stock / tail-stock lifts and clamps, E-stop, and jog.

Each lift and clamp runs to its own prox. Flip still waits for both up proxes.
E-stop and jog bits are C coils for the Click app until real HMI/hardwired
points exist. Analog clamp position is not in this pass.
"""

from pyrung import And, Bool, Or, Program, Timer, comment, on_delay, out, rung, system

SETTLE_MS = 1000

AfterClamp1 = Timer.clone("AfterClamp1")
AfterClamp2 = Timer.clone("AfterClamp2")
AfterLift = Timer.clone("AfterLift")
AfterRotate = Timer.clone("AfterRotate")
AfterDown = Timer.clone("AfterDown")

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
    comment("Holding seals on first scan or reset-to-hold. Drops when a start check latches.")
    with rung(Or(system.sys.first_scan, ResetToHold, Holding), ~AStartCheck, ~BStartCheck):
        out(Holding)

    comment("Robot asks flip to A while holding. Drops when either clamp-in bit latches.")
    with rung(
        Or(And(Holding, FlipToARbt), And(AStartCheck, ~Holding)),
        ~SlideClampsIn1,
        ~SlideClampsIn2,
    ):
        out(AStartCheck)

    comment("Robot asks flip to B while holding. Drops when either clamp-in bit latches.")
    with rung(
        Or(And(Holding, FlipToBRbt), And(BStartCheck, ~Holding)),
        ~SlideClampsIn1,
        ~SlideClampsIn2,
    ):
        out(BStartCheck)

    comment("Head-stock clamp in. Independent of tail stock. Drops when this side starts lifting.")
    with rung(
        Or(And(AStartCheck, BProx), And(BStartCheck, AProx), SlideClampsIn1),
        ~Lift1,
    ):
        out(SlideClampsIn1)

    comment("Tail-stock clamp in. Independent of head stock. Drops when this side starts lifting.")
    with rung(
        Or(And(AStartCheck, BProx), And(BStartCheck, AProx), SlideClampsIn2),
        ~Lift2,
    ):
        out(SlideClampsIn2)

    comment("Lull after head-stock clamp prox before that side lifts.")
    with rung(ClampedProx1):
        on_delay(AfterClamp1, SETTLE_MS)

    comment("Lull after tail-stock clamp prox before that side lifts.")
    with rung(ClampedProx2):
        on_delay(AfterClamp2, SETTLE_MS)

    comment("Head-stock lift after this side is clamped and settled. Drops when flip-direction latches.")
    with rung(
        Or(And(SlideClampsIn1, ClampedProx1, AfterClamp1.Done), Lift1),
        ~FlipDirection,
    ):
        out(Lift1)

    comment("Tail-stock lift after this side is clamped and settled. Drops when flip-direction latches.")
    with rung(
        Or(And(SlideClampsIn2, ClampedProx2, AfterClamp2.Done), Lift2),
        ~FlipDirection,
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
    ):
        out(FlipDirection)

    comment("Rotate toward A while still seeing B. Drops on set-down.")
    with rung(Or(And(FlipDirection, BProx), FlipToA), ~SetDown):
        out(FlipToA)

    comment("Rotate toward B while still seeing A. Drops on set-down.")
    with rung(Or(And(FlipDirection, AProx), FlipToB), ~SetDown):
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
    ):
        out(SetDown)

    comment("Lull after set-down before unclamp.")
    with rung(SetDown):
        on_delay(AfterDown, SETTLE_MS)

    comment("Unclamp after set-down settle when the robot jig-placed signal is on. Drops on reset-to-hold.")
    with rung(
        Or(And(SetDown, AfterDown.Done, JigPlaced), SlideClampsOut1),
        ~ResetToHold,
    ):
        out(SlideClampsOut1)

    comment("Second unclamp bit. Original CSV sealed this on clamp-out 1, not on itself.")
    with rung(
        Or(And(SetDown, AfterDown.Done, JigPlaced), SlideClampsOut1),
        ~ResetToHold,
    ):
        out(SlideClampsOut2)

    comment("Reset to hold once both unclamp proxes prove the clamps are out. Pulses Holding back on.")
    with rung(SlideClampsOut1, SlideClampsOut2, UnclampedProx1, UnclampedProx2):
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
            And(~JogMode, SetDown),
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
            And(~JogMode, SetDown),
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

    comment("Allow jig sense while setting down. Off while waiting in hold. Dead on E-stop.")
    with rung(~Estop, SetDown):
        out(AllowJigSense)
