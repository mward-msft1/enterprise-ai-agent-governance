# EAG-DET-006 Purview evaluation failures

- Priority: P2
- Surface: sentinel
- Required tables: MicrosoftGraphActivityLogs
- Required columns: TimeGenerated, RequestUri, RequestMethod, ResponseStatusCode, AppId, UserId
- Required permissions: ['Log Analytics Reader; Microsoft Graph activity logs connector enabled']
- Schema source: https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/microsoftgraphactivitylogs
- Schema review date: 2026-11-05

## KQL

```kql
MicrosoftGraphActivityLogs
| where TimeGenerated > ago(1d)
| where RequestUri has "dataSecurityAndGovernance"
| where ResponseStatusCode !in (200, 201, 202, 204)
| project TimeGenerated, RequestUri, RequestMethod, ResponseStatusCode, AppId, UserId
```

## Expected results

Non-success Graph calls to dataSecurityAndGovernance endpoints.

## False positives

Consent propagation delay, throttling (429), and intentional negative tests.

## Investigation steps

Group by ResponseStatusCode and AppId. 401/403 indicates permission or consent failure. 429 indicates throttling.

## Remediation guidance

Restore the least-privileged permission, honor retry-after on 429, and do not bypass processContent on failure.

Do not enable this detection in production until a tenant test confirms the table and columns.
