# Team Pricing | Cursor Docs

Source URL: https://cursor.com/docs/account/teams/pricing

---

Account
# Team Pricing

There are two teams plans: Teams ($40/user/mo) and Enterprise (Custom).

Team plans provide additional features like:

Privacy Mode enforcement
Admin Dashboard with usage stats (also accessible via [Admin API](/docs/account/teams/admin-api))
Centralized team billing
SAML/OIDC SSO

We recommend Teams for any customer that is happy self-serving. We recommend [Enterprise](/docs/enterprise) for customers that need priority support, pooled usage, invoicing, SCIM, or advanced security controls. [Contact sales](https://cursor.com/contact-sales) to get started.

## How pricing works

Teams pricing is usage-based. Each seat includes monthly usage, and you can continue using Cursor beyond that with on-demand usage.

### Included usage

Each team seat ($40/mo) comes with $20/mo of included usage. This usage:

Is allocated per user (each user gets their own $20)
Does not transfer between team members
Resets at the start of each billing cycle
Covers all agent requests at public list API prices + Cursor Token Fee

Our [Enterprise plan](/docs/enterprise) offers pooled usage shared between all users in a team. [Get in touch](https://cursor.com/contact-sales) with our team to learn more.

### On-demand usage

On-demand usage allows you to continue using models after your included amount is consumed, billed in arrears.

When exceeding the $20 of included usage, team members automatically continue with on-demand usage:

Billed monthly at the same rates (API prices + Cursor Token Fee)
No interruption in service or quality
Tracked per user in your admin dashboard (see [spending data API](/docs/account/teams/admin-api#get-spending-data))
Can be controlled with spending limits

On-demand usage is enabled by default for the Teams plan.

### Cursor Token Fee

All non-Auto agent requests include a $0.25 per million tokens fee for team plans. This covers:

Codebase indexing and search
Custom model execution (Tab, Apply, etc.)
Infrastructure and processing costs

This fee applies to all tokens: input, output, and cached tokens. This only applies to team plans.

## Active seats

Cursor bills per active user, not pre-allocated seats. Add or remove users anytime and billing will adjust immediately.

Refunds appear as account credit on your next invoice. Your renewal date stays the same.

## Spending controls

Teams can configure monthly team-wide spending limits, as well as optional per-user spending limits. You can manage these limits through the dashboard or programmatically via the [Admin API](/docs/account/teams/admin-api#set-user-spend-limit).

Contact `enterprise@cursor.com` for volume discounts on larger teams.

## Model Pricing

All prices are per million tokens. Teams are charged at public list API prices + [Cursor Token Fee](#cursor-token-fee).

NameInputCache WriteCache ReadOutputClaude 4.1 Opus$15$18.75$1.5$75Claude 4.5 Sonnet$3$3.75$0.3$15Composer 1$1.25$1.25$0.125$10Gemini 3 Pro$2$2$0.2$12GPT-5.1$1.25$1.25$0.125$10GPT-5.1 Codex$1.25$1.25$0.125$10Grok Code$0.2$0.2$0.02$1.5Show more models