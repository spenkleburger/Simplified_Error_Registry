# Ignore files | Cursor Docs

Source URL: https://cursor.com/docs/context/ignore-files

---

Context
# Ignore files

## Overview

Cursor reads and indexes your project's codebase to power its features. Control which directories and files Cursor can access using a `.cursorignore` file in your root directory.

Cursor blocks access to files listed in `.cursorignore` from:

Codebase indexing
Code accessible by [Tab](/docs/tab/overview), [Agent](/docs/agent/overview), and [Inline Edit](/docs/inline-edit/overview)
Code accessible via [@ symbol references](/docs/context/symbols/overview)

The terminal and MCP server tools used by Agent cannot block access to code
governed by `.cursorignore`

## Why ignore files?

Security: Restrict access to API keys, credentials, and secrets. While Cursor blocks ignored files, complete protection isn't guaranteed due to LLM unpredictability.

Performance: In large codebases or monorepos, exclude irrelevant portions for faster indexing and more accurate file discovery.

## Global ignore files

Set ignore patterns for all projects in user settings to exclude sensitive files without per-project configuration.

Default patterns include:

Environment files: `**/.env`, `**/.env.*`
Credentials: `**/credentials.json`, `**/secrets.json`
Keys: `**/*.key`, `**/*.pem`, `**/id_rsa`

## Configuring .cursorignore

Create a `.cursorignore` file in your root directory using `.gitignore` syntax.

### Pattern examples

```
config.json      # Specific file
dist/           # Directory
*.log           # File extension
**/logs         # Nested directories
!app/           # Exclude from ignore (negate)
```

### Hierarchical ignore

Enable `Cursor Settings` > `Features` > `Editor` > `Hierarchical Cursor Ignore` to search parent directories for `.cursorignore` files.

Notes: Comments start with `#`. Later patterns override earlier ones. Patterns are relative to file location.

## Limit indexing with .cursorindexingignore

Use `.cursorindexingignore` to exclude files from indexing only. These files remain accessible to AI features but won't appear in codebase searches.

## Files ignored by default

Cursor automatically ignores files in `.gitignore` and the default ignore list below. Override with `!` prefix in `.cursorignore`.

### Default Ignore List

### Negation pattern limitations

When using negation patterns (prefixed with `!`), you cannot re-include a file if a parent directory is excluded via *.

```
# Ignore all files in public folder
public/*

# ✅ This works, as the file exists at the top level
!public/index.html

# ❌ This doesn't work - cannot re-include files from nested directories
!public/assets/style.css
```

Workaround: Explicitly exclude nested directories:

```
public/assets/*
!public/assets/style.css # This file is now accessible
```

Excluded directories are not traversed for performance, so patterns on contained files have no effect.
This matches the .gitignore implementation for negation patterns in nested directories. For more details, see the [official Git documentation on gitignore patterns](https://git-scm.com/docs/gitignore).

## Troubleshooting

Test patterns with `git check-ignore -v [file]`.