# Inline Edit | Cursor Docs

Source URL: https://cursor.com/docs/inline-edit/overview

---

Core
# Inline Edit

Inline Edit lets you edit code or ask questions directly in your editor with Cmd+KCtrl+K, which opens an input field where your selected code and instructions create your request.

## Modes

### Edit Selection

With code selected, Cmd+KCtrl+K edits that specific code based on your instructions.

Without selection, Cursor generates new code at your cursor position. The AI includes relevant surrounding code for context. For example, triggering on a function name includes the entire function.

### Quick Question

Press Opt+ReturnAlt+Enter in the inline editor to ask questions about selected code.

After getting an answer, type "do it" or similar wording to convert the suggestion into code. This lets you explore ideas before implementing.

### Full File Edits

For file-wide changes, use Cmd+Shift+ReturnCtrl+Shift+Enter. This mode enables comprehensive changes while maintaining control.

### Send to Chat

For multi-file edits or advanced features, use Cmd+LCtrl+L to send selected code to [Chat](/docs/agent/modes#agent). This provides multi-file editing, detailed explanations, and advanced AI capabilities.

## Follow-up instructions

After each edit, refine results by adding instructions and pressing ReturnEnter. The AI updates changes based on your feedback.

## Default context

Inline Edit includes default context to improve code generation beyond any [@ symbols](/docs/context/symbols/files-and-folders) you add.

This includes related files, recently viewed code, and relevant information. Cursor prioritizes the most relevant context for better results.