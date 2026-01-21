# MCP Install Links | Cursor Docs

Source URL: https://cursor.com/docs/context/mcp/install-links

---

Context
# MCP Install Links

MCP servers can be installed with Cursor deeplinks. It uses the same format as [mcp.json](/docs/context/mcp) with a name and transport configuration.

Install links:

```
cursor://anysphere.cursor-deeplink/mcp/install?name=$NAME&config=$BASE64_ENCODED_CONFIG
```

ComponentDescription`cursor://`Protocol scheme`anysphere.cursor-deeplink`Deeplink handler`/mcp/install`Path`name`Query parameter for server name`config`Query parameter for base64 encoded JSON configuration

## Generate install link

Get name and JSON configuration of server
`JSON.stringify` the configuration then base64 encode it
Replace `$NAME` and `$BASE64_ENCODED_CONFIG` with the name and encoded config

Helper for generating links:

MCP server JSON configuration{
  "postgres": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-postgres",
      "postgresql://localhost/mydb"
    ]
  }
}No server detectedCopy deeplinkCopy web linkMarkdownHTMLJSX
Click to copy. Paste in README

## Example

Try this JSON in the MCP install link generator:

Single MCP server config
```
{
  "postgres": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-postgres",
      "postgresql://localhost/mydb"
    ]
  }
}
```

Result:

FormatExampleText link[cursor://anysphere.curs...](cursor://anysphere.cursor-deeplink/mcp/install?name=postgres&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkBtb2RlbGNvbnRleHRwcm90b2NvbC9zZXJ2ZXItcG9zdGdyZXMiLCJwb3N0Z3Jlc3FsOi8vbG9jYWxob3N0L215ZGIiXX0=)Dark button[](cursor://anysphere.cursor-deeplink/mcp/install?name=postgres&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkBtb2RlbGNvbnRleHRwcm90b2NvbC9zZXJ2ZXItcG9zdGdyZXMiLCJwb3N0Z3Jlc3FsOi8vbG9jYWxob3N0L215ZGIiXX0=)Light button[](cursor://anysphere.cursor-deeplink/mcp/install?name=postgres&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkBtb2RlbGNvbnRleHRwcm90b2NvbC9zZXJ2ZXItcG9zdGdyZXMiLCJwb3N0Z3Jlc3FsOi8vbG9jYWxob3N0L215ZGIiXX0=)

## Install server

Click the link or paste into browser
Cursor prompts to install the server
Use the server in Cursor