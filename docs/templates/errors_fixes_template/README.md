# Simplified Error Registry - Quick Reference

This folder contains the Simplified Error Registry (SER) system for tracking and consolidating errors and fixes across development sessions.

## Files

### `errors_and_fixes.md`
- **Purpose**: Session log of errors and fixes during active development
- **Lifecycle**: Ephemeral - contents cleared after daily consolidation (file is kept)
- **When to use**: Agent documents errors and fixes here during development sessions
- **Entry Types**:
  - `### Error:` - Application/test code errors → consolidated to `fix_repo.md`
  - `### Agent Process Issue:` - Agent behavior/workflow issues → consolidated to `coding_tips.md`

### `fix_repo.md`
- **Purpose**: Consolidated solutions to errors in application and test code
- **Lifecycle**: Read-only during development, updated daily by consolidation app
- **When to use**: **Reactive** - when you have a runtime or test error, look here for fixes
- **Contains**: Error signatures → fixes ordered by success count, with tags and metadata

### `coding_tips.md`
- **Purpose**: Agent process and workflow rules
- **Lifecycle**: Read-only during development, updated by consolidation app when process issues detected
- **When to use**: **Proactive** - check before and during coding to avoid mistakes
- **Contains**: Rules, do's/don'ts, examples for agent behavior (paths, commands, Docker, conventions)

## Lookup Order

When an error occurs, check in this order:

1. **First**: Check `errors_and_fixes.md` for recent session attempts
2. **Second**: Check `fix_repo.md` for consolidated code fixes (try fixes in order of success count)
3. **Third**: Check `coding_tips.md` for agent process rules (check proactively before coding)

## Consolidation

The consolidation app runs daily at 2 AM to:
- Consolidate `### Error:` entries → `fix_repo.md`
- Consolidate `### Agent Process Issue:` entries → `coding_tips.md`
- Clear contents of `errors_and_fixes.md` (file is kept for next session)

## Format

All files use:
- UTF-8 encoding
- LF line endings
- Markdown format (parseable by regex v1, future markdown parser)

## Quick Start

1. Bootstrap this folder in your project using: `python scripts/bootstrap_errors_fixes.py /path/to/project`
2. Agent will automatically document errors and fixes in `errors_and_fixes.md`
3. Check `fix_repo.md` when you have errors to fix
4. Check `coding_tips.md` proactively before coding

---

For detailed documentation, see `docs/SIMPLIFIED_ERROR_REGISTRY_V2.md`
