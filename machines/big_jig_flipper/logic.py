"""Big jig flipper: head-stock / tail-stock lifts and clamps, E-stop, and jog.

Each lift and clamp runs to its own prox. Flip still waits for both up proxes.
E-stop and jog bits are C coils for the Click app until real HMI/hardwired
points exist. Analog clamp position is not in this pass.
"""

from pyrung import And, Bool, Or, Program, comment, out, rung, system

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
    comment("Holding seals after first scan. Also true on set-down idle or while a side prox matches its start check.")
    with rung(
        Or(
            And(SetDown, ~AStartCheck, ~BStartCheck),
            Holding,
            And(AStartCheck, AProx),
            And(BStartCheck, BProx),
            system.sys.first_scan,
        )
    ):
        out(Holding)

    comment("Robot asks flip to A while holding. Drops when clamp-in starts. Seals if holding drops mid-request.")
    with rung(
        Or(
            And(Holding, FlipToARbt, ~SlideClampsIn1, ~SlideClampsIn2),
            And(AStartCheck, ~Holding),
        )
    ):
        out(AStartCheck)

    comment("Robot asks flip to B while holding. Same dropout as the A request.")
    with rung(
        Or(
            And(Holding, FlipToBRbt, ~SlideClampsIn1, ~SlideClampsIn2),
            And(BStartCheck, ~Holding),
        )
    ):
        out(BStartCheck)

    comment("Head-stock clamp in. Independent of tail stock. Drops when this side starts lifting.")
    with rung(
        Or(
            And(AStartCheck, BProx, ~Lift1),
            And(BStartCheck, AProx, ~Lift1),
            SlideClampsIn1,
        )
    ):
        out(SlideClampsIn1)

    comment("Tail-stock clamp in. Independent of head stock.")
    with rung(
        Or(
            And(AStartCheck, BProx, ~Lift2),
            And(BStartCheck, AProx, ~Lift2),
            SlideClampsIn2,
        )
    ):
        out(SlideClampsIn2)

    comment("Head-stock lift after this side is clamped. Does not wait for the tail-stock prox.")
    with rung(Or(And(SlideClampsIn1, ClampedProx1, ~FlipDirection), Lift1)):
        out(Lift1)

    comment("Tail-stock lift after this side is clamped. Does not wait for the head-stock prox.")
    with rung(Or(And(SlideClampsIn2, ClampedProx2, ~FlipDirection), Lift2)):
        out(Lift2)

    comment("Flip direction after both lifts are up. Drops when a rotate bit latches. CSV had a bare C10 on this rail; treated as /FlipToB to match the other step dropouts.")
    with rung(
        Or(
            And(Lift1, Lift2, LiftUpProx1, LiftUpProx2, ~FlipToA, ~FlipToB),
            FlipDirection,
        )
    ):
        out(FlipDirection)

    comment("Rotate toward A while still seeing B. Drops on set-down.")
    with rung(Or(And(FlipDirection, BProx, ~SetDown), FlipToA)):
        out(FlipToA)

    comment("Rotate toward B while still seeing A. Drops on set-down.")
    with rung(Or(And(FlipDirection, AProx, ~SetDown), FlipToB)):
        out(FlipToB)

    comment("Set down after the destination prox is made. Drops when clamp-out starts.")
    with rung(
        Or(
            And(FlipToA, AProx, ~SlideClampsOut1, ~SlideClampsOut2),
            And(FlipToB, BProx, ~SlideClampsOut1, ~SlideClampsOut2),
            SetDown,
        )
    ):
        out(SetDown)

    comment("Unclamp after set-down when the robot jig-placed signal is on. Drops on reset-to-hold.")
    with rung(Or(And(SetDown, JigPlaced, ~ResetToHold), SlideClampsOut1)):
        out(SlideClampsOut1)

    comment("Second unclamp bit. Original CSV sealed this on clamp-out 1, not on itself.")
    with rung(Or(And(SetDown, JigPlaced, ~ResetToHold), SlideClampsOut1)):
        out(SlideClampsOut2)

    comment("Reset to hold once both unclamp proxes prove the clamps are out. Original CSV never wrote C14.")
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

    comment("Head-stock lift down. Jog, set-down, or rest. Dead on E-stop.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogLift1Dn, ~JogLift1Up),
            And(~JogMode, SetDown),
            And(~JogMode, Holding, ~Lift1),
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

    comment("Tail-stock lift down. Jog, set-down, or rest. Dead on E-stop.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogLift2Dn, ~JogLift2Up),
            And(~JogMode, SetDown),
            And(~JogMode, Holding, ~Lift2),
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

    comment("Rotate to A. Jog or auto. Dead on E-stop.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogRotateA, ~JogRotateB),
            And(~JogMode, FlipToA, ~FlipToB),
        ),
    ):
        out(RotateToAValve)

    comment("Rotate to B. Jog or auto. Dead on E-stop.")
    with rung(
        ~Estop,
        Or(
            And(JogMode, JogRotateB, ~JogRotateA),
            And(~JogMode, FlipToB, ~FlipToA),
        ),
    ):
        out(RotateToBValve)

    comment("Allow jig sense while holding or setting down, not in E-stop.")
    with rung(~Estop, Or(Holding, SetDown)):
        out(AllowJigSense)
