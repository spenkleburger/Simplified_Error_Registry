# Model and Integration Management | Cursor Docs

Source URL: https://cursor.com/docs/enterprise/model-and-integration-management

---

Account
# Model and Integration Management

Your team can access multiple AI models and integrate Cursor with various services. This documentation covers how to control which models are available, manage MCP server trust, and set up integrations with tools like Slack, GitHub, and Linear.

## Model access control

Enterprise teams can control which AI models team members can use. This helps manage costs, ensure appropriate usage, and comply with organizational policies.

Model access controls are configured through the [team dashboard](/docs/account/teams/dashboard). Navigate to Settings and look for "Model Access Control" (Enterprise only).

### How enterprise model rollout works

When new models become available, Cursor doesn't immediately enable them for all enterprise teams.

Instead, Enterprise teams can opt in to new models for their organization.

See [Models](/docs/models) for the current list of available models.

## MCP server trust management

The Model Context Protocol (MCP) lets you connect external tools and data sources to Cursor. MCP servers can:

Read files from external systems
Execute operations on your behalf
Access databases and APIs
Integrate with third-party services

MCP servers are designed and implemented by external vendors, not Cursor. We work with partners to provide a [vetted directory](https://cursor.com/docs/context/mcp/directory) of trusted servers, but you should review each server's capabilities and permissions before enabling it for your team.

Because MCP servers have significant capabilities, you need to manage which servers your team can use.

### Allowlist and blocklist

Enterprise teams can control MCP server access through allowlists and blocklists:

Set this in the [team dashboard](/docs/account/teams/dashboard) under "MCP Configuration" (Enterprise only).

See [MCP](/docs/context/mcp) for details on MCP servers and configuration.

## Git repository blocklist

You can prevent Cursor from accessing specific repositories.

Add repository URLs or patterns in the [team dashboard](/docs/account/teams/dashboard) under "Repository Blocklist" (Enterprise only). Cursor will refuse to index or work with blocked repositories.

## Integration: Slack

The Slack integration enables Cloud Agents to run directly from Slack. Team members can mention `@cursor` with a prompt and get automated code changes delivered as pull requests.

Cursor requires permissions to read messages, post responses, and access channel metadata. See the [Slack integration documentation](/docs/integrations/slack#permissions) for the full list.

See [Slack integration](/docs/integrations/slack) for detailed setup and usage instructions.

## Integration: GitHub, GHES, and GitLab

Connect Cursor to your version control system to work with Cloud Agents.

Cursor requires read access to repositories and write access to create PRs. You control which repositories the Cursor app can access.

See [GitHub integration](/docs/integrations/github) for setup.

## Integration: Linear

Connect Linear to start Cloud Agents from issues.

Cursor requires read access to issues and write access to update issue status.

See [Linear integration](/docs/integrations/linear) for details.