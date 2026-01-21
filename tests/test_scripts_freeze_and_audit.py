"""Tests for scripts/freeze_and_audit.py."""

from __future__ import annotations

from types import SimpleNamespace

from scripts import freeze_and_audit


def test_freeze_and_audit_writes_requirements(tmp_path, monkeypatch):
    """Ensure main() writes requirements.txt and succeeds."""

    outputs = {
        "freeze": "package-one==1.0.0\npackage-two==2.0.0\n",
        "audit": "No vulnerabilities found\n",
    }
    calls = []

    def fake_run_command(cmd, description, capture_output=True):
        calls.append((cmd, description, capture_output))
        if "pip freeze" in cmd:
            return SimpleNamespace(returncode=0, stdout=outputs["freeze"])
        if "pip_audit" in cmd:
            return SimpleNamespace(returncode=0, stdout=outputs["audit"])
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(freeze_and_audit, "project_root", tmp_path)
    monkeypatch.setattr(freeze_and_audit, "run_command", fake_run_command)

    exit_code = freeze_and_audit.main()

    assert exit_code == 0
    assert (tmp_path / "requirements.txt").read_text() == outputs["freeze"]
    assert any("pip freeze" in call[0] for call in calls)
    assert any("pip_audit" in call[0] for call in calls)
