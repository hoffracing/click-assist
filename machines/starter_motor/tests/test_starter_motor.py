from pyrung import PLC

from machines.starter_motor.logic import (
    EstopOk,
    GuardClosed,
    Motor,
    OverloadOk,
    StartButton,
    StopPressed,
    logic,
)


def _healthy():
    StartButton.value = False
    StopPressed.value = False
    EstopOk.value = True
    GuardClosed.value = True
    OverloadOk.value = True
    Motor.value = False


def test_start_seals_in():
    with PLC(logic) as plc:
        _healthy()
        StartButton.value = True
        plc.step()
        assert Motor.value is True

        StartButton.value = False
        plc.step()
        assert Motor.value is True


def test_stop_drops_motor():
    with PLC(logic) as plc:
        _healthy()
        StartButton.value = True
        plc.step()
        StartButton.value = False
        StopPressed.value = True
        plc.step()
        assert Motor.value is False


def test_estop_drops_motor():
    with PLC(logic) as plc:
        _healthy()
        StartButton.value = True
        plc.step()
        StartButton.value = False
        EstopOk.value = False
        plc.step()
        assert Motor.value is False


def test_open_guard_drops_motor():
    with PLC(logic) as plc:
        _healthy()
        StartButton.value = True
        plc.step()
        StartButton.value = False
        GuardClosed.value = False
        plc.step()
        assert Motor.value is False


def test_overload_drops_motor():
    with PLC(logic) as plc:
        _healthy()
        StartButton.value = True
        plc.step()
        StartButton.value = False
        OverloadOk.value = False
        plc.step()
        assert Motor.value is False


def test_cannot_start_without_permissives():
    with PLC(logic) as plc:
        _healthy()
        StartButton.value = True
        EstopOk.value = False
        plc.step()
        assert Motor.value is False

        _healthy()
        StartButton.value = True
        GuardClosed.value = False
        plc.step()
        assert Motor.value is False

        _healthy()
        StartButton.value = True
        OverloadOk.value = False
        plc.step()
        assert Motor.value is False

        _healthy()
        StartButton.value = True
        StopPressed.value = True
        plc.step()
        assert Motor.value is False
