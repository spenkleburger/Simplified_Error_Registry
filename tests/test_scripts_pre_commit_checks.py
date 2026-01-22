"""Tests for scripts/pre_commit_checks.py."""

from __future__ import annotations

import importlib.util
import warnings
from pathlib import Path
from types import ModuleType
from typing import Iterable

import pytest

# Check if pre_commit_checks module exists
try:
    from scripts import pre_commit_checks
except ImportError:
    pre_commit_checks = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIRECTORIES = [
    ("scripts", PROJECT_ROOT / "scripts"),
    ("src", PROJECT_ROOT / "src"),
]


def _load_module(module_name: str, file_path: Path) -> ModuleType:
    """Load a module from a file path without caching."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {module_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _iter_python_files(directory: Path) -> Iterable[Path]:
    return (
        path
        for path in directory.rglob("*.py")
        if path.name != "__init__.py" and ".pytest_cache" not in path.parts
    )


@pytest.mark.skipif(
    pre_commit_checks is None,
    reason="pre_commit_checks module not found (script may not be implemented yet)",
)
def test_main_exits_zero_when_no_modified_files(monkeypatch):
    """Ensure main() short-circuits cleanly when nothing changed."""

    monkeypatch.setattr(pre_commit_checks, "get_modified_files", lambda: [])
    exit_code = pre_commit_checks.main()
    assert exit_code == 0


def test_python_scripts_are_importable():
    """Import every python file in scripts/ (and src/ if present)."""

    for label, directory in SCRIPT_DIRECTORIES:
        if not directory.exists():
            warnings.warn(
                f"{label} directory not found; skipping import checks",
                UserWarning,
                stacklevel=2,
            )
            continue

        python_files = list(_iter_python_files(directory))
        if not python_files:
            warnings.warn(
                f"No Python files found in {label} directory; skipping import checks",
                UserWarning,
                stacklevel=2,
            )
            continue

        for file_path in python_files:
            module_name = ".".join(
                file_path.relative_to(PROJECT_ROOT).with_suffix("").parts
            )
            _load_module(module_name, file_path)
