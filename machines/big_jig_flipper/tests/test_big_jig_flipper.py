from pyrung import PLC

from machines.big_jig_flipper.logic import (
    SETTLE_MS,
    AProx,
    AStartCheck,
    AllowJigSense,
    BProx,
    Clamp1Valve,
    Clamp2Valve,
    ClampedProx1,
    ClampedProx2,
    Estop,
    FlipDirection,
    FlipToA,
    FlipToARbt,
    FlipToB,
    Holding,
    JigPlaced,
    JogLift1Up,
    JogMode,
    JogRotateA,
    Lift1,
    Lift1DnValve,
    Lift1UpValve,
    Lift2,
    Lift2DnValve,
    Lift2UpValve,
    LiftUpProx1,
    LiftUpProx2,
    ResetToHold,
    RotateToAValve,
    RotateToBValve,
    SetDown,
    SlideClampsIn1,
    SlideClampsOut1,
    Unclamp1Valve,
    Unclamp2Valve,
    UnclampedProx1,
    UnclampedProx2,
    logic,
)

DT = 0.010
SETTLE_SCANS = SETTLE_MS // 10


def _rest_on_b():
    AProx.value = False
    BProx.value = True
    ClampedProx1.value = False
    ClampedProx2.value = False
    UnclampedProx1.value = True
    UnclampedProx2.value = True
    LiftUpProx1.value = False
    LiftUpProx2.value = False
    JigPlaced.value = False
    FlipToARbt.value = False
    Estop.value = False
    JogMode.value = False


def _plc():
    return PLC(logic, dt=DT)


def _until(plc, tag, cycles=SETTLE_SCANS + 5):
    for _ in range(cycles):
        plc.step()
        if tag.value:
            return
    raise AssertionError(f"{tag.name} never came on")


def _assert_outputs_off():
    for tag in (
        Lift1UpValve,
        Lift1DnValve,
        Lift2UpValve,
        Lift2DnValve,
        Clamp1Valve,
        Clamp2Valve,
        Unclamp1Valve,
        Unclamp2Valve,
        RotateToAValve,
        RotateToBValve,
        AllowJigSense,
    ):
        assert tag.value is False, tag.name


def test_wait_in_hold_leaves_every_output_off():
    with _plc() as plc:
        _rest_on_b()
        plc.step()
        assert Holding.value is True
        _assert_outputs_off()


def test_each_lift_runs_until_its_own_prox():
    with _plc() as plc:
        _rest_on_b()
        plc.step()
        FlipToARbt.value = True
        plc.step()
        UnclampedProx1.value = False
        UnclampedProx2.value = False

        ClampedProx1.value = True
        plc.run(cycles=SETTLE_SCANS - 2)
        assert Lift1.value is False

        plc.run(cycles=3)
        assert Lift1.value is True
        assert SlideClampsIn1.value is False
        assert Lift1UpValve.value is True
        assert Lift2.value is False
        assert Lift2UpValve.value is False

        ClampedProx2.value = True
        plc.run(cycles=SETTLE_SCANS + 1)
        assert Lift2.value is True
        assert Lift2UpValve.value is True
        assert Lift1UpValve.value is True

        LiftUpProx1.value = True
        plc.step()
        assert Lift1UpValve.value is False
        assert Lift2UpValve.value is True
        assert FlipDirection.value is False

        LiftUpProx2.value = True
        plc.step()
        assert Lift2UpValve.value is False
        assert FlipDirection.value is False

        _until(plc, FlipDirection)
        assert FlipDirection.value is True
        assert FlipToA.value is True
        plc.step()
        assert FlipDirection.value is False
        assert FlipToA.value is True


