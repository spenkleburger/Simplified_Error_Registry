# @ Symbols | Cursor Docs

Source URL: https://cursor.com/docs/context/symbols

---

Context
# @ Symbols

Navigate suggestions using arrow keys. Press `Enter` to select. If the suggestion is a category like `Files`, the suggestions filter to show the most relevant items within that category.

## @Files & Folders

### Referencing Files

Reference entire files in by selecting `@Files & Folders` followed by the filename to search. You can also drag files from the sidebar directly into Agent to add as context.

### Referencing Folders

When referencing folders using `@Folders`, Cursor provides the folder path and overview of its contents to help the AI understand what's available.

After selecting a folder, type `/` to navigate deeper and see all subfolders.

### Context management

Large files and folders are automatically condensed to fit within context limits. See [file & folder condensation](/docs/agent/chat/summarization#file--folder-condensation) for details.

## @Code

Reference specific code sections using the `@Code` symbol. This provides more granular control than `@Files & Folders`, letting you select precise code snippets instead of entire files.

## @Docs

The `@Docs` feature lets you use documentation to help write code. Cursor includes popular documentation and you can add your own.

### Using existing documentation

Type `@Docs` in chat to see available documentation. Browse and select from popular frameworks and libraries.

### Adding your own documentation

To add documentation not already available:

Type `@Docs` and select Add new doc
Paste the URL of the documentation site

Once added, Cursor reads and understands the documentation, including all subpages. Use it like any other documentation.

Turn on Share with team to make documentation available to everyone on your team.

### Managing your documentation

Go to Cursor Settings > Indexing & Docs to see all your added documentation. From here:

Edit documentation URLs
Remove documentation you no longer need
Add new documentation

## Built-in commands

Summarize: Compress the context window and provide a summary of the conversation.

You can also define [custom commands](/docs/agent/chat/commands) to use in the chat.

## Changelog

Cursor 2.0 includes improvements and some deprecations for context and @ symbols.

We've visually removed the top tray of the prompt input showing included context. However, the agent still sees the same context as before. Files and directories are now shown inline as pills. We've also improved copy/pasting prompts with tagged context.
We've removed explicit items in the context menu, including `@Definitions`, `@Web`, `@Link`, `@Recent Changes`, `@Linter Errors`, and others. Agent can now self-gather context without needing to manually attach it in the prompt input. For example, rather than using `@Git`, you can now ask the agent directly to review changes on your branch, or specific commits.
Notepads have been [deprecated](https://forum.cursor.com/t/deprecating-notepads-in-cursor/138305/5).
Applied rules are now shown by hovering the context gauge in the prompt input.