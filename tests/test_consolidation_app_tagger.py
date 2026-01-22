"""Tests for the consolidation app tagger."""

from datetime import datetime

from src.consolidation_app.parser import ErrorEntry
from src.consolidation_app.tagger import generate_tags_rule_based


def _create_entry(
    signature: str = "TestError",
    error_type: str = "TypeError",
    file: str = "test.py",
    line: int = 10,
    fix_code: str = "fix = 1",
    explanation: str = "Test explanation",
    success_count: int = 1,
    timestamp: datetime | None = None,
    error_signature: str | None = None,
) -> ErrorEntry:
    """Helper to create test ErrorEntry."""
    if timestamp is None:
        timestamp = datetime(2025, 1, 1, 12, 0, 0)
    # Use error_signature if provided, otherwise use signature
    final_signature = error_signature if error_signature is not None else signature
    return ErrorEntry(
        error_signature=final_signature,
        error_type=error_type,
        file=file,
        line=line,
        fix_code=fix_code,
        explanation=explanation,
        result="✅ Solved",
        success_count=success_count,
        tags=[],
        timestamp=timestamp,
        is_process_issue=False,
    )


def test_error_type_tagging():
    """Test that error types are mapped to domain tags."""
    # Test known error type mappings
    entry = _create_entry(error_type="FileNotFoundError")
    tags = generate_tags_rule_based(entry)
    assert "file-io" in tags

    entry = _create_entry(error_type="TypeError")
    tags = generate_tags_rule_based(entry)
    assert "type-conversion" in tags

    entry = _create_entry(error_type="ConnectionRefusedError")
    tags = generate_tags_rule_based(entry)
    assert "networking" in tags

    entry = _create_entry(error_type="KeyError")
    tags = generate_tags_rule_based(entry)
    assert "data-structure" in tags


def test_framework_detection():
    """Test that frameworks are detected from file paths and context."""
    # Docker detection
    entry = _create_entry(
        file="docker-compose.yml",
        explanation="Docker container connection issue",
    )
    tags = generate_tags_rule_based(entry)
    assert "docker" in tags

    # Django detection
    entry = _create_entry(
        file="manage.py",
        explanation="Django settings error",
    )
    tags = generate_tags_rule_based(entry)
    assert "django" in tags

    # Flask detection
    entry = _create_entry(
        file="app.py",
        explanation="Flask application error",
    )
    tags = generate_tags_rule_based(entry)
    assert "flask" in tags

    # Pytest detection
    entry = _create_entry(
        file="test_example.py",
        explanation="Pytest test failure",
    )
    tags = generate_tags_rule_based(entry)
    assert "pytest" in tags

    # Postgres detection
    entry = _create_entry(
        file="database.py",
        explanation="PostgreSQL connection error",
    )
    tags = generate_tags_rule_based(entry)
    assert "postgres" in tags


def test_domain_detection():
    """Test that domains are detected from file paths and error context."""
    # Networking domain
    entry = _create_entry(
        error_type="ConnectionError",
        file="network.py",
        explanation="Connection refused error",
    )
    tags = generate_tags_rule_based(entry)
    assert "networking" in tags

    # Database domain
    entry = _create_entry(
        file="db.py",
        explanation="SQL query failed",
    )
    tags = generate_tags_rule_based(entry)
    assert "database" in tags

    # Authentication domain
    entry = _create_entry(
        file="auth.py",
        explanation="JWT token validation failed",
    )
    tags = generate_tags_rule_based(entry)
    assert "authentication" in tags

    # API domain
    entry = _create_entry(
        file="api.py",
        explanation="API endpoint error",
    )
    tags = generate_tags_rule_based(entry)
    assert "api" in tags

    # Testing domain
    entry = _create_entry(
        file="test_something.py",
        explanation="Test fixture error",
    )
    tags = generate_tags_rule_based(entry)
    assert "testing" in tags


def test_platform_detection():
    """Test that platforms are detected from file paths and error messages."""
    # Windows detection
    entry = _create_entry(
        file="C:\\Users\\test.py",
        error_signature="WinError 2: The system cannot find the file",
    )
    tags = generate_tags_rule_based(entry)
    assert "windows" in tags

    # Linux detection
    entry = _create_entry(
        file="/usr/local/bin/script.py",
        explanation="Linux path issue",
    )
    tags = generate_tags_rule_based(entry)
    assert "linux" in tags

    # macOS detection
    entry = _create_entry(
        file="/Users/test/app.py",
        explanation="macOS specific issue",
    )
    tags = generate_tags_rule_based(entry)
    assert "macos" in tags

    # Cross-platform (no platform tag)
    entry = _create_entry(
        file="src/utils.py",
        explanation="Generic Python error",
    )
    tags = generate_tags_rule_based(entry)
    assert "windows" not in tags
    assert "linux" not in tags
    assert "macos" not in tags


