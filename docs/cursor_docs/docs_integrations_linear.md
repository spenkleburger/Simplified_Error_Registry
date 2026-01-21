# Linear | Cursor Docs

Source URL: https://cursor.com/docs/integrations/linear

---

Integrations
# Linear

Use [Cloud Agents](/docs/cloud-agent) directly from Linear by delegating issues to Cursor or mentioning `@Cursor` in comments.

## Get started

### Installation

You must be a Cursor admin to connect the Linear integration. Other team
settings are available to non-admin members.

Go to [Cursor integrations](https://www.cursor.com/dashboard?tab=integrations)
Click Connect next to Linear
Connect your Linear workspace and select team
Click Authorize
Complete any remaining Cloud Agent setup in Cursor:

Connect GitHub and select default repository
Enable usage-based pricing
Confirm privacy settings

### Account linking

First use prompts account linking between Cursor and Linear. GitHub connection required for PR creation.

## How to use

Delegate issues to Cursor or mention `@Cursor` in comments. Cursor analyzes issues and filters out non-development work automatically.

### Delegating issues

Open Linear issue
Click assignee field
Select "Cursor"

### Mentioning Cursor

Mention `@Cursor` in a comment to assign a new agent or provide additional instructions, for example: `@Cursor fix the authentication bug described above`.

## Workflow

Cloud Agents show real-time status in Linear and create PRs automatically when complete. Track progress in [Cursor dashboard](https://www.cursor.com/dashboard?tab=cloud-agents).

### Follow-up instructions

You can respond in the agent session and it'll get sent as a follow-up to the agent. Simply mention `@Cursor` in a Linear comment to provide additional guidance to a running Cloud Agent.

## Configuration

Configure Cloud Agent settings from [Dashboard → Cloud Agents](https://www.cursor.com/dashboard?tab=cloud-agents).

SettingLocationDescriptionDefault RepositoryCursor DashboardPrimary repository when no project repository configuredDefault ModelCursor DashboardAI model for Cloud AgentsBase BranchCursor DashboardBranch to create PRs from (typically `main` or `develop`)

### Configuration options

You can configure Cloud Agent behavior using several methods:

Issue description or comments: Use `[key=value]` syntax, for example:

`@cursor please fix [repo=anysphere/everysphere]`
`@cursor implement feature [model=claude-3.5-sonnet] [branch=feature-branch]`

Issue labels: Use parent-child label structure where the parent label is the configuration key and the child label is the value.

Project labels: Same parent-child structure as issue labels, applied at the project level.

Supported configuration keys:

`repo`: Specify target repository (e.g., `owner/repository`)
`branch`: Specify base branch for PR creation
`model`: Specify AI model to use

### Repository selection

Cursor determines which repository to work on using this priority order:

Issue description/comments: `[repo=owner/repository]` syntax in issue text or comments
Issue labels: Repository labels attached to the specific Linear issue
Project labels: Repository labels attached to the Linear project
Default repository: Repository specified in Cursor dashboard settings

#### Setting up repository labels

To create repository labels in Linear:

Go to Settings in your Linear workspace
Click Labels
Click New group
Name the group "repo" (case insensitive - must be exactly "repo", not "Repository" or other variations)
Within that group, create labels for each repository using the format `owner/repo`

These labels can then be assigned to issues or projects to specify which repository the Cloud Agent should work on.

## Advanced features

### Triage rules (Advanced)

Set up automation rules in Linear to automatically delegate issues to Cursor:

Go to Linear project settings
Navigate to triage rules
Create rules that automatically:

Add specific labels
Assign issues to Cursor
Trigger Cloud Agents based on conditions

Triage rules are an advanced feature with some current limitations. Linear
requires a human assignee for rules to fire, though this requirement may be
removed in future updates.

### Getting help

Check [agent activity](https://www.cursor.com/dashboard?tab=cloud-agents) and include request IDs when contacting support.

## Feedback

Share feedback through Linear comments or your Cursor dashboard support channels.