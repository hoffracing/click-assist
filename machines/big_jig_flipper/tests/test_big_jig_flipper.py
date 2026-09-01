from pyrung import PLC

from machines.big_jig_flipper.logic import (
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
    Lift1,
    Lift1DnValve,
    Lift1UpValve,
    Lift2,
    Lift2UpValve,
    LiftUpProx1,
    LiftUpProx2,
    ResetToHold,
    RotateToAValve,
    SetDown,
    SlideClampsIn1,
    SlideClampsOut1,
    Unclamp1Valve,
    UnclampedProx1,
    UnclampedProx2,
    logic,
)


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


def test_first_scan_seals_holding_and_allows_jig_sense():
    with PLC(logic) as plc:
        _rest_on_b()
        plc.step()
        assert Holding.value is True
        assert AllowJigSense.value is True
        assert Lift1DnValve.value is True
        assert Lift1UpValve.value is False


def test_each_lift_runs_until_its_own_prox():
    with PLC(logic) as plc:
        _rest_on_b()
        plc.step()
        FlipToARbt.value = True
        plc.step()
        UnclampedProx1.value = False
        UnclampedProx2.value = False

        ClampedProx1.value = True
        plc.step()
        assert Lift1.value is True
        assert Lift1UpValve.value is True
        assert Lift2.value is False
        assert Lift2UpValve.value is False

        ClampedProx2.value = True
        plc.step()
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
        assert FlipDirection.value is True


def test_flip_to_a_from_b():
    with PLC(logic) as plc:
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

        ClampedProx1.value = True
        ClampedProx2.value = True
        plc.step()
        assert Lift1.value is True
        assert Lift2.value is True
        assert Lift1UpValve.value is True
        assert Lift1DnValve.value is False

        LiftUpProx1.value = True
        LiftUpProx2.value = True
        plc.step()
        assert FlipDirection.value is True
        assert FlipToA.value is True
        assert RotateToAValve.value is True
        assert FlipToB.value is False

        BProx.value = False
        AProx.value = True
        plc.step()
        assert SetDown.value is True
        assert Lift1UpValve.value is False
        assert Lift1DnValve.value is True

        JigPlaced.value = True
        plc.step()
        assert SlideClampsOut1.value is True
        assert Unclamp1Valve.value is True
        assert Clamp1Valve.value is False

        UnclampedProx1.value = True
        UnclampedProx2.value = True
        plc.step()
        assert ResetToHold.value is True
        assert Unclamp1Valve.value is False


def test_estop_drops_all_valves():
    with PLC(logic) as plc:
        _rest_on_b()
        plc.step()
        FlipToARbt.value = True
        ClampedProx1.value = True
        ClampedProx2.value = True
        plc.step()
        assert Lift1UpValve.value is True

        Estop.value = True
        plc.step()
        assert Lift1UpValve.value is False
        assert Lift1DnValve.value is False
        assert Clamp1Valve.value is False
        assert AllowJigSense.value is False


def test_jog_lift_while_stuck():
    with PLC(logic) as plc:
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
    with PLC(logic) as plc:
        _rest_on_b()
        plc.step()
        FlipToARbt.value = True
        ClampedProx1.value = True
        ClampedProx2.value = True
        LiftUpProx1.value = True
        LiftUpProx2.value = True
        plc.run(cycles=4)
        assert RotateToAValve.value is True
        assert FlipToB.value is False
