# Pricing | Cursor Docs

Source URL: https://cursor.com/docs/account/pricing

---

Get Started
# Pricing

You can try Cursor for free or purchase an individual or team plan.

## Individual

All individual plans include:

Unlimited tab completions
Extended agent usage limits on all models
Access to Bugbot
Access to Cloud Agents

Each plan includes usage charged at model inference [API prices](/docs/models#model-pricing):

Pro includes $20 of API agent usage + additional bonus usage
Pro Plus includes $70 of API agent usage + additional bonus usage
Ultra includes $400 of API agent usage + additional bonus usage

We work hard to grant additional bonus capacity beyond the guaranteed included usage. Since different models have different API costs, your model selection affects token output and how quickly your included usage is consumed. You can view usage and token breakdowns on [your dashboard](https://cursor.com/dashboard?tab=usage). Limit notifications are routinely shown in the editor.

To understand how usage is calculated, see our guide on [tokens and pricing](/learn/tokens-pricing).

### How much usage do I need?

Based on our usage data, you can expect the following usage levels:

Daily Tab users: Always stay within $20
Limited Agent users: Often stay within the included $20
Daily Agent users: Typically $60–$100/mo total usage
Power users (multiple agents/automation): Often $200+/mo total usage

Based on our usage data, limits are roughly equivalent to the following for a median user:

Pro: ~225 Sonnet 4.5 requests, ~550 Gemini requests, or ~500 GPT 5 requests
Pro+: ~675 Sonnet 4.5 requests, ~1,650 Gemini requests, or ~1,500 GPT 5 requests
Ultra: ~4,500 Sonnet 4.5 requests, ~11,000 Gemini requests, or ~10,000 GPT 5 requests

### What happens when I reach my limit?

When you exceed your included monthly usage, you'll be notified in the editor and can choose to:

Add on-demand usage: Continue using Cursor at the same API rates with pay-as-you-go billing
Upgrade your plan: Move to a higher tier for more included usage

On-demand usage is billed monthly at the same rates as your included usage. Requests are never downgraded in quality or speed.

## Teams

There are two teams plans: Teams ($40/user/mo) and Enterprise (Custom).

Team plans provide additional features like:

Privacy Mode enforcement
Admin Dashboard with usage stats
Centralized team billing
SAML/OIDC SSO

We recommend Teams for any customer that is happy self-serving. We recommend [Enterprise](https://cursor.com/contact-sales) for customers that need priority support, pooled usage, invoicing, SCIM, or advanced security controls.

Learn more about [Teams pricing](/docs/account/teams/pricing).

## Auto

Enabling Auto allows Cursor to select the premium model best fit for the immediate task and with the highest reliability based on current demand. This feature can detect degraded output performance and automatically switch models to resolve it.

Auto consumes usage at the following API rates:

Input + Cache Write: $1.25 per 1M tokens
Output: $6.00 per 1M tokens
Cache Read: $0.25 per 1M tokens

Both the editor and dashboard will show your usage, which includes Auto. If you prefer to select a model directly, usage is incurred at that model's list API price.

## Max Mode

Certain models have the ability to use [Max Mode](/docs/models#max-mode), which allows for longer reasoning and larger context windows up to 1M tokens. While the majority of coding tasks do not need to use Max Mode, it can be helpful for more complex queries, especially with large files or codebases. Using Max Mode will consume more usage. You can view all requests and token breakdowns on [your dashboard](https://cursor.com/dashboard?tab=usage).

## Bugbot

Bugbot is a separate product from Cursor subscriptions and has its own pricing plan.

Pro ($40/mo): Unlimited reviews on up to 200 PRs/month, unlimited access to Cursor Ask, integration with Cursor to fix bugs, and access to Bugbot Rules
Teams ($40/user/mo): Unlimited code reviews across all PRs, unlimited access to Cursor Ask, pooled usage across your team, and advanced rules and settings
Enterprise (Custom): Everything in Teams plus advanced analytics and reporting, priority support, and account management

Learn more about [Bugbot pricing](https://cursor.com/bugbot#pricing).

## Cloud Agent

Cloud Agents are charged at API pricing for the selected [model](/docs/models). You'll be asked to set a spend limit for Cloud Agents when you first start using them.

Virtual Machine (VM) compute for cloud agents will be priced in the
future.