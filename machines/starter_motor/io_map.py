"""Click address map for the starter motor example."""

from pyrung.click import ClickBlocks, TagMap

from machines.starter_motor.logic import (
    EstopOk,
    GuardClosed,
    Motor,
    OverloadOk,
    StartButton,
    StopPressed,
)

blocks = ClickBlocks()

mapping = TagMap(
    {
        StartButton: blocks.x[1],
        StopPressed: blocks.x[2],
        EstopOk: blocks.x[3],
        GuardClosed: blocks.x[4],
        OverloadOk: blocks.x[5],
        Motor: blocks.y[1],
    }
)
