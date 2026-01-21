# Bugbot | Cursor Docs

Source URL: https://cursor.com/docs/bugbot

---

Core
# Bugbot

Bugbot reviews pull requests and identifies bugs, security issues, and code quality problems.

Bugbot includes a free tier: every user gets a limited number of free PR reviews each month. When you reach the limit, reviews pause until your next billing cycle. You can upgrade anytime to a 14‑day free Pro trial for unlimited reviews (subject to standard abuse guardrails).

## How it works

Bugbot analyzes PR diffs and leaves comments with explanations and fix suggestions. It runs automatically on each PR update or manually when triggered.

Runs automatic reviews on every PR update
Manual trigger by commenting `cursor review` or `bugbot run` on any PR
Uses existing PR comments as context: reads GitHub PR comments (top‑level and inline) to avoid duplicate suggestions and build on prior feedback
Fix in Cursor links open issues directly in Cursor
Fix in Web links open issues directly in [cursor.com/agents](https://cursor.com/agents)

## Setup

GitHub.comGitLab.comGitHub Enterprise ServerGitLab Self-Hosted
Requires Cursor admin access and GitHub org admin access.

Go to [cursor.com/dashboard](https://cursor.com/dashboard?tab=integrations)
Navigate to the Integrations tab
Click `Connect GitHub` (or `Manage Connections` if already connected)
Follow the GitHub installation flow
Return to the dashboard to enable Bugbot on specific repositories

## Configuration

IndividualTeam
### Repository settings

Team admins can enable Bugbot per repository, configure allow/deny lists for reviewers, and set:

Run only once per PR per installation, skipping subsequent commits
Disable inline reviews to prevent Bugbot from leaving comments directly on code lines

Bugbot runs for all contributors to enabled repositories, regardless of team membership.

### Personal settings

Team members can override settings for their own PRs:

Run only when mentioned by commenting `cursor review` or `bugbot run`
Run only once per PR, skipping subsequent commits
Enable reviews on draft PRs to include draft pull requests in automatic reviews

### Analytics

## Rules

Create `.cursor/BUGBOT.md` files to provide project-specific context for reviews. Bugbot always includes the root `.cursor/BUGBOT.md` file and any additional files found while traversing upward from changed files.

```
project/
  .cursor/BUGBOT.md          # Always included (project-wide rules)
  backend/
    .cursor/BUGBOT.md        # Included when reviewing backend files
    api/
      .cursor/BUGBOT.md      # Included when reviewing API files
  frontend/
    .cursor/BUGBOT.md        # Included when reviewing frontend files
```

### Team rules

Team admins can create rules from the [Bugbot dashboard](https://cursor.com/dashboard?tab=bugbot) that apply to all repositories in the team. These rules are available to every enabled repository, making it easy to enforce organization-wide standards.

When both Team Rules and project rule files (`.cursor/BUGBOT.md`) exist, Bugbot uses both. They are applied in this order: Team Rules → project BUGBOT.md (including nested files) → User Rules.

### Examples

### Security: Flag any use of eval() or exec()

### OSS licenses: Prevent importing disallowed licenses

### Language standards: Flag React componentWillMount usage

### Standards: Require tests for backend changes

### Style: Disallow TODO comments

## Admin Configuration API

Team admins can use the Bugbot Admin API to programmatically enable or disable Bugbot on repositories. This is useful for automating repository management or enabling Bugbot on large numbers of repositories at once.

### Creating an API Key

Visit the [Settings tab in the Cursor dashboard](https://cursor.com/dashboard?tab=settings)
Under Advanced, click New Admin API Key
Save the API key

### Enabling or Disabling Repositories

Use the `/bugbot/repo/update` endpoint to toggle Bugbot on or off for a repository:

```
curl -X POST https://api.cursor.com/bugbot/repo/update \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/your-org/your-repo",
    "enabled": true
  }'
```

Parameters:

`repoUrl` (string, required): The full URL of the repository
`enabled` (boolean, required): `true` to enable Bugbot, `false` to disable it

The dashboard UI may take a moment to reflect changes made through the API due to caching. The API response shows the current state in the database.

## Pricing

Bugbot offers two tiers: Free and Pro.

### Free tier

Every user on a paid plan gets a limited number of free PR reviews each month. For teams, each team member gets their own free reviews. When you reach the limit, reviews pause until your next billing cycle. You can upgrade anytime to a paid Bugbot plan for unlimited reviews.

### Pro tier

IndividualsTeams
### Per-user billing

Teams pay $40 per user per month for unlimited reviews.

We count a user as someone who authored PRs reviewed by Bugbot in a month.

All licenses are relinquished at the start of each billing cycle, and will be assigned out on a first-come, first-served basis. If a user doesn't author any PRs reviewed by Bugbot in a month, the seat can be used by another user.

### Seat limits

Team admins can set maximum Bugbot seats per month to control costs.

### Getting started

Subscribe through your team dashboard to enable billing.

### Abuse guardrails

In order to prevent abuse, we have a pooled cap of 200 pull requests per month for every Bugbot license. If you need more than 200 pull requests per month, please contact us at [hi@cursor.com](mailto:hi@cursor.com) and we'll be happy to help you out.

For example, if your team has 100 users, your organization will initially be able to review 20,000 pull requests per month. If you reach that limit naturally, please reach out to us and we'll be happy to increase the limit.

## Troubleshooting

If Bugbot isn't working:

Enable verbose mode by commenting `cursor review verbose=true` or `bugbot run verbose=true` for detailed logs and request ID
Check permissions to verify Bugbot has repository access
Verify installation to confirm the GitHub app is installed and enabled

Include the request ID from verbose mode when reporting issues.

## FAQ

### Does Bugbot read GitHub PR comments?

### Is Bugbot privacy-mode compliant?

### What happens when I hit the free tier limit?

### How do I give Bugbot access to my GitLab or GitHub Enterprise Server instance?