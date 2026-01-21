# API Keys | Cursor Docs

Source URL: https://cursor.com/docs/settings/api-keys

---

Core
# API Keys

Use your own API keys to send unlimited AI messages at your own cost. When configured, Cursor will use your API keys to call LLM providers directly.

To use your API key, go to `Cursor Settings` > `Models` and enter your API keys. Click Verify. Once validated, your API key is enabled.

Custom API keys only work with standard chat models. Features requiring
specialized models (like Tab Completion) will continue using Cursor's built-in
models.

Cursor's [Zero Data Retention policy](/docs/account/teams/dashboard#privacy-settings) does not apply when using your own API keys. Your data handling will be subject to the privacy policies of your chosen AI provider (OpenAI, Anthropic, Google, Azure, or AWS).

## Supported providers

OpenAI - Standard, non-reasoning chat models only. The model picker will show the OpenAI models available.
Anthropic - All Claude models available through the Anthropic API.
Google - Gemini models available through the Google AI API.
Azure OpenAI - Models deployed in your Azure OpenAI Service instance.
AWS Bedrock - Use AWS access keys, secret keys, or IAM roles. Works with models available in your Bedrock configuration.

A unique external ID is generated after validating your Bedrock IAM role, which can be added to your IAM role trust policy for additional security.

## FAQ

### Will my API key be stored or leave my device?