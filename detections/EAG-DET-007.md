# EAG-DET-007 Suspicious cloud application activity

- Priority: P2
- Surface: defender-hunting
- Required tables: CloudAppEvents
- Required columns: Timestamp, ActionType, Application, OAuthAppId, AccountObjectId, AccountDisplayName, IsAdminOperation, IPAddress, CountryCode, ReportId
- Required permissions: ['Defender XDR advanced hunting; Defender for Cloud Apps connected']
- Schema source: https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-cloudappevents-table
- Schema review date: 2026-11-05

## KQL

```kql
CloudAppEvents
| where Timestamp > ago(1d)
| where OAuthAppId == "REPLACE_WITH_APPLICATION_ID" or Application has "Copilot"
| where IsAdminOperation == true or ActionType has "Consent"
| project Timestamp, ActionType, Application, OAuthAppId, AccountObjectId, AccountDisplayName, IsAdminOperation, IPAddress, CountryCode, ReportId
```

## Expected results

Admin or consent activity for the agent OAuth app or Copilot-related cloud app events.

## False positives

Security administrator reviews and approved Copilot admin operations.

## Investigation steps

Pivot on ReportId and AccountObjectId. Confirm the OAuth app ID before containment.

## Remediation guidance

Disable the OAuth app or remove consent if the actor is unapproved. Preserve the hunting result as evidence.

Do not enable this detection in production until a tenant test confirms the table and columns.
