# EAG-DET-003 Application credential changes

- Priority: P1
- Surface: sentinel
- Required tables: AuditLogs
- Required columns: TimeGenerated, OperationName, Result, Identity, InitiatedBy, TargetResources, CorrelationId
- Required permissions: ['Microsoft Sentinel Reader or Log Analytics Reader']
- Schema source: https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs
- Schema review date: 2026-11-05

## KQL

```kql
AuditLogs
| where TimeGenerated > ago(1d)
| where OperationName has "credential" or OperationName has "Certificates and secrets"
| project TimeGenerated, OperationName, Result, Identity, InitiatedBy, TargetResources, CorrelationId
```

## Expected results

Audit events that add, update, or remove application or service-principal credentials.

## False positives

Scheduled certificate rotation performed by the approved automation identity.

## Investigation steps

Confirm the initiator, credential type, expiry, and whether the target application ID matches the agent registration.

## Remediation guidance

Remove unexpected credentials, rotate dependent secrets, and restrict who can update application certificates.

Do not enable this detection in production until a tenant test confirms the table and columns.
