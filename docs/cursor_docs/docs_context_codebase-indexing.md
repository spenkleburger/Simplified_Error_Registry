# Codebase Indexing | Cursor Docs

Source URL: https://cursor.com/docs/context/codebase-indexing

---

Context
# Codebase Indexing

Codebase indexing enables semantic search across your local workspace files, building a searchable index for natural language queries to find relevant code across your entire codebase.

## How it works

Cursor transforms your code into searchable vectors through a 7-step process:

Your workspace files are securely synchronized with Cursor's servers to keep the index current and up-to-date.

Files are broken down into meaningful chunks that capture the essence of your code—functions, classes, and logical code blocks rather than arbitrary text segments.

Each chunk is converted into a vector representation using AI models. This creates a mathematical fingerprint that captures the semantic meaning of your code.

These embeddings are stored in a specialized vector database optimized for fast similarity search across millions of code chunks.

When you search, your query is converted into a vector using the same AI models that processed your code.

The system finds the most similar code chunks by comparing your query's vector against stored embeddings.

You get relevant code snippets with file locations and context, ranked by semantic similarity to your search.

Your workspace

File sync

Chunking

AI embeddings

Vector database

Your search query

Query embedding

Search results

## Privacy and security

### Data protection

Your code's privacy is protected through multiple layers of security. File paths are encrypted before being sent to our servers, ensuring your project structure remains confidential. Your actual code content is never stored in plaintext on our servers, maintaining the confidentiality of your intellectual property. Code is only held in memory during the indexing process, then discarded, so there's no permanent storage of your source code.

## Getting started

### First-time indexing

Indexing begins automatically when you open a workspace. The system scans your workspace structure, uploads files securely, and processes them through AI models to create embeddings. Semantic search becomes available at 80% completion.

## Keeping your index updated

### Automatic sync

Cursor automatically keeps your index synchronized with your workspace through periodic checks every 5 minutes. The system intelligently updates only changed files, removing old embeddings and creating new ones as needed. Files are processed in batches for optimal performance, ensuring minimal impact on your development workflow.

### What gets indexed

File TypeActionNew filesAutomatically added to indexModified filesOld embeddings removed, fresh ones createdDeleted filesPromptly removed from indexLarge/complex filesMay be skipped for performance

### Performance and troubleshooting

Performance: Uses intelligent batching and caching for accurate, up-to-date results.

Troubleshooting steps:

Check internet connection
Verify workspace permissions
Restart Cursor
Contact support if issues persist

The indexing system works reliably in the background to keep your code searchable.

## Why semantic search?

While tools like `grep` and `ripgrep` are useful for finding exact string matches, semantic search goes further by understanding the meaning behind your code.

If you ask Agent to "update the top navigation", semantic search can find `header.tsx` even though the word "navigation" doesn't appear in the filename. This works because the embeddings understand that "header" and "top navigation" are semantically related.

### Benefits over grep alone

Semantic search provides several advantages:

Faster results: Compute happens during indexing (offline) rather than at runtime, so Agent searches are faster and cheaper
Better accuracy: Custom-trained models retrieve more relevant results than string matching
Fewer follow-ups: Users send fewer clarifying messages and use fewer tokens compared to grep-only search
Conceptual matching: Find code by what it does, not just what it's named

Agent uses both grep and semantic search together. Grep excels at finding
exact patterns, while semantic search excels at finding conceptually similar
code. This combination delivers the best results.

## Configuration

Cursor indexes all files except those in [ignore files](/docs/context/ignore-files) (e.g. `.gitignore`, `.cursorignore`).

Click `Show Settings` to:

Enable automatic indexing for new repositories
Configure which files to ignore

[Ignoring large content files](/docs/context/ignore-files) improves answer
accuracy.

### View indexed files

To see indexed file paths: `Cursor Settings` > `Indexing & Docs` > `View included files`

This opens a `.txt` file listing all indexed files.

## FAQ

### Where can I see all indexed codebases?

### How do I delete all indexed codebases?

### How long are indexed codebases retained?

### Is my source code stored on Cursor servers?

### Can I customize path encryption?

### How does team sharing work?

### What is smart index copying?

### Does Cursor support multi-root workspaces?