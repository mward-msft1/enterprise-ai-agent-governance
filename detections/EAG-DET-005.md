# EAG-DET-005 Unusual tool execution

- Priority: P2
- Surface: sentinel-custom
- Required tables: AgentGovernance_CL
- Required columns: TimeGenerated, AgentId, ToolName, UserId, Stage
- Required permissions: ['Log Analytics Reader']
- Schema source: deploy/agent-governance-table.json
- Schema review date: 2026-11-05

## KQL

```kql
AgentGovernance_CL
| where TimeGenerated > ago(1d)
| where Stage == "tool"
| where ToolName !in ("knowledge_lookup", "policy_status")
| summarize ToolCalls = count() by AgentId, ToolName, UserId, bin(TimeGenerated, 1h)
| where ToolCalls > 0
```

## Expected results

Tool names outside the customer allowlist.

## False positives

A newly approved tool that has not been added to the query allowlist.

## Investigation steps

Compare ToolName with config tools.allowlist and the MCP gateway log for the same correlation ID.

## Remediation guidance

Remove the tool from the agent, rotate MCP credentials, and update the allowlist only through change control.

Do not enable this detection in production until a tenant test confirms the table and columns.
