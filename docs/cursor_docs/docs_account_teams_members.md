# Members & Roles | Cursor Docs

Source URL: https://cursor.com/docs/account/teams/members

---

Account
# Members & Roles

Cursor teams have three roles:

## Roles

Members are the default role with access to Cursor's Pro features.

Full access to Cursor's Pro features
No access to billing settings or admin dashboard
Can see their own usage and remaining usage-based budget

Admins control team management and security settings.

Full access to Pro features
Add/remove members, modify roles, setup SSO
Configure usage-based pricing and spending limits
Access to team analytics

Unpaid Admins manage teams without using a paid seat - ideal for IT or finance staff who don't need Cursor access.

Not billable, no Pro features
Same administrative capabilities as Admins

Unpaid Admins require at least one paid user on the team.

## Role Comparison

CapabilityMemberAdminUnpaid AdminUse Cursor features✓✓Invite members✓✓✓Remove members✓✓Change user role✓✓Admin dashboard✓✓Configure SSO/Security✓✓Manage Billing✓✓View Analytics✓✓Manage Access✓✓Set usage controls✓ [*](/docs/enterprise/usage-and-spend-controls#team-spending-limits)✓ [*](/docs/enterprise/usage-and-spend-controls#team-spending-limits)✓ [*](/docs/enterprise/usage-and-spend-controls#team-spending-limits)Requires paid seat✓✓

## Managing members

All team members can invite others. We don't currently control invites.

### Add member

Add members three ways:

Email invitation

Click `Invite Members`
Enter email addresses
Users receive email invites

Invite link

Click `Invite Members`
Copy `Invite Link`
Share with team members

SSO

Configure SSO in [admin dashboard](/docs/account/teams/sso)
Users auto-join when logging in via SSO email

Invite links have a long expiration date - anyone with the link can join.
Revoke them or use [SSO](/docs/account/teams/sso)

### Remove member

Admins can remove members anytime via context menu → "Remove".

Billing:

If a member has used any credits, their seat remains occupied until the end of the billing cycle
Billing is automatically adjusted with pro-rated credit for removed members applied to the next invoice

Data deletion:

When a user is removed from the team, their data (including Memories and Cloud Agent data) is permanently deleted
When an entire team is deleted, all associated data is permanently deleted
There must be at least one Admin and one paid member on the team at all times

### Change role

Admins can change roles for other members by clicking the context menu and then use the "Change role" option.

There must be at least one Admin, and one paid member on the team at all times.

## Security & SSO

SAML 2.0 Single Sign-On (SSO) is available on Team plans. Key features include:

Configure SSO connections ([learn more](/docs/account/teams/sso))
Set up domain verification
Automatic user enrollment
SSO enforcement options
Identity provider integration (Okta, etc)

Domain verification is required to enable SSO.

## Usage Controls

Access usage settings to:

Enable usage-based pricing
Enable for premium models
Set admin-only modifications
Set monthly spending limits
Monitor team-wide usage

## Billing

When adding team members:

Each member or admin adds a billable seat (see [pricing](https://cursor.com/pricing))
New members are charged pro-rata for their remaining time in the billing period
Unpaid admin seats aren't counted

Mid-month additions charge only for days used. When removing members who have used credits, their seat remains occupied until the end of the billing cycle - no pro-rated refunds are given.

Role changes (e.g., Admin to Unpaid Admin) adjust billing from the change date. Choose monthly or yearly billing.

Monthly/yearly renewal occurs on your original signup date, regardless of member changes.

### Switch to Yearly billing

Save 20% by switching from monthly to yearly:

Go to [Dashboard](https://cursor.com/dashboard)
In account section, click "Advanced" then "Upgrade to yearly billing"

You can only switch from monthly to yearly via dashboard. To switch from
yearly to monthly, contact [hi@cursor.com](mailto:hi@cursor.com).