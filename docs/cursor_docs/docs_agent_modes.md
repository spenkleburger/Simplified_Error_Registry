# Modes | Cursor Docs

Source URL: https://cursor.com/docs/agent/modes

---

Core
# Modes

Agent offers different modes optimized for specific tasks. Each mode has different capabilities and tools enabled to match your workflow needs.

Understanding [how agents work](/learn/agents) and [tool calling fundamentals](/learn/tool-calling) will help you choose the right mode for your task.

ModeForCapabilitiesTools[Agent](#agent)Complex features, refactoringAutonomous exploration, multi-file editsAll tools enabled[Ask](#ask)Learning, planning, questionsRead-only exploration, no automatic changesSearch tools only[Plan](#plan)Complex features requiring planningCreates detailed plans before execution, asks clarifying questionsAll tools enabled

## Agent

The default mode for complex coding tasks. Agent autonomously explores your codebase, edits multiple files, runs commands, and fixes errors to complete your requests.

## Ask

Read-only mode for learning and exploration. Ask searches your codebase and provides answers without making any changes - perfect for understanding code before modifying it.

## Plan

Plan Mode creates detailed implementation plans before writing any code. Agent researches your codebase, asks clarifying questions, and generates a reviewable plan you can edit before building.

Press Shift+Tab from the chat input to rotate to Plan Mode. Cursor also suggests it automatically when you type keywords that indicate complex tasks.

### How it works

Agent asks clarifying questions to understand your requirements
Researches your codebase to gather relevant context
Creates a comprehensive implementation plan
You review and edit the plan through chat or markdown files
Click to build the plan when ready

Plans open as ephemeral virtual files that you can view and edit. To save a plan to your workspace, click "Save to workspace" to store it in `.cursor/plans/` for future reference, team sharing, and documentation.

## Custom slash commands

For specialized workflows, you can create [custom slash commands](/docs/agent/chat/commands) that combine specific instructions with tool limitations.

Custom modes are deprecated in Cursor 2.1. Users with custom modes can select the "Export Custom Modes" option to transition their modes to [custom commands](/docs/agent/chat/commands).

### Examples

### Learn

### Refactor

### Debug

See the [Commands documentation](/docs/agent/chat/commands) for details on creating custom slash commands.

## Switching modes

Use the mode picker dropdown in Agent
Press Cmd+.Ctrl+. for quick switching
Set keyboard shortcuts in [settings](#settings)

## Settings

All modes share common configuration options:

SettingDescriptionModelChoose which AI model to useKeyboard shortcutsSet shortcuts to switch between modes

Mode-specific settings:

ModeSettingsDescriptionAgentAuto-run and Auto-fix ErrorsAutomatically run commands and fix errorsAskSearch CodebaseAutomatically find relevant files

## Changelog

### Custom modes removed

Custom modes have been removed from Cursor. If you previously used custom modes to create specialized workflows with specific tool combinations, you can now achieve the same functionality using [custom slash commands](/docs/agent/chat/commands).

Custom slash commands allow you to:

Define reusable workflows triggered with a `/` prefix
Include instructions about tool usage directly in the command prompt
Share commands across your team via team commands
Store commands in your project's `.cursor/commands` directory

To limit which tools the agent uses, simply include those instructions as part of the command prompt. For example, a command that should only use search tools might include: "Use only search tools (read file, codebase search, grep) - do not make any edits or run terminal commands."

See the [Commands documentation](/docs/agent/chat/commands) for complete details on creating and using custom slash commands.