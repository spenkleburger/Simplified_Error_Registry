# Usage and Spend Controls | Cursor Docs

Source URL: https://cursor.com/docs/enterprise/usage-and-spend-controls

---

Account
# Usage and Spend Controls

This documentation covers how to enable usage-based pricing, set spending limits, and monitor usage across your team.

## Usage-based pricing

To enable usage-based pricing, an admin must:

Go to your [team dashboard](https://cursor.com/dashboard)
Navigate to Settings
Find "Usage-Based Pricing Settings"
Enable usage-based pricing
Add a payment method

Usage-based pricing requires:

Team plan or Enterprise plan
Valid payment method on file
Admin access to enable

Enterprise plans offer pooled usage across the organization for flexible allocation.

See [Pricing](/docs/account/teams/pricing) for current rates.

## Spending limits

Set spending limits to control costs and prevent unexpected charges.

### Team spending limits

Set a monthly spending limit for your entire team:

Go to [team dashboard](https://cursor.com/dashboard)
Navigate to Settings > Usage-Based Pricing Settings
Set "Team Spending Limit"
Choose monthly amount

You can restrict access for modifying team spend limits through advanced settings.

Behavior when limit is reached:

AI features stop working for all team members
Users see a message that the spending limit was reached
Admins receive email notification
Non-AI features continue working normally

### Per-user spending limits

Set individual spending limits for each team member:

Go to [team dashboard](https://cursor.com/dashboard)
Navigate to Settings > Usage-Based Pricing Settings
Set "Per-User Spending Limit"
This applies to all users or specific users

Behavior when limit is reached:

AI features stop working for that specific user
Other team members continue unaffected
User sees notification of personal limit reached
Admins can increase individual limits as needed

## Monitoring usage

Track usage to understand costs, identify high-usage periods, and optimize spending.

### Team dashboard

The [team dashboard](https://cursor.com/dashboard) shows usage metrics including total spending, spending by day, top users by spending, and model usage breakdown.

Admins can:

Monitor usage in real-time via the analytics dashboard]
Track team performance and individual user adoption
View detailed breakdowns of individual users, including lines of code written and AI feature adoption

### Admin API

Query usage data programmatically using the [Admin API](/docs/account/teams/admin-api):

```
curl -X POST "https://api.cursor.com/teams/daily-usage-data" \
  -u YOUR_API_KEY: \
  -H "Content-Type: application/json" \
  -d '{"startDate": 1710720000000, "endDate": 1710892800000}'
```

Available endpoints:

`POST /teams/daily-usage-data` - Team usage summary and analytics
`POST /teams/filtered-usage-events` - Detailed usage events with filtering
`POST /teams/spend` - Team spending data and member costs

See [Admin API documentation](/docs/account/teams/admin-api) for complete reference.

### Analytics API

For deeper analytics, use the [Analytics API](/docs/account/teams/analytics-api):

Our new Analytics API provides granular usage metrics, custom date ranges, filtering by user, model, or project, and export to CSV or JSON.

### AI Code Tracking API

The [AI Code Tracking API](/docs/account/teams/ai-code-tracking-api) provides granular metrics on AI-generated code. This is an Enterprise-only feature for measuring AI adoption and productivity.

Track metrics including:

Lines of code accepted from AI suggestions
Per-commit AI usage metrics
Model attribution for generated code
Repository-level statistics
User-level productivity metrics

```
curl -X GET "https://api.cursor.com/analytics/ai-code/commits" \
  -u YOUR_API_KEY: \
  -d "startDate=7d&endDate=now"
```

See [AI Code Tracking API](/docs/account/teams/ai-code-tracking-api) for full documentation.

## Cost optimization strategies

Reduce spending while maintaining productivity:

### Model selection

Different [models](/docs/models) have different costs. Ensure you configure [model access controls](/docs/enterprise/model-and-integration-management) to use the most cost-effective models for your team.

### Context management

Additional context means more tokens, which leads to higher usage.

Only include relevant files in context
Avoid including entire repositories in prompts
Use specific file references rather than broad searches

Learn more about [context](/learn/context).