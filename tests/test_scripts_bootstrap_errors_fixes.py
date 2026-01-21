# File: tests/test_scripts_bootstrap_errors_fixes.py
# Description: Unit tests for bootstrap_errors_fixes.py script
# Version: 1.0


import pytest

from scripts.bootstrap_errors_fixes import (
    bootstrap_project,
    create_coding_tips_file,
    create_errors_and_fixes_file,
    create_errors_fixes_directory,
    create_fix_repo_file,
    update_gitignore,
)


class TestCreateErrorsFixesDirectory:
    """Test create_errors_fixes_directory function."""

    def test_create_directory_success(self, tmp_path):
        """Test successful directory creation."""
        errors_fixes_dir = create_errors_fixes_directory(tmp_path)

        assert errors_fixes_dir.exists()
        assert errors_fixes_dir.is_dir()
        assert errors_fixes_dir.name == ".errors_fixes"
        assert errors_fixes_dir.parent == tmp_path

    def test_create_directory_already_exists(self, tmp_path):
        """Test directory creation when directory already exists."""
        # Create directory first
        existing_dir = tmp_path / ".errors_fixes"
        existing_dir.mkdir()

        # Should not raise error
        errors_fixes_dir = create_errors_fixes_directory(tmp_path)

        assert errors_fixes_dir.exists()
        assert errors_fixes_dir == existing_dir


class TestCreateErrorsAndFixesFile:
    """Test create_errors_and_fixes_file function."""

    def test_create_file_success(self, tmp_path):
        """Test successful file creation."""
        errors_fixes_dir = tmp_path / ".errors_fixes"
        errors_fixes_dir.mkdir()

        create_errors_and_fixes_file(errors_fixes_dir)

        file_path = errors_fixes_dir / "errors_and_fixes.md"
        assert file_path.exists()
        assert file_path.is_file()

        content = file_path.read_text(encoding="utf-8")
        assert "# Errors and Fixes Log" in content
        assert "processed daily by the consolidation app" in content

    def test_create_file_already_exists(self, tmp_path):
        """Test file creation when file already exists."""
        errors_fixes_dir = tmp_path / ".errors_fixes"
        errors_fixes_dir.mkdir()
        file_path = errors_fixes_dir / "errors_and_fixes.md"
        file_path.write_text("existing content", encoding="utf-8")

        # Should not raise error, should skip
        create_errors_and_fixes_file(errors_fixes_dir)

        # Content should remain unchanged
        content = file_path.read_text(encoding="utf-8")
        assert content == "existing content"

    def test_file_has_lf_line_endings(self, tmp_path):
        """Test that file uses LF line endings."""
        errors_fixes_dir = tmp_path / ".errors_fixes"
        errors_fixes_dir.mkdir()

        create_errors_and_fixes_file(errors_fixes_dir)

        file_path = errors_fixes_dir / "errors_and_fixes.md"
        content = file_path.read_bytes()
        # Should not contain CRLF (\r\n), only LF (\n)
        assert b"\r\n" not in content
        # Should contain LF
        assert b"\n" in content


class TestCreateFixRepoFile:
    """Test create_fix_repo_file function."""

    def test_create_file_success(self, tmp_path):
        """Test successful file creation."""
        errors_fixes_dir = tmp_path / ".errors_fixes"
        errors_fixes_dir.mkdir()

        create_fix_repo_file(errors_fixes_dir)

        file_path = errors_fixes_dir / "fix_repo.md"
        assert file_path.exists()
        assert file_path.is_file()

        content = file_path.read_text(encoding="utf-8")
        assert "# Fix Repository" in content
        assert "Last Updated:" in content
        assert "Total Entries:" in content
        assert "0" in content

    def test_create_file_already_exists(self, tmp_path):
        """Test file creation when file already exists."""
        errors_fixes_dir = tmp_path / ".errors_fixes"
        errors_fixes_dir.mkdir()
        file_path = errors_fixes_dir / "fix_repo.md"
        file_path.write_text("existing content", encoding="utf-8")

        # Should not raise error, should skip
        create_fix_repo_file(errors_fixes_dir)

        # Content should remain unchanged
        content = file_path.read_text(encoding="utf-8")
        assert content == "existing content"

    def test_file_has_lf_line_endings(self, tmp_path):
        """Test that file uses LF line endings."""
        errors_fixes_dir = tmp_path / ".errors_fixes"
        errors_fixes_dir.mkdir()

        create_fix_repo_file(errors_fixes_dir)

        file_path = errors_fixes_dir / "fix_repo.md"
        content = file_path.read_bytes()
        # Should not contain CRLF (\r\n), only LF (\n)
        assert b"\r\n" not in content
        # Should contain LF
        assert b"\n" in content


class TestCreateCodingTipsFile:
    """Test create_coding_tips_file function."""

    def test_create_file_success(self, tmp_path):
        """Test successful file creation."""
        errors_fixes_dir = tmp_path / ".errors_fixes"
        errors_fixes_dir.mkdir()

        create_coding_tips_file(errors_fixes_dir)

        file_path = errors_fixes_dir / "coding_tips.md"
        assert file_path.exists()
        assert file_path.is_file()

        content = file_path.read_text(encoding="utf-8")
        assert "# Coding Tips - Agent Process Rules" in content
        assert "Last Updated:" in content
        assert "Total Rules:" in content
        assert "0" in content

    def test_create_file_already_exists(self, tmp_path):
        """Test file creation when file already exists."""
        errors_fixes_dir = tmp_path / ".errors_fixes"
        errors_fixes_dir.mkdir()
        file_path = errors_fixes_dir / "coding_tips.md"
        file_path.write_text("existing content", encoding="utf-8")

        # Should not raise error, should skip
        create_coding_tips_file(errors_fixes_dir)

        # Content should remain unchanged
        content = file_path.read_text(encoding="utf-8")
        assert content == "existing content"

    def test_file_has_lf_line_endings(self, tmp_path):
        """Test that file uses LF line endings."""
        errors_fixes_dir = tmp_path / ".errors_fixes"
        errors_fixes_dir.mkdir()

        create_coding_tips_file(errors_fixes_dir)

        file_path = errors_fixes_dir / "coding_tips.md"
        content = file_path.read_bytes()
        # Should not contain CRLF (\r\n), only LF (\n)
        assert b"\r\n" not in content
        # Should contain LF
        assert b"\n" in content


