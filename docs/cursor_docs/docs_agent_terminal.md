# Terminal | Cursor Docs

Source URL: https://cursor.com/docs/agent/terminal

---

Core
# Terminal

Agent runs shell commands directly in your terminal, with safe sandbox execution for macOS users. Command history persists across sessions. Click skip to interrupt running commands with `Ctrl+C`.

## Sandbox

Sandbox is currently available on macOS only. Linux support is coming soon. Windows users can use WSL or devcontainers for sandboxed command execution.

Auto mode is not currently compatible with Sandbox.

By default, Agent runs terminal commands in a restricted environment that blocks unauthorized file access and network activity. Commands execute automatically while staying confined to your workspace. On macOS, this is implemented using `sandbox-exec`.

### How the sandbox works

The sandbox prevents unauthorized access while allowing workspace operations:

Access TypeDescriptionFile accessRead access to the filesystemRead and write access to workspace directoriesNetwork accessBlocked by default (configurable in settings)Temporary filesFull access to `/tmp/` or equivalent system temp directories

The `.cursor` configuration directory stays protected regardless of allowlist settings.

### Allowlist

Commands on the allowlist skip sandbox restrictions and run immediately. You can add commands to the allowlist by choosing "Add to allowlist" when prompted after a sandboxed command fails.

When a sandboxed command fails due to restrictions, you can:

OptionDescriptionSkipCancel the command and let Agent try something elseRunExecute the command without sandbox restrictionsAdd to allowlistRun without restrictions and automatically approve it for future use

## Editor Configuration

Configure how Agent runs terminal commands in the editor by navigating to Settings -> Cursor Settings -> Agents -> Auto-Run.

Editor SettingDescriptionAuto-Run ModeChoose how Agent runs tools like command execution, MCP, and file writes. Users can select from three options: • Run in Sandbox: Tools and commands will auto-run in sandbox where possible. Available on macOS only. • Ask Every Time: All tools and commands require user approval before running. • Run Everything: The agent runs all tools and commands automatically without asking for user input.Auto-Run Network AccessChoose whether commands that run in the sandbox have network access.Allow Git Writes Without ApprovalWhen enabled, git write operations (commit, push, etc.) run without approval in the sandbox. When disabled, they require approval. Note that git push and similar actions will require network access to run.Command AllowlistCommands that can run automatically outside of the sandbox.MCP AllowlistMCP tools that can run automatically outside of the sandbox.Browser ProtectionPrevent Agent from automatically running [Browser](https://cursor.com/docs/agent/browser) tools.File-Deletion ProtectionPrevent Agent from deleting files automatically.Dotfile ProtectionPrevent Agent from modifying dot files like .gitignore automatically.External-File ProtectionPrevent Agent from creating or modifying files outside of the workspace automatically.

## Enterprise Controls

Only available for Enterprise subscriptions.

Enterprise admins can override editor configurations or change which settings are visible for end users. Navigate to Settings -> Auto-Run in the [web dashboard](https://cursor.com/dashboard?tab=settings) to view and change these settings.

Admin SettingDescriptionAuto-Run ControlsEnable controls for auto-run and sandbox mode. If disabled, the default behavior for all end users is that commands will auto-run in the sandbox when available, otherwise they will ask for permission to run.Sandboxing ModeControl whether sandbox is available for end users. When enabled, commands will run automatically in the sandbox even if they are not on the allowlist.Sandbox NetworkingChoose whether commands that run in the sandbox have network access.Sandbox Git AccessWhen enabled, git write operations (commit, push, etc.) run without approval in the sandbox. When disabled, they require approval. Note that git push and similar actions will require network access to run.Delete File ProtectionPrevent Agent from deleting files automatically.MCP Tool ProtectionWhen enabled, prevents the agent from automatically running MCP tools.Terminal Command AllowlistSpecify which terminal commands can run automatically without sandboxing. If empty, all commands require manual approval. When sandbox is enabled, commands not on this list will auto-run in sandbox mode.Enable Run EverythingGive end users the ability to enable the `Run Everything` Auto-Run-Mode.

## Troubleshooting

Some shell themes (for example, Powerlevel9k/Powerlevel10k) can interfere with
the inline terminal output. If your command output looks truncated or
misformatted, disable the theme or switch to a simpler prompt when Agent runs.

### Disable heavy prompts for Agent sessions

Use the `CURSOR_AGENT` environment variable in your shell config to detect when
the Agent is running and skip initializing fancy prompts/themes.

```
# ~/.zshrc — disable Powerlevel10k when Cursor Agent runs
if [[ -n "$CURSOR_AGENT" ]]; then
  # Skip theme initialization for better compatibility
else
  [[ -r ~/.p10k.zsh ]] && source ~/.p10k.zsh
fi
```

```
# ~/.bashrc — fall back to a simple prompt in Agent sessions
if [[ -n "$CURSOR_AGENT" ]]; then
  PS1='\u@\h \W \$ '
fi
```