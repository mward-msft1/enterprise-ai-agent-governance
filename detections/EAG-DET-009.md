# EAG-DET-009 High-severity Defender alerts

- Priority: P1
- Surface: defender-hunting
- Required tables: AlertInfo
- Required columns: Timestamp, AlertId, Title, Category, Severity, ServiceSource, DetectionSource, AttackTechniques
- Required permissions: ['Defender XDR advanced hunting; service data access depends on deployed Defender products and RBAC']
- Schema source: https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertinfo-table
- Schema review date: 2026-11-05

## KQL

```kql
AlertInfo
| where Timestamp > ago(1d)
| where Severity =~ "High"
| project Timestamp, AlertId, Title, Category, Severity, ServiceSource, DetectionSource, AttackTechniques
```

## Expected results

High-severity alerts from Defender services and, when onboarded, Sentinel alerts in the Defender portal.

## False positives

Known pentest windows and noisy policies that the SOC has already accepted.

## Investigation steps

Join AlertEvidence on AlertId in the Defender portal to list entities. This query does not join AlertEvidence so it stays on verified AlertInfo columns.

## Remediation guidance

Follow the product incident queue. Contain only confirmed entities. Record the AlertId in the evidence manifest.

Do not enable this detection in production until a tenant test confirms the table and columns.
