# Shell Commands | Cursor Docs

Source URL: https://cursor.com/docs/configuration/shell

---

Configuration
# Shell Commands

Cursor provides command-line tools to open files and folders from your terminal. Install both the `cursor` and `code` commands to integrate Cursor with your development workflow.

## Installing CLI commands

Install the CLI commands through the Command Palette:

Open the Command Palette (Cmd/Ctrl + P)
Type "Install" to filter installation commands
Select and run `Install 'cursor' to shell`
Repeat and select `Install 'code' to shell`

## Using the CLI commands

After installation, use either command to open files or folders in Cursor:

```
# Using the cursor command
cursor path/to/file.js
cursor path/to/folder/

# Using the code command (VS Code compatible)
code path/to/file.js
code path/to/folder/
```

## Command options

Both commands support these options:

Open a file: `cursor file.js`
Open a folder: `cursor ./my-project`
Open multiple items: `cursor file1.js file2.js folder1/`
Open in a new window: `cursor -n` or `cursor --new-window`
Wait for the window to close: `cursor -w` or `cursor --wait`

## FAQ

### What's the difference between cursor and code commands?

### Do I need to install both commands?

### Where are the commands installed?