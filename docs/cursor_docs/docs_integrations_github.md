# GitHub | Cursor Docs

Source URL: https://cursor.com/docs/integrations/github

---

Integrations
# GitHub

[Cloud Agents](/docs/cloud-agent) and [Bugbot](/docs/bugbot) require the Cursor GitHub app to clone repositories and push changes.

## Installation

Go to [Integrations in Dashboard](https://cursor.com/dashboard?tab=integrations)
Click Connect next to GitHub
Choose repository either All repositories or Selected repositories

To disconnect your GitHub account, return to the integrations dashboard and click Disconnect Account.

## Using Agent in GitHub

The GitHub integration enables cloud agent workflows directly from pull requests and issues. You can trigger an agent to read context, implement fixes, and push commits by commenting `@cursor [prompt]` on any PR or issue.

If you have [Bugbot](/docs/bugbot) enabled, you can comment `@cursor fix` to read the suggested fix from Bugbot to trigger a cloud agent to address the issue.

## Permissions

The GitHub app requires specific permissions to work with cloud agents:

PermissionPurposeRepository accessClone your code and create working branchesPull requestsCreate PRs with agent changes for your reviewIssuesTrack bugs and tasks that agents discover or fixChecks and statusesReport on code quality and test resultsActions and workflowsMonitor CI/CD pipelines and deployment status

All permissions follow the principle of least privilege needed for cloud agent functionality.

## IP Allow List Configuration

If your organization uses GitHub's IP allow list feature to restrict access to your repositories, you'll need to contact support first to enable IP allowlist functionality for your team.

### Contact Support

Before configuring IP allowlists, contact [hi@cursor.com](mailto:hi@cursor.com) to enable this feature for your team. This is required for both configuration methods below.

### Enable IP allow list configuration for installed GitHub Apps (Recommended)

The Cursor GitHub app has the IP list already pre-configured. You can enable the allowlist for installed apps to automatically inherit this list. This is the recommended approach, as it allows us to update the list and your organization receives updates automatically.

To enable this:

Go to your organization's Security settings
Navigate to IP allow list settings
Check "Allow access by GitHub Apps"

For detailed instructions, see [GitHub's documentation](https://docs.github.com/en/enterprise-cloud@latest/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/managing-allowed-ip-addresses-for-your-organization#allowing-access-by-github-apps).

### Add IPs directly to your allowlist

If your organization uses IdP-defined allowlists in GitHub or otherwise cannot use the pre-configured allowlist, you can manually add the IP addresses:

```
184.73.225.134
3.209.66.12
52.44.113.131
```

The list of IP addresses may infrequently change. Teams using IP allow lists will be given advanced notice before IP addresses are added or removed.

## Troubleshooting

### Agent can't access repository

### Permission denied for pull requests

### App not visible in GitHub settings