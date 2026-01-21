# Deeplinks | Cursor Docs

Source URL: https://cursor.com/docs/integrations/deeplinks

---

Integrations
# Deeplinks

Deeplinks allow you to share prompts and commands with others, enabling collaboration and knowledge sharing across teams and communities.

Links can also be opened via [cursor.com](https://cursor.com). Append the path and url params to the end of the url, for example: [cursor.com/link/prompt?text=...](https://cursor.com/link/prompt?text=Research+and+find+one+bug+in+this+codebase)

Always review your prompts and commands before sharing to ensure they don't contain sensitive information like API keys, passwords, or proprietary code.

## Prompts

Share prompts that others can use to get started quickly with specific tasks or workflows. When someone clicks a prompt deeplink, it opens Cursor with the prompt pre-filled in the chat. The user must review and confirm the prompt before it gets executed. Deeplinks never trigger automatic execution.

Research and find one bug in this codebase
[Cursor LogoTry in Cursor](cursor://anysphere.cursor-deeplink/prompt?text=Research+and+find+one+bug+in+this+codebase)
PlaygroundTypeScriptPythonTextProgress circleCopy link

## Commands

Share commands that others can execute directly in their Cursor environment. Command deeplinks allow you to share custom commands defined in your `.cursor/commands` directory. When someone clicks a command deeplink, it opens Cursor and creates a new command with the specified name and content. The user must review and confirm the command before it gets executed.

debug-api: Add console.log statements to debug API responses
[Cursor LogoAdd to Cursor](cursor://anysphere.cursor-deeplink/command?name=debug-api&text=Add+console.log+statements+to+debug+API+responses)
PlaygroundTypeScriptPythonNameUse letters, numbers, dots, hyphens, and underscores onlyContentProgress circleThis will be saved as a command in .cursor/commands/Copy link

## Rules

Share rules that others can add to their Cursor environment. Rule deeplinks allow you to share custom rules defined in your `.cursor/rules` directory. When someone clicks a rule deeplink, it opens Cursor and creates a new rule with the specified name and content. The user must review and confirm the rule before it gets added.

typescript-strict: Always use strict TypeScript types and avoid 'any'
[Cursor LogoAdd to Cursor](cursor://anysphere.cursor-deeplink/rule?name=typescript-strict&text=Always+use+strict+TypeScript+types+and+avoid+%27any%27)
PlaygroundTypeScriptPythonNameUse letters, numbers, dots, hyphens, and underscores onlyContentProgress circleThis will be saved as a rule in .cursor/rules/Copy link

## FAQ

### What is the maximum length for deeplink URLs?

### How do I use deeplinks on the web instead of in the Cursor app?