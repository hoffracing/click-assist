"""Seal-in motor starter with E-stop and interlocks."""

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
