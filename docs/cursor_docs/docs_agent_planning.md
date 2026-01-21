# Planning | Cursor Docs

Source URL: https://cursor.com/docs/agent/planning

---

Core
# Planning

Agent can plan ahead and manage complex tasks with structured to-do lists and message queuing, making long-horizon tasks easier to understand and track.

## Plan Mode

Plan Mode creates detailed implementation plans before writing any code. Agent researches your codebase, asks clarifying questions, and generates a reviewable plan you can edit before building.

Press Shift+Tab from the chat input to rotate to Plan Mode. Cursor also suggests it automatically when you type keywords that indicate complex tasks.

### How it works

Agent asks clarifying questions to understand your requirements
Researches your codebase to gather relevant context
Creates a comprehensive implementation plan
You review and edit the plan through chat or markdown files
Click to build the plan when ready

Plans open as ephemeral virtual files that you can view and edit. To save a plan to your workspace, click "Save to workspace" to store it in `.cursor/plans/` for future reference, team sharing, and documentation.

## Agent to-dos

Agent can break down longer tasks into manageable steps with dependencies, creating a structured plan that updates as work progresses.

### How it works

Agent automatically creates to-do lists for complex tasks
Each item can have dependencies on other tasks
The list updates in real-time as work progresses
Completed tasks are marked off automatically

### Visibility

To-dos appear in the chat interface
If [Slack integration](/docs/integrations/slack) is set up, to-dos are also visible there
You can view the full task breakdown at any time

For better planning, describe your end goal clearly. Agent will create more
accurate task breakdowns when it understands the full scope.

## Queued messages

Queue follow-up messages while Agent is working on the current task. Your instructions wait in line and execute automatically when ready.

### Using the queue

While Agent is working, type your next instruction
Press Ctrl+Enter to add it to the queue
Messages appear in order below the active task
Reorder queued messages by clicking arrow
Agent processes them sequentially after finishing

### Override the queue

To queue your message instead of using default messaging, use Ctrl+Enter. To send a message immediately without queuing, use Cmd+EnterCtrl+Enter. This "force pushes" your message, bypassing the queue to execute right away.

## Default messaging

Messages send as fast as possible by default, typically appearing right after Agent completes a tool call. This creates the most responsive experience.

### How default messaging works

Your message gets appended to the most recent user message in the chat
Messages typically attach to tool results and send immediately when ready
This creates a more natural conversation flow without interrupting Agent's current work
By default, this happens when you press Enter while Agent is working