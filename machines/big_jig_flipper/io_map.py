"""Click address map for the big jig flipper.

X101-X109 proxes and robot handshake.
Y201-Y211 hydraulic valves.
C1-C14 sequencer. C101/C102 robot flip requests.
C20 E-stop. C21 jog mode. C22-C31 jog pushes for the Click app.

Analog clamp (voltage linear sensor) is not mapped yet. When it lands, use a
DF register for the raw volts and compare in calc() rungs. Do not reuse these
X/Y/C addresses.
"""

from pyrung.click import ClickBlocks, TagMap

from machines.big_jig_flipper.logic import (
    AProx,
    AStartCheck,
    AllowJigSense,
    BProx,
    BStartCheck,
    Clamp1Valve,
    Clamp2Valve,
    ClampedProx1,
    ClampedProx2,
    Estop,
    FlipDirection,
    FlipToA,
    FlipToARbt,
    FlipToB,
    FlipToBRbt,
    Holding,
    JigPlaced,
    JogClamp1In,
    JogClamp1Out,
    JogClamp2In,
    JogClamp2Out,
    JogLift1Dn,
    JogLift1Up,
    JogLift2Dn,
    JogLift2Up,
    JogMode,
    JogRotateA,
    JogRotateB,
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
    SlideClampsIn2,
    SlideClampsOut1,
    SlideClampsOut2,
    Unclamp1Valve,
    Unclamp2Valve,
    UnclampedProx1,
    UnclampedProx2,
)

blocks = ClickBlocks()

mapping = TagMap(
    {
        AProx: blocks.x[101],
        BProx: blocks.x[102],
        ClampedProx1: blocks.x[103],
        ClampedProx2: blocks.x[104],
        UnclampedProx1: blocks.x[105],
        UnclampedProx2: blocks.x[106],
        LiftUpProx1: blocks.x[107],
        LiftUpProx2: blocks.x[108],
        JigPlaced: blocks.x[109],
        Lift1UpValve: blocks.y[201],
        Lift1DnValve: blocks.y[202],
        Lift2UpValve: blocks.y[203],
        Lift2DnValve: blocks.y[204],
        Clamp1Valve: blocks.y[205],
        Unclamp1Valve: blocks.y[206],
        Clamp2Valve: blocks.y[207],
        Unclamp2Valve: blocks.y[208],
        RotateToAValve: blocks.y[209],
        RotateToBValve: blocks.y[210],
        AllowJigSense: blocks.y[211],
        Holding: blocks.c[1],
        AStartCheck: blocks.c[2],
        BStartCheck: blocks.c[3],
        SlideClampsIn1: blocks.c[4],
        SlideClampsIn2: blocks.c[5],
        Lift1: blocks.c[6],
        Lift2: blocks.c[7],
        FlipDirection: blocks.c[8],
        FlipToA: blocks.c[9],
        FlipToB: blocks.c[10],
        SetDown: blocks.c[11],
        SlideClampsOut1: blocks.c[12],
        SlideClampsOut2: blocks.c[13],
        ResetToHold: blocks.c[14],
        FlipToARbt: blocks.c[101],
        FlipToBRbt: blocks.c[102],
        Estop: blocks.c[20],
        JogMode: blocks.c[21],
        JogLift1Up: blocks.c[22],
        JogLift1Dn: blocks.c[23],
        JogLift2Up: blocks.c[24],
        JogLift2Dn: blocks.c[25],
        JogClamp1In: blocks.c[26],
        JogClamp1Out: blocks.c[27],
        JogClamp2In: blocks.c[28],
        JogClamp2Out: blocks.c[29],
        JogRotateA: blocks.c[30],
        JogRotateB: blocks.c[31],
    }
)
