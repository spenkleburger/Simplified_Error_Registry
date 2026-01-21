# Git | Cursor Docs

Source URL: https://cursor.com/docs/integrations/git

---

Integrations
# Git

Cursor provides AI-powered Git features to streamline your workflow, including automatic commit message generation and intelligent merge conflict resolution.

## AI Commit Message

Cursor generates commit messages from staged changes.

Stage files to commit
Open the Git tab in the sidebar
Click the sparkle (✨) icon next to the commit message input

Generated messages use staged changes and repository git history. If you use conventions like [Conventional Commits](https://www.conventionalcommits.org/), messages follow the same pattern.

### Add shortcut

To bind to a keyboard shortcut:

Go to Keyboard Shortcuts (Cmd+R Cmd+SCtrl+R Ctrl+S or Cmd+Shift+PCtrl+Shift+P and search "Open Keyboard Shortcuts (JSON)")

Add this binding for Cmd+MCtrl+M:

```
{
  "key": "cmd+m",
  "command": "cursor.generateGitCommitMessage"
}
```

Save

You cannot customize commit message generation. Cursor adapts to your existing
commit style.

## AI Resolve Conflicts

When merge conflicts occur, Cursor Agent can help resolve them by understanding both sides of the conflict and proposing a resolution.

### How to use

When a merge conflict occurs, you'll see the conflict markers in your file
Click the Resolve in Chat button that appears in the merge conflict UI
Agent will analyze both versions and suggest a resolution
Review the proposed changes and apply them