# EAG-DET-008 Anonymous proxy activity

- Priority: P1
- Surface: defender-hunting
- Required tables: CloudAppEvents
- Required columns: Timestamp, ActionType, Application, OAuthAppId, AccountObjectId, IPAddress, IsAnonymousProxy, CountryCode, City, Isp, ReportId
- Required permissions: ['Defender XDR advanced hunting']
- Schema source: https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-cloudappevents-table
- Schema review date: 2026-11-05

## KQL

```kql
CloudAppEvents
| where Timestamp > ago(1d)
| where IsAnonymousProxy == true
| where OAuthAppId == "REPLACE_WITH_APPLICATION_ID" or Application has "REPLACE_WITH_AGENT_DISPLAY_NAME"
| project Timestamp, ActionType, Application, OAuthAppId, AccountObjectId, IPAddress, IsAnonymousProxy, CountryCode, City, Isp, ReportId
```

## Expected results

Cloud app events whose client IP is classified as an anonymous proxy.

## False positives

Approved privacy relays and corporate secure web gateways that Defender classifies as proxy.

## Investigation steps

Check Isp, CountryCode, and whether the account is an agent operator. Compare with SigninLogs for the same window.

## Remediation guidance

Block anonymous proxy sign-in with Conditional Access if confirmed. Do not treat the classification as proof of compromise by itself.

Do not enable this detection in production until a tenant test confirms the table and columns.