def test_no_rotate_unless_both_clamps_are_in():
    with _plc() as plc:
        _rest_on_b()
        plc.step()
        JogMode.value = True
        JogRotateA.value = True
        plc.step()
        assert RotateToAValve.value is False

        ClampedProx1.value = True
        plc.step()
        assert RotateToAValve.value is False

        ClampedProx2.value = True
        plc.step()
        assert RotateToAValve.value is True

        ClampedProx1.value = False
        plc.step()
        assert RotateToAValve.value is False


def test_flip_to_a_from_b():
    with _plc() as plc:
        _rest_on_b()
        plc.step()
        assert Holding.value is True

        FlipToARbt.value = True
        plc.step()
        assert AStartCheck.value is True
        assert SlideClampsIn1.value is True
        UnclampedProx1.value = False
        UnclampedProx2.value = False
        assert Clamp1Valve.value is True
        plc.step()
        assert Holding.value is False
        assert AStartCheck.value is False
        assert SlideClampsIn1.value is True

        ClampedProx1.value = True
        ClampedProx2.value = True
        plc.run(cycles=SETTLE_SCANS + 1)
        assert Lift1.value is True
        assert Lift2.value is True
        assert Lift1UpValve.value is True
        assert Lift1DnValve.value is False

        LiftUpProx1.value = True
        LiftUpProx2.value = True
        _until(plc, FlipDirection)
        assert FlipToA.value is True
        assert RotateToAValve.value is True
        assert FlipToB.value is False
        assert Holding.value is False

        plc.step()
        assert FlipDirection.value is False
        assert FlipToA.value is True
        assert Lift1.value is False
        assert Lift2.value is False
        assert Lift1DnValve.value is False

        BProx.value = False
        AProx.value = True
        plc.step()
        assert SetDown.value is False
        assert FlipToA.value is True

        plc.run(cycles=SETTLE_SCANS + 1)
        assert SetDown.value is True
        assert FlipToA.value is False
        assert Lift1UpValve.value is False
        assert Lift1DnValve.value is True
        assert AllowJigSense.value is True

        JigPlaced.value = True
        plc.step()
        assert SlideClampsOut1.value is False

        plc.run(cycles=SETTLE_SCANS + 1)
        assert SlideClampsOut1.value is True
        assert SetDown.value is False
        assert Unclamp1Valve.value is True
        assert Clamp1Valve.value is False

        FlipToARbt.value = False
        UnclampedProx1.value = True
        UnclampedProx2.value = True
        plc.step()
        assert ResetToHold.value is True
        assert Unclamp1Valve.value is False

        plc.step()
        assert Holding.value is True
        assert ResetToHold.value is False
        assert SlideClampsOut1.value is False
        assert AStartCheck.value is False
        assert SlideClampsIn1.value is False
        _assert_outputs_off()


def test_estop_drops_all_valves():
    with _plc() as plc:
        _rest_on_b()
        plc.step()
        FlipToARbt.value = True
        ClampedProx1.value = True
        ClampedProx2.value = True
        plc.run(cycles=SETTLE_SCANS + 1)
        assert Lift1UpValve.value is True

        Estop.value = True
        plc.step()
        assert Lift1UpValve.value is False
        assert Lift1DnValve.value is False
        assert Clamp1Valve.value is False
        assert AllowJigSense.value is False


def test_jog_lift_while_stuck():
    with _plc() as plc:
        _rest_on_b()
        plc.step()
        JogMode.value = True
        JogLift1Up.value = True
        plc.step()
        assert Lift1UpValve.value is True
        assert Lift2UpValve.value is False
        assert Clamp1Valve.value is False
        assert Clamp2Valve.value is False


def test_opposing_rotate_valves_do_not_fire_together():
    with _plc() as plc:
        _rest_on_b()
        plc.step()
        FlipToARbt.value = True
        ClampedProx1.value = True
        ClampedProx2.value = True
        LiftUpProx1.value = True
        LiftUpProx2.value = True
        plc.run(cycles=SETTLE_SCANS * 2 + 4)
        assert RotateToAValve.value is True
        assert FlipToB.value is False
