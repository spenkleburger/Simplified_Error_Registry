# SSO | Cursor Docs

Source URL: https://cursor.com/docs/account/teams/sso

---

Account
# SSO

## Overview

SAML 2.0 SSO is available at no additional cost on Teams and Enterprise plans. Use your existing identity provider (IdP) to authenticate team members without separate Cursor accounts.

## Prerequisites

Cursor Team plan
Admin access to your identity provider (e.g., Okta)
Admin access to your Cursor organization

## Configuration Steps

1
### Sign in to your Cursor account

Navigate to [cursor.com/dashboard?tab=settings](https://www.cursor.com/dashboard?tab=settings) with an admin account.
2
### Locate the SSO configuration

Find the "Single Sign-On (SSO)" section and expand it.
3
### Begin the setup process

Click the "SSO Provider Connection settings" button to start SSO setup and follow the wizard.
4
### Configure your identity provider

In your identity provider (e.g., Okta):

Create new SAML application
Configure SAML settings using Cursor's information
Set up Just-in-Time (JIT) provisioning
5
### Verify domain

Verify the domain of your users in Cursor by clicking the "Domain verification settings" button.

### Identity Provider Setup Guides

For provider-specific setup instructions:

[Identity Provider GuidesSetup instructions for Okta, Azure AD, Google Workspace, and more.](https://workos.com/docs/integrations)

## Additional Settings

Manage SSO enforcement through admin dashboard
New users auto-enroll when signing in through SSO
Handle user management through your identity provider

## Multiple domains

To handle multiple domains in your organization:

Verify each domain separately in Cursor through the domain verification settings
Configure each domain in your identity provider
Each domain needs to go through the verification process independently

## Troubleshooting

If issues occur:

Verify domain is verified in Cursor
Ensure SAML attributes are properly mapped
Check SSO is enabled in admin dashboard
Match first and last names between identity provider and Cursor
Check provider-specific guides above
Contact [hi@cursor.com](mailto:hi@cursor.com) if issues persist