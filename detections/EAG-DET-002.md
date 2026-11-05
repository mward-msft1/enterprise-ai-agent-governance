# EAG-DET-002 Suspicious authentication

- Priority: P1
- Surface: sentinel
- Required tables: SigninLogs
- Required columns: TimeGenerated, UserPrincipalName, AppId, AppDisplayName, IPAddress, ResultType, RiskLevelDuringSignIn, ConditionalAccessStatus, Location, CorrelationId
- Required permissions: ['Microsoft Sentinel Reader or Log Analytics Reader']
- Schema source: https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
- Schema review date: 2026-11-05

## KQL

```kql
SigninLogs
| where TimeGenerated > ago(1d)
| where AppId == "REPLACE_WITH_APPLICATION_ID"
| where ResultType != 0 or RiskLevelDuringSignIn has "high" or ConditionalAccessStatus == "failure"
| project TimeGenerated, UserPrincipalName, AppId, AppDisplayName, IPAddress, ResultType, RiskLevelDuringSignIn, ConditionalAccessStatus, Location, CorrelationId
```

## Expected results

Failed, high-risk, or Conditional Access failure sign-ins to the agent application.

## False positives

Users who have not registered MFA, conditional-access report-only experiments, and lab tenants.

## Investigation steps

Correlate ResultType, IPAddress, and Location with the user's normal pattern. Do not disable the account from this query alone.

## Remediation guidance

Require MFA or a compliant device, revoke sessions if risk is confirmed, and review the app's audience.

Do not enable this detection in production until a tenant test confirms the table and columns.
