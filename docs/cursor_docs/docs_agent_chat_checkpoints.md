# Checkpoints | Cursor Docs

Source URL: https://cursor.com/docs/agent/chat/checkpoints

---

Core
# Checkpoints

Checkpoints are automatic snapshots of Agent's changes to your codebase. They let you undo Agent modifications if needed.

## Restoring checkpoints

Two ways to restore:

From input box: Click `Restore Checkpoint` button on previous requests
From message: Click the + button when hovering over a message

Checkpoints are not version control. Use Git for permanent history.

## How they work

Stored locally, separate from Git
Track only Agent changes (not manual edits)
Cleaned up automatically

Manual edits aren't tracked. Only use checkpoints for Agent changes.

## FAQ

### Do checkpoints affect Git?

### How long are they kept?

### Can I create them manually?