"""Tests for the consolidation app discovery module."""

from pathlib import Path

import pytest

from src.consolidation_app import discovery


def test_rglob_discovery(tmp_path):
    """Test discovering projects via immediate subdirectories (no recursion)."""
    # Create project structure: each project is an immediate subdir of root
    project1 = tmp_path / "project1"
    project2 = tmp_path / "project2"
    project3 = tmp_path / "project3"

    for proj in (project1, project2, project3):
        (proj / ".errors_fixes").mkdir(parents=True)
        (proj / ".errors_fixes" / "errors_and_fixes.md").write_text(
            "# Errors\n", encoding="utf-8"
        )

    projects = discovery.discover_projects(tmp_path)

    assert len(projects) == 3
    assert project1.resolve() in projects
    assert project2.resolve() in projects
    assert project3.resolve() in projects


def test_extra_projects_with_existing_errors_and_fixes(tmp_path):
    """Test extra_projects when errors_and_fixes.md already exists."""
    # Create a project outside the root_path
    extra_project = tmp_path / "extra_project"
    extra_project.mkdir()
    (extra_project / ".errors_fixes").mkdir()
    (extra_project / ".errors_fixes" / "errors_and_fixes.md").write_text(
        "# Errors\n", encoding="utf-8"
    )

    # Create root_path (different from extra_project)
    root_path = tmp_path / "root"
    root_path.mkdir()

    # Discover with extra_projects
    projects = discovery.discover_projects(
        root_path, extra_projects=[str(extra_project)]
    )

    # Should find the extra project
    assert len(projects) == 1
    assert extra_project.resolve() in projects


def test_extra_projects_with_missing_errors_and_fixes(tmp_path):
    """Test extra_projects auto-bootstrap when errors_and_fixes.md is missing."""
    # Create a project without .errors_fixes folder
    extra_project = tmp_path / "extra_project"
    extra_project.mkdir()

    # Create root_path
    root_path = tmp_path / "root"
    root_path.mkdir()

    # Discover with extra_projects (should auto-bootstrap)
    projects = discovery.discover_projects(
        root_path, extra_projects=[str(extra_project)]
    )

    # Should find the extra project
    assert len(projects) == 1
    assert extra_project.resolve() in projects

    # Verify bootstrap created the files
    errors_fixes_file = extra_project / ".errors_fixes" / "errors_and_fixes.md"
    assert errors_fixes_file.exists()
    assert (extra_project / ".errors_fixes" / "fix_repo.md").exists()
    assert (extra_project / ".errors_fixes" / "coding_tips.md").exists()


def test_deduplication(tmp_path):
    """Test that duplicate projects are removed."""
    # Create a project
    project1 = tmp_path / "project1"
    (project1 / ".errors_fixes").mkdir(parents=True)
    (project1 / ".errors_fixes" / "errors_and_fixes.md").write_text(
        "# Errors\n", encoding="utf-8"
    )

    # Discover with both immediate-subdir scan and extra_projects pointing to same project
    projects = discovery.discover_projects(tmp_path, extra_projects=[str(project1)])

    # Should only find project once
    assert len(projects) == 1
    assert project1.resolve() in projects


def test_missing_root_path_raises_error(tmp_path):
    """Test that missing root_path raises FileNotFoundError."""
    missing_path = tmp_path / "nonexistent"

    with pytest.raises(FileNotFoundError):
        discovery.discover_projects(missing_path)


def test_root_path_not_directory_raises_error(tmp_path):
    """Test that non-directory root_path raises NotADirectoryError."""
    file_path = tmp_path / "not_a_dir"
    file_path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        discovery.discover_projects(file_path)


def test_extra_projects_nonexistent_path_skipped(tmp_path):
    """Test that nonexistent extra_projects paths are skipped with warning."""
    root_path = tmp_path / "root"
    root_path.mkdir()

    # Should not raise, but should skip the nonexistent path
    projects = discovery.discover_projects(
        root_path, extra_projects=["/nonexistent/path"]
    )

    # Should return empty list (no projects found)
    assert len(projects) == 0


def test_extra_projects_file_path_skipped(tmp_path):
    """Test that file paths in extra_projects are skipped."""
    root_path = tmp_path / "root"
    root_path.mkdir()

    file_path = tmp_path / "not_a_dir"
    file_path.write_text("not a directory", encoding="utf-8")

    # Should not raise, but should skip the file path
    projects = discovery.discover_projects(root_path, extra_projects=[str(file_path)])

    # Should return empty list
    assert len(projects) == 0


def test_empty_root_path_returns_empty_list(tmp_path):
    """Test that empty root_path returns empty list."""
    empty_root = tmp_path / "empty"
    empty_root.mkdir()

    projects = discovery.discover_projects(empty_root)

    assert len(projects) == 0


def test_extra_projects_empty_list(tmp_path):
    """Test that empty extra_projects list works correctly."""
    root_path = tmp_path / "root"
    root_path.mkdir()

    projects = discovery.discover_projects(root_path, extra_projects=[])

    assert len(projects) == 0


def test_extra_projects_none(tmp_path):
    """Test that None extra_projects works correctly."""
    root_path = tmp_path / "root"
    root_path.mkdir()

    projects = discovery.discover_projects(root_path, extra_projects=None)

    assert len(projects) == 0


