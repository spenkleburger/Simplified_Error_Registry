# Tab | Cursor Docs

Source URL: https://cursor.com/docs/tab/overview

---

Core
# Tab

Tab is a specialized Cursor model for autocompletion. The more you use it, the better it becomes as you inject intent by accepting Tab or rejecting EscapeEsc suggestions. With Tab, you can:

Modify multiple lines at once
Add import statements when missing
Jump within and across files for coordinated edits
Get suggestions based on recent changes, linter errors and accepted edits

## Suggestions

When adding text, completions appear as semi-opaque ghost text. When modifying existing code, it shows as a diff popup right of your current line.

Accept suggestions with Tab, reject with EscapeEsc, or accept word-by-word using Cmd+Arrow RightCtrl+Arrow Right. Keep typing or press EscapeEsc to hide suggestions.

### Jump in file

Tab predicts your next editing location in the file and suggests jumps. After accepting an edit, press Tab again to jump to the next location.

### Jump across files

Tab predicts context-aware edits across files. A portal window appears at the bottom when a cross-file jump is suggested.

### Auto-import

In TypeScript and Python, Tab automatically adds import statements when missing. Use a method from another file and Tab suggests the import. Accepting adds it without disrupting your flow.

If auto-import isn't working:

Ensure your project has the right language server or extensions
Test with Cmd .Ctrl . to check if the import appears in Quick Fix suggestions

### Tab in Peek

Tab works in Go to Definition or Go to Type Definition peek views. Useful for modifying function signatures and fixing call sites.

In Vim, use with `gd` to jump to definitions, modify, and resolve references in one flow.

### Partial Accepts

Accept one word at a time with Cmd RightCtrl Right, or set your keybinding via `editor.action.inlineSuggest.acceptNextWord`. Enable in: `Cursor Settings` → `Tab`.

## Settings

SettingDescriptionCursor TabContext-aware, multi-line suggestions around your cursor based on recent editsPartial AcceptsAccept the next word of a suggestion via Cmd RightCtrl RightSuggestions While CommentingEnable Tab inside comment blocksWhitespace-Only SuggestionsAllow edits affecting only formattingImportsEnable auto-import for TypeScriptAuto Import for Python (beta)Enable auto-import for Python projects

### Toggling

Use the status bar (bottom-right) to:

Snooze: Temporarily disable Tab for a chosen duration
Disable globally: Disable Tab for all files
Disable for extensions: Disable Tab for specific file extensions (e.g., markdown or JSON)

## FAQ

### Tab gets in the way when writing comments, what can I do?

### Can I change the keyboard shortcut for Tab suggestions?

### How does Tab generate suggestions?