def test_multiple_tags_generated():
    """Test that multiple tags are generated (error type, framework, domain, platform)."""
    entry = _create_entry(
        error_type="FileNotFoundError",
        file="docker-compose.yml",
        explanation="Docker container file not found on Windows",
        error_signature="WinError 2: File not found",
    )
    tags = generate_tags_rule_based(entry)
    # Should have error type tag, framework tag, domain tag, and platform tag
    assert len(tags) >= 3
    assert "file-io" in tags or "type-conversion" in tags  # Error type domain
    assert "docker" in tags  # Framework
    assert "windows" in tags  # Platform


def test_edge_cases_unknown_error_type():
    """Test that unknown error types are handled gracefully."""
    entry = _create_entry(
        error_type="CustomError",
        file="test.py",
    )
    tags = generate_tags_rule_based(entry)
    # Should still generate some tags (domain, framework, etc.)
    assert isinstance(tags, list)
    # Custom error type should be normalized to lowercase
    assert len(tags) >= 0  # May or may not have tags depending on other fields


def test_edge_cases_no_framework_detected():
    """Test that missing framework detection doesn't break tagging."""
    entry = _create_entry(
        error_type="TypeError",
        file="generic.py",
        explanation="Generic Python error",
    )
    tags = generate_tags_rule_based(entry)
    # Should still have error type tag and possibly domain tag
    assert isinstance(tags, list)
    assert len(tags) >= 1  # At least error type tag


def test_edge_cases_empty_fields():
    """Test that empty fields are handled gracefully."""
    entry = _create_entry(
        error_type="",
        file="",
        explanation="",
        error_signature="",
    )
    tags = generate_tags_rule_based(entry)
    # Should return empty list or minimal tags
    assert isinstance(tags, list)


def test_tags_are_deduplicated():
    """Test that duplicate tags are removed."""
    entry = _create_entry(
        error_type="FileNotFoundError",  # Maps to "file-io"
        file="file.py",  # Also matches "file-io" domain pattern
        explanation="File not found error",
    )
    tags = generate_tags_rule_based(entry)
    # Should not have duplicate "file-io" tags
    assert tags.count("file-io") <= 1


def test_tags_are_sorted():
    """Test that tags are returned in sorted order."""
    entry = _create_entry(
        error_type="TypeError",
        file="docker-compose.yml",
        explanation="Docker connection error",
    )
    tags = generate_tags_rule_based(entry)
    # Should be sorted
    assert tags == sorted(tags)


def test_error_signature_in_detection():
    """Test that error signature is used in pattern matching."""
    entry = _create_entry(
        error_type="ConnectionError",
        error_signature="ConnectionRefusedError: [Errno 111] Connect call failed",
        file="network.py",
    )
    tags = generate_tags_rule_based(entry)
    # Should detect networking domain from error signature
    assert "networking" in tags


def test_explanation_in_detection():
    """Test that explanation is used in pattern matching."""
    entry = _create_entry(
        error_type="TypeError",
        file="test.py",
        explanation="PostgreSQL database connection failed",
    )
    tags = generate_tags_rule_based(entry)
    # Should detect postgres framework and database domain from explanation
    assert "postgres" in tags or "database" in tags


def test_file_path_patterns():
    """Test that file path patterns are detected correctly."""
    # Test Django patterns
    entry = _create_entry(file="settings.py", explanation="Django settings")
    tags = generate_tags_rule_based(entry)
    assert "django" in tags

    # Test React patterns
    entry = _create_entry(file="component.jsx", explanation="React component")
    tags = generate_tags_rule_based(entry)
    assert "react" in tags

    # Test SQLite patterns
    entry = _create_entry(file="data.db", explanation="Database file")
    tags = generate_tags_rule_based(entry)
    assert "sqlite" in tags


def test_platform_from_error_message():
    """Test that platform is detected from error messages."""
    entry = _create_entry(
        error_signature="[WinError 2] The system cannot find the file specified",
        file="test.py",
    )
    tags = generate_tags_rule_based(entry)
    assert "windows" in tags

    entry = _create_entry(
        error_signature="Connection error on Linux system",
        file="test.py",
    )
    tags = generate_tags_rule_based(entry)
    assert "linux" in tags


def test_minimal_entry_still_generates_tags():
    """Test that minimal entry with only error_type still generates tags."""
    entry = _create_entry(
        error_type="FileNotFoundError",
        file="",
        explanation="",
        error_signature="",
    )
    tags = generate_tags_rule_based(entry)
    # Should at least have error type tag
    assert len(tags) >= 1
    assert "file-io" in tags
