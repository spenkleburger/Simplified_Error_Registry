# Cloud Agents | Cursor Docs

Source URL: https://cursor.com/docs/cloud-agent

---

Core
# Cloud Agents

With cloud agents, spawn asynchronous agents that edit and run code in a remote environment. View their status, send follow-ups, or take over anytime.

Cloud agents leverage the same [agent fundamentals](/learn/agents) but run autonomously in isolated environments.

## How to Use

You can access cloud agents in two ways:

Cloud Agent Sidebar: Use the cloud agent tab in the native Cursor sidebar to view all cloud agents associated with your account, search existing agents, and start new ones.
Cloud Agent Mode: Hit Cmd ECtrl E to trigger cloud agent mode in the UI.

After submitting a prompt, select your agent from the list to view status and enter the machine.

Cloud agents require data retention on the order of a few days.

## Setup

Cloud agents run in an isolated ubuntu-based machine by default. Agents have internet access and can install packages.

#### GitHub or GitLab connection

Cloud agents clone your repo from GitHub or GitLab and work on a separate branch, pushing to your repo for easy handoff.

Grant read-write privileges to your repo (and any dependent repos or submodules). We'll support other providers (BitBucket, etc) in the future.

#### Base Environment Setup

You can view your environment configuration within Cursor by visiting the [Cursor Settings](cursor://anysphere.cursor-deeplink/settings) → `Cloud Agents` tab, or start the setup process by running `Cursor: Start Cloud Agent Setup` in the command palette.

For advanced cases, set up the environment yourself. Get an IDE instance connected to the remote machine. Set up your machine, install tools and packages, then take a snapshot. Configure runtime settings:

Install command runs before an agent starts and installs runtime dependencies. This might mean running `npm install` or `bazel build`.
Terminals run cloud processes while the agent works - like starting a web server or compiling protobuf files.

For the most advanced cases, use a Dockerfile for machine setup. The dockerfile lets you set up system-level dependencies: install specific compiler versions, debuggers, or switch the base OS image. Don't `COPY` the entire project - we manage the workspace and check out the correct commit. Still handle dependency installation in the install script.

Enter any required secrets for your dev environment - they're stored encrypted-at-rest (using KMS) in our database and provided in the cloud agent environment.

The machine setup lives in `.cursor/environment.json`, which can be committed in your repo (recommended) or stored privately. The setup flow guides you through creating `environment.json`.

#### Maintenance Commands

When setting up a new machine, we start from the base environment, then run the `install` command from your `environment.json`. This command is what a developer would run when switching branches - install any new dependencies.

For most people, the `install` command is `npm install` or `bazel build`.

To ensure fast machine startup, we cache disk state after the `install` command runs. Design it to run multiple times. Only disk state persists from the `install` command - processes started here won't be alive when the agent starts.

#### Startup Commands

After running `install`, the machine starts and we run the `start` command followed by starting any `terminals`. This starts processes that should be alive when the agent runs.

The `start` command can often be skipped. Use it if your dev environment relies on docker - put `sudo service docker start` in the `start` command.

`terminals` are for app code. These terminals run in a `tmux` session available to you and the agent. For example, many website repos put `npm run watch` as a terminal.

#### The environment.json Spec

The `environment.json` file can look like:

```
{
  "snapshot": "POPULATED_FROM_SETTINGS",
  "install": "npm install",
  "terminals": [
    {
      "name": "Run Next.js",
      "command": "npm run dev"
    }
  ]
}
```

Formally, the spec is [defined here](https://www.cursor.com/schemas/environment.schema.json).

#### Using AWS IAM Roles

Cursor supports assuming customer-provided IAM roles for deeper integration with AWS. This allows you to grant specific AWS permissions to cloud agents without sharing long-lived credentials.

Create the IAM role: In your AWS account, create the IAM role that you'd like the cloud agent to assume, and note its ARN (e.g. `arn:aws:iam::123456789012:role/acmeRole`).

Configure the IAM role secret: Navigate to [Cursor Dashboard → Cloud Agents](https://cursor.com/dashboard?tab=cloud-agents), and add a user or team secret named `CURSOR_AWS_ASSUME_IAM_ROLE_ARN` set to the ARN of the IAM role you just created.

Generate an external ID: Navigate to [Cursor Dashboard → Settings](https://cursor.com/dashboard?tab=settings) and find the External ID settings. If you don't see an external ID displayed, enter a placeholder value in the "AWS IAM Role ARN" field, click "Validate & Save", and reload the page - this will generate an external ID for your team (e.g. `cursor-xxx-yyy-zzz`).

Configure IAM role trust policy: In your AWS account, update the IAM role's trust policy to trust Cursor's role assumer. The trust policy should look like this:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCursorAssume",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::289469326074:role/roleAssumer"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "cursor-xxx-yyy-zzz"
        }
      }
    }
  ]
}
```

Replace `cursor-xxx-yyy-zzz` with the external ID generated for your team.

Environment Variables:

When configured, the following AWS environment variables are set in the cloud agent's environment:

`AWS_ACCESS_KEY_ID`
`AWS_SECRET_ACCESS_KEY`
`AWS_SESSION_TOKEN`

The AWS CLI and AWS SDKs should automatically pick up the environment variables.

Due to AWS constraints with role chaining, the assumed credentials expire
after 1 hour.

## Models

Only [Max Mode](/docs/context/max-mode)-compatible models are available for cloud agents.

## Pricing

Learn more about [Cloud Agent pricing](/docs/account/pricing#cloud-agent).

## Security

Cloud Agents are available in Privacy Mode. We never train on your code and only retain code for running the agent. [Learn more about Privacy mode](https://www.cursor.com/privacy-overview).

What you should know:

Grant read-write privileges to our GitHub app for repos you want to edit. We use this to clone the repo and make changes.
Your code runs inside our AWS infrastructure in isolated VMs and is stored on VM disks while the agent is accessible.
The agent has internet access.
The agent auto-runs all terminal commands, letting it iterate on tests. This differs from the foreground agent, which requires user approval for every command. Auto-running introduces data exfiltration risk: attackers could execute prompt injection attacks, tricking the agent to upload code to malicious websites. See [OpenAI's explanation about risks of prompt injection for cloud agents](https://platform.openai.com/docs/codex/agent-network#risks-of-agent-internet-access).
If privacy mode is disabled, we collect prompts and dev environments to improve the product.
If you disable privacy mode when starting a cloud agent, then enable it during the agent's run, the agent continues with privacy mode disabled until it completes.

## Dashboard settings

Workspace admins can configure additional settings from the Cloud Agents tab on the dashboard.

### Defaults Settings

Default model – the model used when a run does not specify one. Pick any model that supports Max Mode.
Default repository – when empty, agents ask the user to choose a repo. Supplying a repo here lets users skip that step.
Base branch – the branch agents fork from when creating pull requests. Leave blank to use the repository’s default branch.

### Security Settings

All security options require admin privileges.

Display agent summary – controls whether Cursor shows the agent's file-diff images and code snippets. Disable this if you prefer not to expose file paths or code in the sidebar.
Display agent summary in external channels – extends the previous toggle to Slack or any external channel you've connected.

Changes save instantly and affect new agents immediately.

## Naming History

Cloud Agents were formerly called Background Agents.