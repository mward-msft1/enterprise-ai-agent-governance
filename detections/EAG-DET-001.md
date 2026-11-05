# EAG-DET-001 Agent permission changes

- Priority: P1
- Surface: sentinel
- Required tables: AuditLogs
- Required columns: TimeGenerated, OperationName, Category, Result, Identity, InitiatedBy, TargetResources, CorrelationId
- Required permissions: ['Microsoft Sentinel Reader or Log Analytics Reader on the workspace']
- Schema source: https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs
- Schema review date: 2026-11-05

## KQL

```kql
AuditLogs
| where TimeGenerated > ago(1d)
| where Category == "ApplicationManagement"
| where OperationName has "permission" or OperationName has "role assignment" or OperationName has "Consent to application"
| project TimeGenerated, OperationName, Category, Result, Identity, InitiatedBy, TargetResources, CorrelationId
```

## Expected results

Rows only when an Entra application-management audit records a permission, role-assignment, or consent change in the lookback window.

## False positives

Planned admin consent, package deployment, and break-glass access reviews.

## Investigation steps

Open the audit event, identify InitiatedBy, compare TargetResources with the approved agent application ID, and confirm a change ticket.

## Remediation guidance

Remove unapproved permission grants, rotate credentials if consent was unexpected, and require admin-consent workflow for agent apps.

Do not enable this detection in production until a tenant test confirms the table and columns.