class TestUpdateGitignore:
    """Test update_gitignore function."""

    def test_create_new_gitignore(self, tmp_path):
        """Test creating new .gitignore when it doesn't exist."""
        update_gitignore(tmp_path)

        gitignore_path = tmp_path / ".gitignore"
        assert gitignore_path.exists()

        content = gitignore_path.read_text(encoding="utf-8")
        assert ".errors_fixes/" in content

    def test_add_entry_to_existing_gitignore(self, tmp_path):
        """Test adding entry to existing .gitignore."""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("*.pyc\n__pycache__/\n", encoding="utf-8")

        update_gitignore(tmp_path)

        content = gitignore_path.read_text(encoding="utf-8")
        assert ".errors_fixes/" in content
        assert "*.pyc" in content
        assert "__pycache__/" in content

    def test_skip_if_entry_already_exists(self, tmp_path):
        """Test skipping if entry already exists in .gitignore."""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text(".errors_fixes/\n*.pyc\n", encoding="utf-8")

        update_gitignore(tmp_path)

        # Content should be unchanged (or same structure)
        content = gitignore_path.read_text(encoding="utf-8")
        assert ".errors_fixes/" in content
        # Should only appear once
        assert content.count(".errors_fixes/") == 1

    def test_skip_if_entry_without_slash_exists(self, tmp_path):
        """Test skipping if entry without trailing slash exists."""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text(".errors_fixes\n*.pyc\n", encoding="utf-8")

        update_gitignore(tmp_path)

        content = gitignore_path.read_text(encoding="utf-8")
        # Should not add duplicate
        assert content.count(".errors_fixes") == 1

    def test_file_has_lf_line_endings(self, tmp_path):
        """Test that .gitignore uses LF line endings."""
        update_gitignore(tmp_path)

        gitignore_path = tmp_path / ".gitignore"
        content = gitignore_path.read_bytes()
        # Should not contain CRLF (\r\n), only LF (\n)
        assert b"\r\n" not in content
        # Should contain LF
        assert b"\n" in content


class TestBootstrapProject:
    """Test bootstrap_project function."""

    def test_bootstrap_success(self, tmp_path):
        """Test successful bootstrap of project."""
        bootstrap_project(tmp_path, update_gitignore_flag=True)

        # Check directory exists
        errors_fixes_dir = tmp_path / ".errors_fixes"
        assert errors_fixes_dir.exists()
        assert errors_fixes_dir.is_dir()

        # Check files exist
        assert (errors_fixes_dir / "errors_and_fixes.md").exists()
        assert (errors_fixes_dir / "fix_repo.md").exists()
        assert (errors_fixes_dir / "coding_tips.md").exists()

        # Check .gitignore updated
        gitignore_path = tmp_path / ".gitignore"
        assert gitignore_path.exists()
        assert ".errors_fixes/" in gitignore_path.read_text(encoding="utf-8")

    def test_bootstrap_without_gitignore(self, tmp_path):
        """Test bootstrap without updating .gitignore."""
        bootstrap_project(tmp_path, update_gitignore_flag=False)

        # Check directory and files exist
        errors_fixes_dir = tmp_path / ".errors_fixes"
        assert errors_fixes_dir.exists()
        assert (errors_fixes_dir / "errors_and_fixes.md").exists()
        assert (errors_fixes_dir / "fix_repo.md").exists()
        assert (errors_fixes_dir / "coding_tips.md").exists()

        # Check .gitignore not created
        gitignore_path = tmp_path / ".gitignore"
        if gitignore_path.exists():
            assert ".errors_fixes/" not in gitignore_path.read_text(encoding="utf-8")

    def test_bootstrap_project_path_not_exists(self, tmp_path):
        """Test bootstrap fails when project path doesn't exist."""
        non_existent_path = tmp_path / "non_existent"

        with pytest.raises(FileNotFoundError):
            bootstrap_project(non_existent_path)

    def test_bootstrap_project_path_not_directory(self, tmp_path):
        """Test bootstrap fails when project path is not a directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            bootstrap_project(file_path)

    def test_bootstrap_handles_existing_directory(self, tmp_path):
        """Test bootstrap handles existing .errors_fixes directory gracefully."""
        # Create directory and one file first
        errors_fixes_dir = tmp_path / ".errors_fixes"
        errors_fixes_dir.mkdir()
        existing_file = errors_fixes_dir / "errors_and_fixes.md"
        existing_file.write_text("existing content", encoding="utf-8")

        # Bootstrap should complete without error
        bootstrap_project(tmp_path, update_gitignore_flag=False)

        # Existing file should remain unchanged
        assert existing_file.read_text(encoding="utf-8") == "existing content"

        # Other files should be created
        assert (errors_fixes_dir / "fix_repo.md").exists()
        assert (errors_fixes_dir / "coding_tips.md").exists()
