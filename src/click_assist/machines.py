"""Discover machine packages under machines/."""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
MACHINES_DIR = REPO_ROOT / "machines"


@dataclass(frozen=True)
class Machine:
    name: str
    path: Path
    logic_module: ModuleType
    io_module: ModuleType

    @property
    def logic(self):
        return self.logic_module.logic

    @property
    def mapping(self):
        return self.io_module.mapping

    @property
    def export_dir(self) -> Path:
        return self.path / "export"

    @property
    def tests_dir(self) -> Path:
        return self.path / "tests"


def ensure_repo_on_path() -> None:
    root = str(REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def list_machine_names() -> list[str]:
    if not MACHINES_DIR.is_dir():
        return []
    names = []
    for child in sorted(MACHINES_DIR.iterdir()):
        if child.is_dir() and (child / "logic.py").is_file() and (child / "io_map.py").is_file():
            names.append(child.name)
    return names


def load_machine(name: str) -> Machine:
    ensure_repo_on_path()
    path = MACHINES_DIR / name
    if not path.is_dir():
        known = ", ".join(list_machine_names()) or "(none)"
        raise FileNotFoundError(f"Unknown machine {name!r}. Available: {known}")
    logic_module = importlib.import_module(f"machines.{name}.logic")
    io_module = importlib.import_module(f"machines.{name}.io_map")
    if not hasattr(logic_module, "logic"):
        raise AttributeError(f"{name}.logic must export `logic`")
    if not hasattr(io_module, "mapping"):
        raise AttributeError(f"{name}.io_map must export `mapping`")
    return Machine(name=name, path=path, logic_module=logic_module, io_module=io_module)
