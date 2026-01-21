# Enterprise | Cursor Docs

Source URL: https://cursor.com/docs/enterprise

---

Account
# Enterprise

Cursor provides enterprise-grade security, compliance, and administrative controls for organizations deploying AI-assisted development at scale.

## Security and compliance resources

For security reviews and compliance assessments, start with these resources:

[Trust Center](https://trust.cursor.com/) - Security practices, certifications, and compliance information
[Security page](https://cursor.com/security) - Detailed security architecture and controls
[Privacy Overview](https://cursor.com/privacy-overview) - Data handling and privacy guarantees
[Data Processing Agreement](https://cursor.com/terms/dpa) - GDPR-compliant DPA with data protection commitments

Our certifications include SOC2 Type II, and we maintain GDPR compliance. Visit the [Trust Center](https://trust.cursor.com/) for the latest certification documents and third-party assessment reports.

## Enterprise documentation

Learn how to deploy, configure, and manage Cursor for your organization. This documentation covers:

[Identity & access](/docs/enterprise/identity-and-access-management) - SSO, SCIM, RBAC, and MDM policies
[Privacy & data governance](/docs/enterprise/privacy-and-data-governance) - Data flows, Privacy Mode, and data residency
[Network configuration](/docs/enterprise/network-configuration) - Proxy setup, IP allowlisting, and encryption
[LLM safety & controls](/docs/enterprise/llm-safety-and-controls) - Hooks, terminal sandboxing, and agent controls
[Models & integrations](/docs/enterprise/model-and-integration-management) - Model controls, MCP, and third-party integrations
[Usage & spend controls](/docs/enterprise/usage-and-spend-controls) - Pricing, limits, and analytics
[Compliance & monitoring](/docs/enterprise/compliance-and-monitoring) - Audit logs and tracking
[Deployment patterns](/docs/enterprise/deployment-patterns) - MDM-managed IDE vs self-hosted CLI

## Key features

### Identity and access

[SSO and SAML](/docs/account/teams/sso) - Single sign-on for streamlined authentication
[SCIM](/docs/account/teams/scim) - Automated user provisioning and deprovisioning
[MDM policies](/docs/enterprise/identity-and-access-management#mdm-policies) - Enforce allowed team IDs and extensions on user devices

### Privacy and security

[Privacy Mode](https://cursor.com/privacy-overview) - Zero data retention with AI providers
[Agent Security](/docs/agent/security) - Guardrails for agent tool execution
[Hooks](/docs/agent/hooks) - Custom security and compliance workflows

### Administrative controls

[Dashboard](/docs/account/teams/dashboard) - Team management, settings, and monitoring
[Admin API](/docs/account/teams/admin-api) - Programmatic access to admin features
[Analytics](/docs/account/teams/analytics) - Usage metrics and insights
[AI Code Tracking API](/docs/account/teams/ai-code-tracking-api) - Per-commit AI usage metrics (Enterprise only)
[Analytics API](/docs/account/teams/analytics-api) - Usage metrics and insights

### Models and integrations

[Models](/docs/models) - Available models and configuration
[MCP](/docs/context/mcp) - Model Context Protocol server trust management
[Slack](/docs/integrations/slack) - Cloud Agents in Slack
[GitHub](/docs/integrations/github) - Repository integration
[Linear](/docs/integrations/linear) - Issue tracking integration
[Bugbot](/docs/bugbot) - Automated bug detection and fixing

### Monitoring and compliance

Audit logs - Track authentication, user management, and administrative actions (Enterprise only)
SIEM integration - Stream audit logs to your security tools

## Getting started

Review the [Trust Center](https://trust.cursor.com/) and [Security page](https://cursor.com/security) for your security assessment
Read through the [enterprise documentation](/docs/enterprise) to understand deployment options
Set up [SSO](/docs/account/teams/sso) and [SCIM](/docs/account/teams/scim) for user management
Deploy Cursor and configure [MDM policies](/docs/enterprise/deployment-patterns#mdm-configuration) to enforce team IDs and extensions
Review the [Dashboard](/docs/account/teams/dashboard) to monitor team usage

## Plan Comparison

### Team Admin & Billing

CapabilityIndividual PlansTeamsEnterpriseCentralized Billing✓✓Usage Spend ControlsPersonal limitsTeam + per-user limits[Pooled usage + admin-only controls](https://cursor.com/docs/enterprise/usage-and-spend-controls#usage-and-spend-controls)[Team Usage Analytics](https://cursor.com/docs/account/teams/analytics#analytics)[Analytics Dashboard](https://cursor.com/docs/account/teams/analytics)[Analytics Dashboard](https://cursor.com/docs/account/teams/analytics) & [AI Code Tracking API](https://cursor.com/docs/account/teams/ai-code-tracking-api)[SSO (SAML/OIDC)](https://cursor.com/docs/enterprise/identity-and-access-management#single-sign-on-sso-and-saml)✓✓SCIM Provisioning[Automated provisioning](https://cursor.com/docs/enterprise/identity-and-access-management)[Audit Logs](https://cursor.com/docs/enterprise/compliance-and-monitoring#audit-logs)✓

### Support & Legal

CapabilityIndividual & Teams PlansEnterpriseTechnical Support[Community & Standard Support](https://forum.cursor.com/)Priority SupportTerms[Online Terms](https://cursor.com/terms-of-service)[MSA & DPA](https://cursor.com/terms/msa)

### Centralized Agent Controls

CapabilityIndividual PlansTeamsEnterprisePrivacy ModeUser choiceEnforce org-wide[Enforce org-wide](https://cursor.com/docs/enterprise/privacy-and-data-governance#privacy-mode-enforcement)[Team Rules](https://cursor.com/docs/context/rules#team-rules)Enforceable + OptionalEnforceable + Optional[Hooks for Logging,Auditing, and more](https://cursor.com/docs/agent/hooks#hooks)✓MDM Distribution[MDM & Server-side distribution](https://cursor.com/docs/agent/hooks#team-distribution)[Agent Sandbox Mode](https://cursor.com/docs/agent/terminal#sandbox)✓✓Enforce org-wideRepository Access Control[Repository Blocklist](https://cursor.com/docs/enterprise/model-and-integration-management#git-repository-blocklist)Model Access Restrictions[Control which models users can use](https://cursor.com/docs/enterprise/model-and-integration-management#model-and-integration-management)

## Support

For enterprise support inquiries, contact your account team. For security vulnerabilities, see our [responsible disclosure program](/docs/agent/security#responsible-disclosure).