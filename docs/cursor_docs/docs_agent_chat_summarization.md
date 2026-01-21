# Summarization | Cursor Docs

Source URL: https://cursor.com/docs/agent/chat/summarization

---

Core
# Summarization

## Message summarization

As conversations grow longer, Cursor automatically summarizes and manages context to keep your chats efficient. Learn how to use the context menu and understand how files are condensed to fit within model context windows.

### Using the /summarize command

You can manually trigger summarization using the `/summarize` command in chat. This command helps manage context when conversations become too long, allowing you to continue working efficiently without losing important information.

New to Cursor? Learn more about [Context](/learn/context).

### How summarization works

When conversations grow longer, they exceed the model's context window limit:

UserCursorUserContext window limitCursorUserCursor

To solve this, Cursor summarizes older messages to make room for new conversations.

Context window limit

Summarized Messages
CursorUserCursor

## File & folder condensation

While chat summarization handles long conversations, Cursor uses a different strategy for managing large files and folders: smart condensation. When you include files in your conversation, Cursor determines the best way to present them based on their size and available context space.

Here are the different states a file/folder can be in:

### Condensed

When files or folders are too large to fit within the context window, Cursor automatically condenses them. Condensing shows the model key structural elements like function signatures, classes, and methods. From this condensed view, the model can choose to expand specific files if needed. This approach maximizes effective use of the available context window.

### Significantly condensed

When a file name appears with a "Significantly Condensed" label, the file was too large to include in full, even in condensed form. Only the file name will be shown to the model.

### Not included

When a warning icon appears next to a file or folder, the item is too large to be included in the context window, even in condensed form. This helps you understand which parts of your codebase are accessible to the model.