# File: scripts/check_dependencies.py
# Description: Check if requirements.txt contains all dependencies used in the codebase
# Usage: python scripts/check_dependencies.py

"""
Check if requirements.txt contains all dependencies used in the codebase.

This script:
1. Scans all Python files for imports
2. Identifies third-party packages (not stdlib, not local project modules)
3. Compares against requirements.txt
4. Reports missing dependencies

Local project modules are automatically excluded:
- src (local package)
- config (local config module)
- scripts (local scripts directory)
- Individual script files (e.g., bootstrap_errors_fixes)
"""

from __future__ import annotations

import ast
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set

# Standard library modules (don't need to be in requirements.txt)
STDLIB_MODULES = {
    # Core
    "abc", "argparse", "array", "ast", "asyncio", "atexit", "base64", "binascii",
    "bisect", "builtins", "bz2", "calendar", "cmath", "codecs", "collections",
    "collections.abc", "contextlib", "copy", "copyreg", "csv", "dataclasses",
    "datetime", "decimal", "difflib", "dis", "doctest", "email", "encodings",
    "enum", "errno", "faulthandler", "fcntl", "fractions", "functools", "gc",
    "getopt", "getpass", "gettext", "glob", "graphlib", "grp", "gzip", "hashlib",
    "heapq", "hmac", "html", "http", "imaplib", "importlib", "inspect", "io",
    "ipaddress", "itertools", "json", "keyword", "lib2to3", "linecache", "locale",
    "logging", "lzma", "mailbox", "marshal", "math", "mimetypes", "mmap", "modulefinder",
    "msilib", "msvcrt", "multiprocessing", "netrc", "nis", "nntplib", "nt", "ntpath",
    "nturl2path", "numbers", "opcode", "operator", "optparse", "os", "ossaudiodev",
    "pathlib", "pdb", "pickle", "pickletools", "pipes", "pkgutil", "platform",
    "plistlib", "poplib", "posix", "posixpath", "pprint", "profile", "pstats",
    "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue", "quopri", "random",
    "re", "readline", "reprlib", "resource", "rlcompleter", "runpy", "sched",
    "secrets", "select", "selectors", "shelve", "shlex", "shutil", "signal",
    "site", "smtplib", "sndhdr", "socket", "socketserver", "spwd", "sqlite3",
    "sre", "sre_compile", "sre_constants", "sre_parse", "ssl", "stat", "statistics",
    "string", "stringprep", "struct", "subprocess", "sunau", "symbol", "symtable",
    "sys", "sysconfig", "syslog", "tarfile", "telnetlib", "tempfile", "termios",
    "test", "textwrap", "threading", "time", "timeit", "tkinter", "token",
    "tokenize", "trace", "traceback", "tracemalloc", "tty", "turtle", "turtledemo",
    "types", "typing", "typing_extensions", "unicodedata", "unittest", "urllib",
    "uu", "uuid", "venv", "warnings", "wave", "weakref", "webbrowser", "winreg",
    "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile", "zipimport",
    "zlib",
}


def get_imports_from_file(file_path: Path) -> Set[str]:
    """
    Extract all import statements from a Python file.
    
    Returns:
        Set of imported module names (top-level only, e.g., 'requests', not 'requests.get')
    """
    imports: Set[str] = set()
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse AST to get imports
        tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Get top-level module name
                    module_name = alias.name.split(".")[0]
                    imports.add(module_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Get top-level module name
                    module_name = node.module.split(".")[0]
                    imports.add(module_name)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"[WARNING] Could not parse {file_path}: {e}", file=sys.stderr)
    
    return imports


def scan_directory(directory: Path, project_root: Path) -> Dict[str, Set[Path]]:
    """
    Scan a directory for Python files and extract imports.
    
    Args:
        directory: Directory to scan
        project_root: Project root directory (for identifying local modules)
    
    Returns:
        Dictionary mapping module names to sets of files that import them
    """
    imports_map: Dict[str, Set[Path]] = defaultdict(set)
    
    # Identify local project modules (don't treat as third-party)
    local_modules = {
        "src",  # Local package
        "config",  # Local config module
        "scripts",  # Local scripts directory
        "tests",  # Local tests directory
    }
    
    # Also check for local script names (from scripts/ directory)
    scripts_dir = project_root / "scripts"
    if scripts_dir.exists():
        for script_file in scripts_dir.glob("*.py"):
            if script_file.name != "__init__.py":
                # Module name is filename without .py extension
                module_name = script_file.stem
                local_modules.add(module_name)
    
    # Find all Python files
    for py_file in directory.rglob("*.py"):
        # Skip test files and __pycache__
        if "__pycache__" in py_file.parts or ".pytest_cache" in py_file.parts:
            continue
        
        imports = get_imports_from_file(py_file)
        for module in imports:
            # Only track third-party modules (not stdlib, not local)
            if (
                module not in STDLIB_MODULES
                and module not in local_modules
                and not module.startswith("_")
            ):
                imports_map[module].add(py_file)
    
    return imports_map


