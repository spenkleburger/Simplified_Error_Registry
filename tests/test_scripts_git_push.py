"""Tests for scripts/git_push.py."""

from __future__ import annotations

import builtins
from types import SimpleNamespace

from scripts import git_push


def test_git_push_cancel_on_empty_commit(monkeypatch):
    """main() should abort when commit message is empty."""

    calls = []

    def fake_run_command(cmd, check=True):
        calls.append(cmd)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(git_push, "run_command", fake_run_command)
    monkeypatch.setattr(builtins, "input", lambda prompt="": "")

    exit_code = git_push.main()

    assert exit_code == 1
    assert calls == [[git_push.GIT_BINARY, "add", "."]]


def test_git_push_happy_path(monkeypatch):
    """main() should run add/commit/push when message is provided."""

    calls = []

    def fake_run_command(cmd, check=True):
        calls.append(cmd)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(git_push, "run_command", fake_run_command)
    monkeypatch.setattr(builtins, "input", lambda prompt="": "feat: add tests")

    exit_code = git_push.main()

    assert exit_code == 0
    assert calls == [
        [git_push.GIT_BINARY, "add", "."],
        [git_push.GIT_BINARY, "commit", "-m", "feat: add tests"],
        [git_push.GIT_BINARY, "push"],
    ]
