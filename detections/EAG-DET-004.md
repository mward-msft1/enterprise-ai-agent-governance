# EAG-DET-004 Agent policy denials

- Priority: P2
- Surface: sentinel-custom
- Required tables: AgentGovernance_CL
- Required columns: TimeGenerated, CorrelationId, AgentId, Stage, Decision, UserId, Allowed
- Required permissions: ['Log Analytics Reader on the workspace that hosts the custom table']
- Schema source: deploy/agent-governance-table.json
- Schema review date: 2026-11-05

## KQL

```kql
AgentGovernance_CL
| where TimeGenerated > ago(1d)
| where Allowed == false and Stage in ("prompt", "response")
| project TimeGenerated, CorrelationId, AgentId, Stage, Decision, UserId, Allowed
```

## Expected results

Custom-table rows emitted by this reference app when Purview or the synthetic policy engine denies a prompt or response.

## False positives

Policy tests, red-team exercises, and synthetic dry runs if they are ingested into the production workspace.

## Investigation steps

Use CorrelationId to retrieve the local workflow record. Do not copy raw prompt text into the ticket.

## Remediation guidance

Tune the Purview policy if the denial is expected business content, or block the user/tool path if it is not.

Do not enable this detection in production until a tenant test confirms the table and columns.