def parse_requirements(requirements_file: Path) -> Set[str]:
    """
    Parse requirements.txt and extract package names.
    
    Handles:
    - Comments (lines starting with #)
    - Version constraints (package>=1.0.0)
    - Multiple formats
    """
    packages: Set[str] = set()
    
    if not requirements_file.exists():
        return packages
    
    with open(requirements_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # Extract package name (before any version constraint or comment)
            # Handles: package, package>=1.0.0, package==1.0.0, package~=1.0.0, etc.
            match = re.match(r"^([a-zA-Z0-9_-]+(?:\[[^\]]+\])?)", line)
            if match:
                package_name = match.group(1)
                # Remove extras markers like [dev] or [test]
                if "[" in package_name:
                    package_name = package_name.split("[")[0]
                packages.add(package_name.lower())
    
    return packages


def normalize_package_name(module_name: str) -> str:
    """
    Normalize module name to package name.
    
    Some modules have different names than their packages:
    - dotenv -> python-dotenv
    - PIL -> Pillow
    - yaml -> PyYAML
    """
    name_mapping = {
        "dotenv": "python-dotenv",
        "PIL": "Pillow",
        "yaml": "PyYAML",
        "dateutil": "python-dateutil",
    }
    
    return name_mapping.get(module_name, module_name.lower())


def main():
    """Main function to check dependencies."""
    project_root = Path(__file__).parent.parent
    
    print("=" * 70)
    print("Dependency Checker")
    print("=" * 70)
    print("\nScanning codebase for imports...\n")
    
    # Scan source code
    src_dir = project_root / "src"
    scripts_dir = project_root / "scripts"
    
    all_imports: Dict[str, Set[Path]] = {}
    
    if src_dir.exists():
        print(f"[*] Scanning {src_dir}...")
        src_imports = scan_directory(src_dir, project_root)
        all_imports.update(src_imports)
    
    if scripts_dir.exists():
        print(f"[*] Scanning {scripts_dir}...")
        scripts_imports = scan_directory(scripts_dir, project_root)
        all_imports.update(scripts_imports)
    
    # Get third-party packages
    third_party_modules = {
        module for module in all_imports.keys()
        if module not in STDLIB_MODULES
    }
    
    print(f"\n[OK] Found {len(third_party_modules)} third-party modules in use")
    
    # Parse requirements.txt
    requirements_file = project_root / "requirements.txt"
    requirements_packages = parse_requirements(requirements_file)
    
    print(f"[*] Found {len(requirements_packages)} packages in requirements.txt\n")
    
    # Compare
    missing_packages: Set[str] = set()
    unused_packages: Set[str] = set()
    
    # Normalize module names to package names
    module_to_package = {module: normalize_package_name(module) for module in third_party_modules}
    used_packages = set(module_to_package.values())
    
    # Find missing packages
    for module, package in module_to_package.items():
        if package not in requirements_packages:
            missing_packages.add((module, package))
    
    # Find unused packages (in requirements but not used)
    # Note: This is less reliable as packages might be used indirectly
    # Only check packages that are actually installed/active (not commented)
    for req_package in requirements_packages:
        # Check if any module maps to this package
        if req_package not in used_packages:
            # Skip type stubs (types-*) - these are for type checking only
            # Skip packages that might be dependencies of other packages
            if not req_package.startswith("types-"):
                # Check if it's a reverse mapping (package -> module)
                # Some packages have different module names
                reverse_mapping = {
                    "python-dotenv": "dotenv",
                    "Pillow": "PIL",
                    "PyYAML": "yaml",
                    "python-dateutil": "dateutil",
                }
                mapped_module = reverse_mapping.get(req_package)
                if mapped_module and mapped_module in third_party_modules:
                    # Package is used, just with different module name
                    continue
                unused_packages.add(req_package)
    
    # Report results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    if missing_packages:
        print(f"\n[!] MISSING DEPENDENCIES ({len(missing_packages)}):")
        print("-" * 70)
        for module, package in sorted(missing_packages):
            files = sorted(all_imports[module])
            print(f"  - {package} (imported as '{module}')")
            print(f"    Used in: {len(files)} file(s)")
            for file in files[:3]:  # Show first 3 files
                rel_path = file.relative_to(project_root)
                print(f"      - {rel_path}")
            if len(files) > 3:
                print(f"      ... and {len(files) - 3} more file(s)")
        print("\n[ACTION] Add these packages to requirements.txt")
    else:
        print("\n[OK] All used dependencies are in requirements.txt")
    
    if unused_packages:
        print(f"\n[?] POTENTIALLY UNUSED PACKAGES ({len(unused_packages)}):")
        print("-" * 70)
        print("  (These are in requirements.txt but not directly imported)")
        print("  (They might be used indirectly or are commented out)")
        for package in sorted(unused_packages):
            print(f"  - {package}")
        print("\n[ACTION] Review if these are needed")
    else:
        print("\n[OK] No obviously unused packages found")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Third-party modules used: {len(third_party_modules)}")
    print(f"Packages in requirements.txt: {len(requirements_packages)}")
    print(f"Missing packages: {len(missing_packages)}")
    print(f"Potentially unused packages: {len(unused_packages)}")
    
    if missing_packages:
        print("\n[!] requirements.txt is INCOMPLETE")
        return 1
    else:
        print("\n[OK] requirements.txt appears COMPLETE")
        return 0


if __name__ == "__main__":
    sys.exit(main())
