# Browser | Cursor Docs

Source URL: https://cursor.com/docs/agent/browser

---

Core
# Browser

Agent can control a web browser to test applications, audit accessibility, convert designs into code, and more. With full access to console logs and network traffic, Agent can debug issues and automate comprehensive testing workflows.

For enterprise customers, browser controls are governed by MCP allowlist or denylist.

## Native integration

Agent displays browser actions like screenshots and actions in the chat, as well as the browser window itself either in a separate window or an inline pane.

We've optimized the browser tools to be more efficient and reduce token usage, as well as:

Efficient log handling: Browser logs are written to files that Agent can grep and selectively read. Instead of summarizing verbose output after every action, Agent reads only the relevant lines it needs. This preserves full context while minimizing token usage.
Visual feedback with images: Screenshots are integrated directly with the file reading tool, so Agent actually sees the browser state as images rather than relying on text descriptions. This enables better understanding of visual layouts and UI elements.
Smart prompting: Agent receives additional context about browser logs, including total line counts and preview snippets, helping it make informed decisions about what to inspect.
Development server awareness: Agent is prompted to detect running development servers and use the correct ports instead of starting duplicate servers or guessing port numbers.

You can use Browser without installing or configuring any external tools.

## Browser capabilities

Agent has access to the following browser tools:

### Navigate

### Click

### Type

### Scroll

### Screenshot

### Console Output

### Network Traffic

## Session persistence

Browser state persists between Agent sessions based on your workspace. This means:

Cookies: Authentication cookies and session data remain available across browser sessions
Local Storage: Data stored in `localStorage` and `sessionStorage` persists
IndexedDB: Database content is retained between sessions

The browser context is isolated per workspace, ensuring that different projects maintain separate storage and cookie states.

## Use cases

### Accessibility improvements

Agent can audit and improve web accessibility to meet WCAG compliance standards.

@browser Check color contrast ratios, verify semantic HTML and ARIA labels, test keyboard navigation, and identify missing alt text
[Cursor LogoTry in Cursor](cursor://anysphere.cursor-deeplink/prompt?text=%40browser+Check+color+contrast+ratios%2C+verify+semantic+HTML+and+ARIA+labels%2C+test+keyboard+navigation%2C+and+identify+missing+alt+text)

### Automated testing

Agent can execute comprehensive test suites and capture screenshots for visual regression testing.

@browser Fill out forms with test data, click through workflows, test responsive designs, validate error messages, and monitor console for JavaScript errors
[Cursor LogoTry in Cursor](cursor://anysphere.cursor-deeplink/prompt?text=%40browser+Fill+out+forms+with+test+data%2C+click+through+workflows%2C+test+responsive+designs%2C+validate+error+messages%2C+and+monitor+console+for+JavaScript+errors)

### Design to code

Agent can convert designs into working code with responsive layouts.

@browser Analyze this design mockup, extract colors and typography, and generate pixel-perfect HTML and CSS code
[Cursor LogoTry in Cursor](cursor://anysphere.cursor-deeplink/prompt?text=%40browser+Analyze+this+design+mockup%2C+extract+colors+and+typography%2C+and+generate+pixel-perfect+HTML+and+CSS+code)

### Adjusting UI design from screenshots

Agent can refine existing interfaces by identifying visual discrepancies and updating component styles.

@browser Compare current UI against this design screenshot and adjust spacing, colors, and typography to match
[Cursor LogoTry in Cursor](cursor://anysphere.cursor-deeplink/prompt?text=%40browser+Compare+current+UI+against+this+design+screenshot+and+adjust+spacing%2C+colors%2C+and+typography+to+match)

## Security

Browser runs as a secure web view and is controlled using an MCP server running as an extension. Multiple layers protect you from unauthorized access and malicious actions.
Cursor's Browser integrations have also been reviewed by multiple external security auditors.

### Authentication and isolation

The browser implements several security measures:

Token authentication: Agent layout generates a random authentication token before each browser session starts
Tab isolation: Each browser tab receives a unique random ID to prevent cross-tab interference
Session-based security: Tokens regenerate for each new browser session

### Tool approval

Browser tools require your approval by default. Review each action before Agent executes it. This prevents unexpected navigation, data submission, or script execution.

You can configure approval settings in Agent Settings. Available modes:

ModeDescriptionManual approvalReview and approve each browser action individually (recommended)Allow-listed actionsActions matching your allow list run automatically; others require approvalAuto-runAll browser actions execute immediately without approval (use with caution)

### Allow and block lists

Browser tools integrate with Cursor's [security guardrails](/docs/agent/security). Configure which browser actions run automatically:

Allow list: Specify trusted actions that skip approval prompts
Block list: Define actions that should always be blocked
Access settings through: `Cursor Settings` → `Chat` → `Auto-Run`

The allow/block list system provides best-effort protection. AI behavior can be unpredictable due to prompt injection and other issues. Review auto-approved actions regularly.

Never use auto-run mode with untrusted code or unfamiliar websites. Agent could execute malicious scripts or submit sensitive data without your knowledge.

### Browser context

The browser window's behavior changes based on where you run it:

ContextBehaviorChromeOpens an isolated Chrome process for full-screen browsingInternalOpens as a pane within Cursor

Both contexts allow the agent to control the browser a set MCP tools to control the browser. See further details below.

## Recommended models

We recommend using Sonnet 4.5, GPT-5, and Auto for the best performance.

## Enterprise usage

For enterprise customers, browser functionality is managed through toggling availability under MCP controls. Admins have granular controls over each MCP server, as well as over browser access.

### Enabling browser for enterprise

To enable browser capabilities for your enterprise team:

Navigate to your [Settings Dashboard](https://cursor.com/dashboard?tab=settings)
Go to MCP Configuration
Toggle "browser features"

Once configured, users in your organization will have access to browser tools based on your MCP allowlist or denylist settings.

### Origin allowlist

Enterprise administrators can configure an origin allowlist that restricts which sites the agent can automatically navigate to and where MCP tools can run. This provides granular control over browser access for security and compliance.

#### Configuration

To configure the origin allowlist:

Contact your Enterprise account manager to enable the feature
Navigate to your [Admin Dashboard](https://cursor.com/dashboard?tab=settings)
Go to Browser Security or MCP Configuration
Add origins to the allowlist (e.g., `*`, `http://localhost:3000`, `https://internal.example.com`)

#### Behavior

When an origin allowlist is configured:

Automatic navigation: The agent can only use the `browser_navigate` tool to visit URLs matching origins in the allowlist
MCP tool execution: MCP tools can only run on origins that are in the allowlist
Manual navigation: Users can still manually navigate the browser to any URL, including origins outside the allowlist (useful for viewing documentation or inspecting external sites)
Tool restrictions: Once the browser is on an origin not in the allowlist, browser tools (click, type, navigate) are blocked, even if the user navigated there manually

#### Edge cases

The origin allowlist provides best-effort protection. Be aware of these behaviors:

Link navigation: If the agent clicks a link on an allowed domain that navigates to a non-allowed origin, the navigation will succeed
Redirects: If the agent navigates to an allowed origin that subsequently redirects to a non-allowed origin, the redirect will be permitted
JavaScript navigation: Client-side navigation (via `window.location` or similar) from an allowed origin to a non-allowed origin will succeed

The origin allowlist restricts automatic agent navigation but cannot prevent all navigation paths. Review your allowlist regularly and consider the security implications of allowing access to domains that may redirect or link to external sites.