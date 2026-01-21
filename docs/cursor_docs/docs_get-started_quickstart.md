# Quickstart | Cursor Docs

Source URL: https://cursor.com/docs/get-started/quickstart

---

Get Started
# Quickstart

This quickstart will walk you through a project using Cursor's core features. By the end, you'll be familiar with Tab, Inline Edit, and Agent.

[Download Cursor⤓](https://cursor.com/downloads)

## Open a project in Cursor

Use an existing project or clone our example:

Clone example projectUse existing project
Ensure git is installed
Clone the example project:

```
git clone git@github.com:voxelize/voxelize.git && \
cd voxelize && \
cursor .
```

We'll be showcasing using the example project, but you can use any project you have locally.

## Autocomplete with Tab

[Tab](/docs/configuration/kbd#tab) is the autocomplete model we've trained in-house. It's a great way to ease into AI assisted coding if you're not used to it. With Tab, you can:

Autocomplete multiple lines and blocks of code
Jump in and across files to the next autocomplete suggestion

Let's try it out:

Start typing the beginning of a function: `function calculate`
Tab suggestions appear automatically
Press Tab to accept the suggestion
Cursor suggests parameters and function bodies

## Inline Edit a selection

Select the function you just created
Press Cmd KCtrl K
Type "make this function calculate fibonacci numbers"
Press ReturnEnter to apply the changes
Cursor adds imports and documentation

## Chat with Agent

Open the Chat panel (Cmd ICtrl I)
Ask: "Add tests for this function and run them"
[Agent](/docs/agent/overview) will create a test file, write test cases, and run them for you

## Bonus

Read more about [Keyboard Shortcuts](/docs/configuration/kbd), [Themes](/docs/configuration/themes) and [Shell Commands](/docs/configuration/shell)

You can also explore these advanced features:

### Write a rule

### Set up an MCP server

## Next steps

We recommend taking the [AI Foundations course](/learn) to learn more about how AI works and how to use it effectively. This course covers topics like selecting models, managing context, and using agents.