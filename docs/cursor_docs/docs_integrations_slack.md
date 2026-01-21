# Slack | Cursor Docs

Source URL: https://cursor.com/docs/integrations/slack

---

Integrations
# Slack

With Cursor's integration for Slack, you can use [Cloud Agents](/docs/cloud-agent) to work on your tasks directly from Slack by mentioning `@cursor` with a prompt.

## Get started

### Installation

Go to [Cursor integrations](https://www.cursor.com/dashboard?tab=integrations)

Click Connect next to Slack or go to [installation page](https://cursor.com/api/install-slack-app) from here

You'll be prompted to install the Cursor app for Slack in your workspace.

After installing in Slack, you'll be redirected back to Cursor to finalize setup

Connect GitHub (if not already connected) and pick a default repository
Enable usage-based pricing
Confirm privacy settings

Start using Cloud Agents in Slack by mentioning `@cursor`

## How to use

Mention `@cursor` and give your prompt. This handles most use cases, but you can also use commands below to customize your agent.

For example, mention `@Cursor fix the login bug` directly in conversation, or use specific commands like `@Cursor [repo=torvalds/linux] fix bug` to target a particular repository.

### Commands

Run `@Cursor help` for an up-to-date command list.

CommandDescription`@Cursor [prompt]`Start a Cloud Agent. In threads with existing agents, adds followup instructions`@Cursor settings`Configure defaults and channel's default repository`@Cursor [options] [prompt]`Use advanced options: `branch`, `model`, `repo``@Cursor agent [prompt]`Force create a new agent in a thread`@Cursor list my agents`Show your running agents

#### Options

Customize Cloud Agent behavior with these options:

OptionDescriptionExample`branch`Specify base branch`branch=main``model`Choose AI model`model=o3``repo`Target specific repository`repo=owner/repo``autopr`Enable/disable automatic PR creation`autopr=false`

#### Syntax Formats

Brackets:

```
@Cursor [branch=dev, model=o3, repo=owner/repo, autopr=false] Fix the login bug
```

Inline:

```
@Cursor branch=dev model=o3 repo=owner/repo autopr=false Fix the login bug
```

#### Option precedence

When combining options:

Explicit values override defaults
Later values override earlier ones if duplicated
Inline options take precedence over settings modal defaults

The bot parses options from anywhere in the message, allowing natural command writing.

#### Using thread context

Cloud Agents understand and use context from existing thread discussions. Useful when your team discusses an issue and you want the agent to implement the solution based on that conversation.

Cloud Agents read the entire thread for context when invoked,
understanding and implementing solutions based on the team's discussion.

#### When to use force commands

When do I need `@Cursor agent`?

In threads with existing agents, `@Cursor [prompt]` adds followup instructions (only works if you own the agent). Use `@Cursor agent [prompt]` to launch a separate agent.

When do I need `Add follow-up` (from context menu)?

Use the context menu (⋯) on an agent's response for followup instructions. Useful when multiple agents exist in a thread and you need to specify which one to follow up on.

### Status updates & handoff

When Cloud Agent runs, you first get an option to Open in Cursor.

When Cloud Agent completes, you get a notification in Slack and an option to view the created PR in GitHub.

### Managing agents

To see all running agents, run `@Cursor list my agents`.

Manage Cloud Agents using the context menu by clicking the three dots (⋯) on any agent message.

Available options:

Add follow-up: Add instructions to an existing agent
Delete: Stop and archive the Cloud Agent
View request ID: View unique request ID for troubleshooting (include when contacting support)
Give feedback: Provide feedback about agent performance

## Configuration

Manage default settings and privacy options from [Dashboard → Cloud Agents](https://www.cursor.com/dashboard?tab=cloud-agents).

### Settings

#### Default Model

Used when no model is explicitly specified with `@Cursor [model=...]`. See [settings](https://www.cursor.com/dashboard?tab=cloud-agents) for available options.

#### Default Repository

Used when no repository is specified. Use these formats:

`https://github.com/org/repository`
`org/repository`

If you reference a non-existent repository, it appears as if you don't have
access. This shows in the error message when Cloud Agent fails to start.

#### Base Branch

Starting branch for Cloud Agent. Leave blank to use the repository's default branch (often `main`)

### Channel Settings

Configure default settings at the channel level using `@Cursor settings`. These settings are per team and override your personal defaults for that channel.

Particularly useful when:

Different channels work on different repositories
Teams want consistent settings across all members
You want to avoid specifying the repository in every command

To configure channel settings:

Run `@Cursor settings` in the desired channel
Set the default repository for that channel
All team members using Cloud Agents in that channel use these defaults

Channel settings take precedence over personal defaults but can be overridden
by explicit options like `@Cursor [repo=...] [prompt]`

### Privacy

Cloud Agents support Privacy Mode.

Read more about [Privacy Mode](https://www.cursor.com/privacy-overview) or manage your [privacy settings](https://www.cursor.com/dashboard?tab=cloud-agents).

Privacy Mode (Legacy) is not supported. Cloud Agents require temporary
code storage while running.

#### Display Agent Summary

Display agent summaries and diff images. May contain file paths or code snippets. Can be turned On/Off.

#### Display Agent Summary in External Channels

For Slack Connect with other workspaces or channels with external members like Guests, choose to display agent summaries in external channels.

## Permissions

Cursor requests these Slack permissions for Cloud Agents to work within your workspace:

PermissionDescription`app_mentions:read`Detects @mentions to start Cloud Agents and respond to requests`channels:history`Reads previous messages in threads for context when adding follow-up instructions`channels:join`Automatically joins public channels when invited or requested`channels:read`Accesses channel metadata (IDs and names) to post replies and updates`chat:write`Sends status updates, completion notifications, and PR links when agents finish`files:read`Downloads shared files (logs, screenshots, code samples) for additional context`files:write`Uploads visual summaries of agent changes for quick review`groups:history`Reads previous messages in private channels for context in multi-turn conversations`groups:read`Accesses private channel metadata to post responses and maintain conversation flow`im:history`Accesses direct message history for context in continued conversations`im:read`Reads DM metadata to identify participants and maintain proper threading`im:write`Initiates direct messages for private notifications or individual communication`mpim:history`Accesses group DM history for multi-participant conversations`mpim:read`Reads group DM metadata to address participants and ensure proper delivery`reactions:read`Observes emoji reactions for user feedback and status signals`reactions:write`Adds emoji reactions to mark status - ⏳ for running, ✅ for completed, ❌ for failed`team:read`Identifies workspace details to separate installations and apply settings`users:read`Matches Slack users with Cursor accounts for permissions and secure access