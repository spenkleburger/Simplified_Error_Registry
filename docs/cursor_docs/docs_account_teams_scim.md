# SCIM | Cursor Docs

Source URL: https://cursor.com/docs/account/teams/scim

---

Account
# SCIM

## Overview

SCIM 2.0 provisioning automatically manages your team members and directory groups through your identity provider. Available on [Enterprise](/docs/enterprise) plans with SSO enabled.

## Prerequisites

Cursor [Enterprise plan](/docs/enterprise)
SSO must be configured first - SCIM requires an active SSO connection
Admin access to your identity provider (Okta, Azure AD, etc.)
Admin access to your Cursor organization

## How it works

### User provisioning

Users are automatically added to Cursor when assigned to the SCIM application in your identity provider. When unassigned, they're removed. Changes sync in real-time.

### Directory groups

Directory groups and their membership sync from your identity provider. Group and user management must be done through your identity provider - Cursor displays this information as read-only.

### Spend management

Set different per-user spend limits for each directory group. Directory group limits take precedence over team-level limits. Users in multiple groups receive the highest applicable spend limit.

## Setup

1
### Ensure SSO is configured

SCIM requires SSO to be set up first. If you haven't configured SSO yet,
follow the [SSO setup guide](/docs/account/teams/sso) before proceeding.
2
### Access Active Directory Management

Navigate to
[cursor.com/dashboard?tab=active-directory](https://www.cursor.com/dashboard?tab=active-directory)
with an admin account, or go to your dashboard settings and select the "Active
Directory Management" tab.
3
### Start SCIM setup

Once SSO is verified, you'll see a link for step-by-step SCIM setup. Click
this to begin the configuration wizard.
4
### Configure SCIM in your identity provider

In your identity provider: - Create or configure your SCIM application - Use
the SCIM endpoint and token provided by Cursor - Enable user and push group
provisioning - Test the connection
5
### Configure spend limits (optional)

Back in Cursor's Active Directory Management page: - View your synchronized
directory groups - Set per-user spend limits for specific groups as needed -
Review which limits apply to users in multiple groups

### Identity provider setup

For provider-specific setup instructions:

[Identity Provider GuidesSetup instructions for Okta, Azure AD, Google Workspace, and more.](https://workos.com/docs/integrations)

## Managing users and groups

All user and group management must be done through your identity provider.
Changes made in your identity provider will automatically sync to Cursor, but
you cannot modify users or groups directly in Cursor.

### User management

Add users by assigning them to your SCIM application in your identity provider
Remove users by unassigning them from the SCIM application
User profile changes (name, email) sync automatically from your identity provider

### Group management

Directory groups are automatically synced from your identity provider
Group membership changes are reflected in real-time
Use groups to organize users and set different spend limits

### Spend limits

Set different per-user limits for each directory group
Users inherit the highest spend limit from their groups
Group limits override the default team-wide per-user limit

## FAQ

### Why isn't SCIM management showing up in my dashboard?

Ensure SSO is properly configured and working before setting up SCIM. SCIM requires an active SSO connection to function.

### Why aren't users syncing?

Verify that users are assigned to the SCIM application in your identity provider. Users must be explicitly assigned to appear in Cursor.

### Why aren't groups appearing?

Check that push group provisioning is enabled in your identity provider's SCIM settings. Group sync must be configured separately from user sync.

### Why aren't spend limits applying?

Confirm users are properly assigned to the expected groups in your identity provider. Group membership determines which spend limits apply.

### Can I manage SCIM users and groups directly in Cursor?

No. All user and group management must be done through your identity provider. Cursor displays this information as read-only.

### How quickly do changes sync?

Changes made in your identity provider sync to Cursor in real-time. There may be a brief delay for large bulk operations.