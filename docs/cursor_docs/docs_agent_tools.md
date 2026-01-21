# Tools | Cursor Docs

Source URL: https://cursor.com/docs/agent/tools

---

Core
# Tools

A list of all tools available to modes within the [Agent](/docs/agent/overview).

To understand how tool calling works under the hood, see our [tool calling fundamentals](/learn/tool-calling).

There is no limit on the number of tool calls Agent can make during a task.
Agent will continue using tools as needed to complete your request.

## Search

Tools used to search your codebase and the web to find relevant information.

### Read File

### List Directory

### Codebase

### Grep

### Search Files

### Web

### Fetch Rules

## Edit

Tools used to make specific edits to your files and codebase.

### Edit & Reapply

### Delete File

## Run

Chat can interact with your terminal.

### Terminal

By default, Cursor uses the first terminal profile available.

To set your preferred terminal profile:

Open Command Palette (`Cmd/Ctrl+Shift+P`)
Search for "Terminal: Select Default Profile"
Choose your desired profile

## MCP

Chat can use configured MCP servers to interact with external services, such as databases or 3rd party APIs.

### Toggle MCP Servers

Learn more about [Model Context Protocol](/docs/context/mcp) and explore available servers in the [MCP directory](/docs/context/mcp/directory).

## Advanced options

### Auto-apply Edits

### Auto-run

### Guardrails

### Auto-fix Errors