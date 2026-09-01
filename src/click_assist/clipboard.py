"""Encode ladder CSV and place it on the Click clipboard format."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

CLICK_CLIPBOARD_FORMAT = 522  # 0x020A, same as ClickNick


def encode_csv(csv_path: Path) -> bytes:
    from laddercodec import encode, read_csv

    rungs = read_csv(str(csv_path))
    return encode(rungs)


def copy_click_clipboard(data: bytes, *, require_click: bool = False) -> str:
    if sys.platform != "win32":
        raise RuntimeError("Click clipboard paste only works on Windows.")

    clicknick = shutil.which("clicknick-rung")
    if clicknick:
        return _copy_via_clicknick(clicknick, data)

    return _copy_via_win32(data, require_click=require_click)


def _copy_via_clicknick(exe: str, data: bytes) -> str:
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(suffix=".bin", delete=False) as handle:
        handle.write(data)
        tmp = Path(handle.name)
    try:
        completed = subprocess.run(
            [exe, "load", str(tmp)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                completed.stderr.strip() or completed.stdout.strip() or "clicknick-rung load failed"
            )
    finally:
        tmp.unlink(missing_ok=True)
    return "clicknick-rung"


def _copy_via_win32(data: bytes, *, require_click: bool) -> str:
    import ctypes
    import time

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    user32.OpenClipboard.argtypes = [ctypes.c_void_p]

    hwnd = _find_click_hwnd()
    if require_click and hwnd == 0:
        raise RuntimeError("CLICK Programming Software is not running.")

    gmem_moveable = 0x0002
    opened = False
    for _ in range(20):
        if user32.OpenClipboard(hwnd):
            opened = True
            break
        time.sleep(0.05)
    if not opened:
        raise RuntimeError("OpenClipboard failed. Close other clipboard users and retry.")

    try:
        if not user32.EmptyClipboard():
            raise RuntimeError("EmptyClipboard failed")
        hmem = kernel32.GlobalAlloc(gmem_moveable, len(data))
        if not hmem:
            raise RuntimeError("GlobalAlloc failed")
        ptr = kernel32.GlobalLock(hmem)
        if not ptr:
            kernel32.GlobalFree(hmem)
            raise RuntimeError("GlobalLock failed")
        ctypes.memmove(ptr, data, len(data))
        kernel32.GlobalUnlock(hmem)
        if not user32.SetClipboardData(CLICK_CLIPBOARD_FORMAT, hmem):
            kernel32.GlobalFree(hmem)
            raise RuntimeError("SetClipboardData failed")
    finally:
        user32.CloseClipboard()
    return "win32"


def _find_click_hwnd() -> int:
    if sys.platform != "win32":
        return 0
    try:
        import win32gui
    except ImportError:
        return 0

    found: list[int] = []

    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if "CLICK Programming Software" in title:
            found.append(hwnd)
        return True

    win32gui.EnumWindows(callback, None)
    return found[0] if found else 0
