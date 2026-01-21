"""Tests for docs/PORTS.md."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PORTS_DOC = PROJECT_ROOT / "docs" / "PORTS.md"


@pytest.mark.skipif(not PORTS_DOC.exists(), reason="PORTS.md not found")
def test_ports_document_has_required_sections():
    """Ensure PORTS.md includes development and production sections."""

    contents = PORTS_DOC.read_text(encoding="utf-8")
    assert "## Development Ports" in contents
    assert "## Production Ports" in contents
    assert "| Service | Port | Protocol | Description |" in contents


@pytest.mark.skipif(not PORTS_DOC.exists(), reason="PORTS.md not found")
def test_ports_document_has_placeholders():
    """Ensure table includes placeholder entries for customization."""

    contents = PORTS_DOC.read_text(encoding="utf-8")
    assert "xxxx" in contents  # Template placeholders should remain
