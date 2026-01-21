# Large Codebases | Cursor Docs

Source URL: https://cursor.com/docs/cookbook/large-codebases

---

Cookbook
# Large Codebases

Working with large codebases introduces a new set of challenges than working on smaller projects. Drawing from both our experience scaling Cursor's own codebase and insights from customers managing massive codebases, we've discovered some useful patterns for handling increased complexity.

Let's explore some of these techniques that we've found be useful for large codebases.

## Use Chat to quickly get up to speed on unfamiliar code

Navigating a large codebase, especially if it's new to you, can be challenging. You often grep, search, and click around to find the specific parts of the codebase you're looking for. With [Chat](/docs/chat/overview), you can start asking questions to find what you're looking for and get a detailed explanation of how it works.

Here we're getting help to find implementation details of codebase indexing in Cursor, and even asking for some examples to make it easier to understand.

## Write rules for domain-specific knowledge

If you were onboarding a new collaborator into your codebase, what context would you give them to make sure they can start doing meaningful contributions?

Your answer to this question is likely valuable information for Cursor to understand as well. For every organization or project, there's latent knowledge that might not be fully captured in your documentation. Using rules effectively is the single best way to ensure Cursor is getting the full picture.

For example, if you're writing instructions for how to implement a new feature or service, consider writing a short rule to document it for posterity.

```
---
description: Add a new VSCode frontend service
---

1. **Interface Definition:**
   - Define a new service interface using `createDecorator` and ensure `_serviceBrand` is included to avoid errors.

2. **Service Implementation:**
   - Implement the service in a new TypeScript file, extending `Disposable`, and register it as a singleton with `registerSingleton`.

3. **Service Contribution:**
   - Create a contribution file to import and load the service, and register it in the main entrypoint.

4. **Context Integration:**
   - Update the context to include the new service, allowing access throughout the application.
```

If there are common formatting patterns that you want to make sure Cursor adheres to, consider auto-attaching rules based on glob patterns.

```
---
globs: *.ts
---
- Use bun as package manager. See [package.json](mdc:backend/reddit-eval-tool/package.json) for scripts
- Use kebab-case for file names
- Use camelCase for function and variable names
- Use UPPERCASE_SNAKE_CASE for hardcoded constants
- Prefer `function foo()` over `const foo = () =>`
- Use `Array<T>` instead of `T[]`
- Use named exports over default exports, e.g (`export const variable ...`, `export function `)
```

## Stay close to the plan-creation process

For larger changes, spending an above-average amount of thought to create a precise, well-scoped plan can significantly improve Cursor's output.

If you find that you're not getting the result you want after a few different variations of the same prompt, consider zooming out and creating a more detailed plan from scratch, as if you were creating a PRD for a coworker. Oftentimes the hard part is figuring out what change should be made, a task suited well for humans. With the right instructions, we can delegate some parts of the implementation to Cursor.

One way to use AI to augment the plan-creation process is to use Ask mode. To create a plan, turn on Ask mode in Cursor and dump whatever context you have from your project management systems, internal docs, or loose thoughts. Think about what files and dependencies you have in the codebase that you already know you want to include. This can be a file that includes pieces of code you want to integrate with, or perhaps a whole folder.

Here's an example prompt:

Planning prompt
```
- create a plan for how we shoud create a new feature (just like @existingfeature.ts)
- ask me questions (max 3) if anything is unclear
- make sure to search the codebase

here's some more context from [project management tool]:
[pasted ticket description]
```

We're asking the model to create a plan and gather context by asking the human questions, referencing any earlier exploration prompts and also the ticket descriptions. Using a thinking model like `claude-sonnet-4.5`, `gpt-5-codex`, or `gemini-2.5-pro` is recommended as they can understand the intent of the change and better synthesize a plan.

From this, you can iteratively formulate the plan with the help of Cursor before starting implementation.

## Pick the right tool for the job

One of the most important skills in using Cursor effectively is choosing the right tool for the job. Think about what you're trying to accomplish and pick the approach that will keep you in flow.

ToolUse caseStrengthLimitation[Tab](/docs/tab/overview)Quick, manual changesFull control, fastSingle-file[Inline Edit](/docs/inline-edit/overview)Scoped changes in one fileFocused editsSingle-file[Chat](/docs/chat/overview)Larger, multi-file changesAuto-gathers context, deep editsSlower, context-heavy

Each tool has its sweet spot:

Tab is your go-to for quick edits where you want to be in the driver's seat
Inline Edit shines when you need to make focused changes to a specific section of code
Chat is perfect for those bigger changes where you need Cursor to understand the broader context

When you're using Chat mode (which can feel a bit slower but is incredibly powerful), help it help you by providing good context. Use [@files](/docs/context/symbols) to point to similar code you want to emulate, or [@folder](/docs/context/symbols) to give it a better understanding of your project structure. And don't be afraid to break bigger changes into smaller chunks - starting fresh chats helps keep things focused and efficient.

## Takeaways

Scope down changes and don't try to do too much at once
Include relevant context when you can
Use Chat, Inline Edit & Tab for what they're best at
Create new chats often
Plan with [Ask mode](/docs/agent/modes), implement with [Agent mode](/docs/agent/overview)