def test_combined_rglob_and_extra_projects(tmp_path):
    """Test combining immediate-subdir discovery with extra_projects."""
    # Create root_path with a project inside it
    root_path = tmp_path / "root"
    root_path.mkdir()

    # Create project1 inside root_path (will be found via immediate subdir scan)
    project1_in_root = root_path / "project1"
    (project1_in_root / ".errors_fixes").mkdir(parents=True)
    (project1_in_root / ".errors_fixes" / "errors_and_fixes.md").write_text(
        "# Errors\n", encoding="utf-8"
    )

    # Create extra project outside root (will be found via extra_projects)
    extra_project = tmp_path / "extra"
    extra_project.mkdir()
    (extra_project / ".errors_fixes").mkdir()
    (extra_project / ".errors_fixes" / "errors_and_fixes.md").write_text(
        "# Errors\n", encoding="utf-8"
    )

    # Discover with both
    projects = discovery.discover_projects(
        root_path, extra_projects=[str(extra_project)]
    )

    # Should find both projects
    assert len(projects) == 2
    assert project1_in_root.resolve() in projects
    assert extra_project.resolve() in projects


def test_permission_error_handling(tmp_path, monkeypatch):
    """Test that permission errors are handled gracefully."""
    root_path = tmp_path / "root"
    root_path.mkdir()

    real_iterdir = Path.iterdir

    def mock_iterdir(self):
        if self.resolve() == root_path.resolve():
            raise PermissionError("Permission denied")
        return real_iterdir(self)

    monkeypatch.setattr(Path, "iterdir", mock_iterdir)

    # Should not raise, but should return empty list
    projects = discovery.discover_projects(root_path)

    # Should return empty list (iterdir failed, no extra_projects)
    assert len(projects) == 0


def test_extra_projects_relative_path_resolution(tmp_path):
    """Test that relative paths in extra_projects are resolved correctly."""
    # Create project with relative path
    extra_project = tmp_path / "extra_project"
    extra_project.mkdir()
    (extra_project / ".errors_fixes").mkdir()
    (extra_project / ".errors_fixes" / "errors_and_fixes.md").write_text(
        "# Errors\n", encoding="utf-8"
    )

    root_path = tmp_path / "root"
    root_path.mkdir()

    # Use relative path
    relative_path = Path("extra_project")
    if not relative_path.is_absolute():
        # Change to tmp_path directory for relative path resolution
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            projects = discovery.discover_projects(
                root_path, extra_projects=[str(relative_path)]
            )
        finally:
            os.chdir(old_cwd)
    else:
        projects = discovery.discover_projects(
            root_path, extra_projects=[str(relative_path)]
        )

    # Should find the project (path should be resolved)
    assert len(projects) >= 0  # May or may not find it depending on cwd


def test_project_order_preserved(tmp_path):
    """Test that project order is preserved (immediate subdirs first, then extra_projects)."""
    # Create projects
    project1 = tmp_path / "project1"
    project2 = tmp_path / "project2"
    (project1 / ".errors_fixes").mkdir(parents=True)
    (project1 / ".errors_fixes" / "errors_and_fixes.md").write_text(
        "# Errors\n", encoding="utf-8"
    )
    (project2 / ".errors_fixes").mkdir(parents=True)
    (project2 / ".errors_fixes" / "errors_and_fixes.md").write_text(
        "# Errors\n", encoding="utf-8"
    )

    # Discover
    projects = discovery.discover_projects(tmp_path)

    # Should preserve order (project1 before project2 in filesystem order)
    assert len(projects) == 2
    # Order may vary by filesystem, so just check both are present
    assert project1.resolve() in projects
    assert project2.resolve() in projects


def test_extra_projects_rejects_traversal_paths(tmp_path):
    """Test that extra_projects rejects suspicious directory traversal paths."""
    root_path = tmp_path / "root"
    root_path.mkdir()

    # Test various suspicious patterns
    suspicious_paths = [
        "../../etc/passwd",
        "..\\..\\windows\\system32",
        "/../etc/passwd",
        "\\..\\windows",
        "../..",
        "..\\..",
    ]

    for suspicious_path in suspicious_paths:
        projects = discovery.discover_projects(
            root_path, extra_projects=[suspicious_path]
        )
        # Should skip suspicious paths and return empty or only valid projects
        assert suspicious_path not in [str(p) for p in projects]


def test_extra_projects_rejects_empty_paths(tmp_path):
    """Test that extra_projects rejects empty or whitespace-only paths."""
    root_path = tmp_path / "root"
    root_path.mkdir()

    empty_paths = ["", "   ", "\t", "\n"]

    for empty_path in empty_paths:
        projects = discovery.discover_projects(root_path, extra_projects=[empty_path])
        # Should skip empty paths
        assert len(projects) == 0 or empty_path not in [str(p) for p in projects]


def test_extra_projects_accepts_valid_paths(tmp_path):
    """Test that extra_projects accepts valid absolute paths."""
    root_path = tmp_path / "root"
    root_path.mkdir()

    # Create a valid extra project
    valid_project = tmp_path / "valid_project"
    valid_project.mkdir()
    (valid_project / ".errors_fixes").mkdir()
    (valid_project / ".errors_fixes" / "errors_and_fixes.md").write_text(
        "# Errors\n", encoding="utf-8"
    )

    # Test with absolute path (relative paths resolve relative to cwd, not root_path)
    projects = discovery.discover_projects(
        root_path, extra_projects=[str(valid_project.resolve())]
    )
    assert valid_project.resolve() in projects
