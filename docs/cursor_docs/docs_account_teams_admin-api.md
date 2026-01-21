# Admin API | Cursor Docs

Source URL: https://cursor.com/docs/account/teams/admin-api

---

APICopy pageShare feedbackExplain more
# Admin API

The Admin API lets you programmatically access your team's data, including member information, usage metrics, and spending details.

The Admin API uses [Basic Authentication](/docs/api#basic-authentication) with your API key as the username.
For details on creating API keys, authentication methods, rate limits, and best practices, see the [API Overview](/docs/api).

## Endpoints

### Get Team Members
GET`/teams/members`
Retrieve all team members and their details.

```
curl -X GET https://api.cursor.com/teams/members \
  -u YOUR_API_KEY:
```

Response:

```
{
  "teamMembers": [
    {
      "name": "Alex",
      "email": "developer@company.com",
      "role": "member"
    },
    {
      "name": "Sam",
      "email": "admin@company.com",
      "role": "owner"
    }
  ]
}
```

### Get Audit Logs
GET`/teams/audit-logs`
Retrieve audit log events for your team with filtering. Track team activity, security events, and configuration changes. Rate limited to 20 requests per minute per team. See [rate limits and best practices](/docs/api#rate-limits).

#### Parameters

`startTime` string | number
Start time (defaults to 7 days ago). See [Date Formats](#date-formats)
`endTime` string | number
End time (defaults to now). See [Date Formats](#date-formats)
`eventTypes` string
Comma-separated event types to filter by
`search` string
Search term to filter events
`page` number
Page number (1-indexed). Default: `1`
`pageSize` number
Results per page (1-500). Default: `100`
`users` string
Filter by users. See [User Filtering](#user-filtering) below
Date range cannot exceed 30 days. Make multiple requests for longer periods.

#### Date Formats

The `startTime` and `endTime` parameters support multiple formats:

Relative shortcuts: `now`, `today`, `yesterday`, `7d` (7 days ago), `5h` (5 hours ago), `300s` (300 seconds ago)
ISO 8601 strings: `2024-01-15T12:00:00Z` or `2024-01-15T10:00:00-05:00`
YYYY-MM-DD format: `2024-01-15` (time defaults to 00:00:00 UTC)
Unix timestamps: `1705315200` (seconds) or `1705315200000` (milliseconds)

Examples:

`?startTime=7d&endTime=now` - Last 7 days
`?startTime=5h&endTime=now` - Last 5 hours
`?startTime=2024-01-15&endTime=2024-01-20` - Specific date range
`?startTime=1705315200000&endTime=1705401600000` - Unix timestamps

#### User Filtering

The `users` parameter accepts multiple formats, comma-separated:

Email addresses: `developer@company.com,admin@company.com`
Encoded user IDs: `user_PDSPmvukpYgZEDXsoNirw3CFhy,user_kljUvI0ASZORvSEXf9hV0ydcso`

You can mix formats: `developer@company.com,12345,user_PDSPmvukpYgZEDXsoNirw3CFhy`

Maximum number of users per request equals `pageSize`.

```
curl -X GET "https://api.cursor.com/teams/audit-logs?users=admin@company.com,developer@company.com&eventTypes=login,settings_changed" \
  -u YOUR_API_KEY:
```

Response:

```
{
  "events": [
    {
      "event_id": "evt_abc123",
      "timestamp": "2024-01-15T12:30:00.000Z",
      "user_email": "admin@company.com",
      "event_type": "settings_changed",
      "event_data": {
        "setting_name": "team_spend_limit",
        "old_value": 1000,
        "new_value": 2000
      }
    },
    {
      "event_id": "evt_def456",
      "timestamp": "2024-01-15T10:15:00.000Z",
      "user_email": "developer@company.com",
      "event_type": "login",
      "event_data": {
        "ip_address": "192.168.1.1",
        "user_agent": "Cursor/0.42.0"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 100,
    "totalCount": 2,
    "totalPages": 1,
    "hasNextPage": false,
    "hasPreviousPage": false
  },
  "params": {
    "teamId": 12345,
    "startDate": 1704729600000,
    "endDate": 1705334400000
  }
}
```

### Get Daily Usage Data
POST`/teams/daily-usage-data`
Retrieve daily usage metrics for your team. Data is aggregated at the hourly level - we recommend polling this endpoint at most once per hour. Rate limited to 20 requests per minute per team. See [best practices](/docs/api#best-practices).

#### Parameters

`startDate` number Required
Start date in epoch milliseconds
`endDate` number Required
End date in epoch milliseconds
Date range cannot exceed 30 days. Make multiple requests for longer periods.

```
curl -X POST https://api.cursor.com/teams/daily-usage-data \
  -u YOUR_API_KEY: \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": 1710720000000,
    "endDate": 1710892800000
  }'
```

Response:

```
{
  "data": [
    {
      "date": 1710720000000,
      "isActive": true,
      "totalLinesAdded": 1543,
      "totalLinesDeleted": 892,
      "acceptedLinesAdded": 1102,
      "acceptedLinesDeleted": 645,
      "totalApplies": 87,
      "totalAccepts": 73,
      "totalRejects": 14,
      "totalTabsShown": 342,
      "totalTabsAccepted": 289,
      "composerRequests": 45,
      "chatRequests": 128,
      "agentRequests": 12,
      "cmdkUsages": 67,
      "subscriptionIncludedReqs": 180,
      "apiKeyReqs": 0,
      "usageBasedReqs": 5,
      "bugbotUsages": 3,
      "mostUsedModel": "gpt-5",
      "applyMostUsedExtension": ".tsx",
      "tabMostUsedExtension": ".ts",
      "clientVersion": "0.25.1",
      "email": "developer@company.com"
    },
    {
      "date": 1710806400000,
      "isActive": true,
      "totalLinesAdded": 2104,
      "totalLinesDeleted": 1203,
      "acceptedLinesAdded": 1876,
      "acceptedLinesDeleted": 987,
      "totalApplies": 102,
      "totalAccepts": 91,
      "totalRejects": 11,
      "totalTabsShown": 456,
      "totalTabsAccepted": 398,
      "composerRequests": 67,
      "chatRequests": 156,
      "agentRequests": 23,
      "cmdkUsages": 89,
      "subscriptionIncludedReqs": 320,
      "apiKeyReqs": 15,
      "usageBasedReqs": 0,
      "bugbotUsages": 5,
      "mostUsedModel": "claude-3-opus",
      "applyMostUsedExtension": ".py",
      "tabMostUsedExtension": ".py",
      "clientVersion": "0.25.1",
      "email": "developer@company.com"
    }
  ],
  "period": {
    "startDate": 1710720000000,
    "endDate": 1710892800000
  }
}
```

### Get Spending Data
POST`/teams/spend`
Retrieve spending information for the current calendar month with search, sorting, and pagination.

#### Parameters

`searchTerm` string
Search in user names and emails
`sortBy` string
Sort by: `amount`, `date`, `user`. Default: `date`
`sortDirection` string
Sort direction: `asc`, `desc`. Default: `desc`
`page` number
Page number (1-indexed). Default: `1`
`pageSize` number
Results per page
```
curl -X POST https://api.cursor.com/teams/spend \
  -u YOUR_API_KEY: \
  -H "Content-Type: application/json" \
  -d '{
    "searchTerm": "alex@company.com",
    "page": 2,
    "pageSize": 25
  }'
```

Response:

```
{
  "teamMemberSpend": [
    {
      "spendCents": 2450,
      "fastPremiumRequests": 1250,
      "name": "Alex",
      "email": "developer@company.com",
      "role": "member",
      "hardLimitOverrideDollars": 100
    },
    {
      "spendCents": 1875,
      "fastPremiumRequests": 980,
      "name": "Sam",
      "email": "admin@company.com",
      "role": "owner",
      "hardLimitOverrideDollars": 0
    }
  ],
  "subscriptionCycleStart": 1708992000000,
  "totalMembers": 15,
  "totalPages": 1
}
```

### Get Usage Events Data
POST`/teams/filtered-usage-events`
Retrieve detailed usage events for your team with comprehensive filtering, search, and pagination options. This endpoint provides granular insights into individual API calls, model usage, token consumption, and costs. Data is aggregated at the hourly level - we recommend polling this endpoint at most once per hour. Rate limited to 20 requests per minute per team. See [best practices](/docs/api#best-practices).

#### Parameters

`startDate` number
Start date in epoch milliseconds
`endDate` number
End date in epoch milliseconds
`userId` number
Filter by specific user ID
`page` number
Page number (1-indexed). Default: `1`
`pageSize` number
Number of results per page. Default: `10`
`email` string
Filter by user email address
```
curl -X POST https://api.cursor.com/teams/filtered-usage-events \
  -u YOUR_API_KEY: \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": 1748411762359,
    "endDate": 1751003762359,
    "email": "developer@company.com",
    "page": 1,
    "pageSize": 25
  }'
```

Response:

```
{
  "totalUsageEventsCount": 113,
  "pagination": {
    "numPages": 12,
    "currentPage": 1,
    "pageSize": 10,
    "hasNextPage": true,
    "hasPreviousPage": false
  },
  "usageEvents": [
    {
      "timestamp": "1750979225854",
      "model": "claude-4-opus",
      "kind": "Usage-based",
      "maxMode": true,
      "requestsCosts": 5,
      "isTokenBasedCall": true,
      "tokenUsage": {
        "inputTokens": 126,
        "outputTokens": 450,
        "cacheWriteTokens": 6112,
        "cacheReadTokens": 11964,
        "totalCents": 20.18232
      },
      "isFreeBugbot": false,
      "userEmail": "developer@company.com"
    },
    {
      "timestamp": "1750979173824",
      "model": "claude-4-opus",
      "kind": "Usage-based",
      "maxMode": true,
      "requestsCosts": 10,
      "isTokenBasedCall": true,
      "tokenUsage": {
        "inputTokens": 5805,
        "outputTokens": 311,
        "cacheWriteTokens": 11964,
        "cacheReadTokens": 0,
        "totalCents": 40.16699999999999
      },
      "isFreeBugbot": false,
      "userEmail": "developer@company.com"
    },
    {
      "timestamp": "1750978339901",
      "model": "claude-4-sonnet-thinking",
      "kind": "Included in Business",
      "maxMode": true,
      "requestsCosts": 1.4,
      "isTokenBasedCall": false,
      "isFreeBugbot": false,
      "userEmail": "admin@company.com"
    }
  ],
  "period": {
    "startDate": 1748411762359,
    "endDate": 1751003762359
  }
}
```

### Set User Spend Limit
POST`/teams/user-spend-limit`
Set spending limits for individual team members. This allows you to control how much each user can spend on AI usage within your team. Rate limited to 60 requests per minute per team. See [rate limits](/docs/api#rate-limits).

#### Parameters

`userEmail` string Required
Email address of the team member
`spendLimitDollars` number | null Required
Spending limit in dollars (integer only, no decimals). Set to `null` to remove the limit.
The user must already be a member of your team
Only integer values are accepted (no decimal amounts)
Setting `spendLimitDollars` to 0 will set the limit to $0
Setting `spendLimitDollars` to `null` will clear/remove the limit entirely

```
curl -X POST https://api.cursor.com/teams/user-spend-limit \
  -u YOUR_API_KEY: \
  -H "Content-Type: application/json" \
  -d '{
    "userEmail": "developer@company.com",
    "spendLimitDollars": 100
  }'
```

Successful response:

```
{
  "outcome": "success",
  "message": "Spend limit set to $100 for user developer@company.com"
}
```

Error response:

```
{
  "outcome": "error",
  "message": "Invalid email format"
}
```

### Get Team Repo Blocklists
GET`/settings/repo-blocklists/repos`
Retrieve all repository blocklists configured for your team. Add repositories and use patterns to prevent files or directories from being indexed or used as context.

#### Pattern Examples

Common blocklist patterns:

`*` - Block entire repository
`*.env` - Block all .env files
`config/*` - Block all files in config directory
`**/*.secret` - Block all .secret files in any subdirectory
`src/api/keys.ts` - Block specific file

```
curl -X GET https://api.cursor.com/settings/repo-blocklists/repos \
  -u YOUR_API_KEY:
```

Response:

```
{
  "repos": [
    {
      "id": "repo_123",
      "url": "https://github.com/company/sensitive-repo",
      "patterns": ["*.env", "config/*", "secrets/**"]
    },
    {
      "id": "repo_456",
      "url": "https://github.com/company/internal-tools",
      "patterns": ["*"]
    }
  ]
}
```

### Upsert Repo Blocklists
POST`/settings/repo-blocklists/repos/upsert`
Replace existing repository blocklists for the provided repos. This endpoint will only overwrite the patterns for the repositories provided. All other repos will be unaffected.

#### Parameters

`repos` array Required

Array of repository blocklist objects. Each repository object must contain:

`url` string - Repository URL to blocklist
`patterns` string[] - Array of file patterns to block (glob patterns supported)

```
curl -X POST https://api.cursor.com/settings/repo-blocklists/repos/upsert \
  -u YOUR_API_KEY: \
  -H "Content-Type: application/json" \
  -d '{
    "repos": [
      {
        "url": "https://github.com/company/sensitive-repo",
        "patterns": ["*.env", "config/*", "secrets/**"]
      },
      {
        "url": "https://github.com/company/internal-tools",
        "patterns": ["*"]
      }
    ]
  }'
```

Response:

```
{
  "repos": [
    {
      "id": "repo_123",
      "url": "https://github.com/company/sensitive-repo",
      "patterns": ["*.env", "config/*", "secrets/**"]
    },
    {
      "id": "repo_456",
      "url": "https://github.com/company/internal-tools",
      "patterns": ["*"]
    }
  ]
}
```

### Delete Repo Blocklist
DELETE`/settings/repo-blocklists/repos/:repoId`
Remove a specific repository from the blocklist. Returns 204 No Content on successful deletion.

#### Parameters

`repoId` string Required
ID of the repository blocklist to delete
```
curl -X DELETE https://api.cursor.com/settings/repo-blocklists/repos/repo_123 \
  -u YOUR_API_KEY:
```

Response:

```
204 No Content
```