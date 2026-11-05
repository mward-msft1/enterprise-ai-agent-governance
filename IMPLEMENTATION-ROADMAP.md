# Implementation roadmap

Complete the phases in order. A later phase does not make an earlier untested integration production-ready.

## Phase 0 — Local review

1. Read [PRODUCTION-GATES.md](PRODUCTION-GATES.md).
2. Run `python -m unittest discover -s tests -v`.
3. Run `python examples/offline_demo.py`.
4. Confirm synthetic evidence is labeled `SYNTHETIC`.

Exit: local tests pass. This is not tenant validation.

## Phase 1 — Identity

1. Create the Entra app registration.
2. Create the Agent 365 blueprint and agent instance.
3. Record tenant, client, application, blueprint, and agent IDs outside git.
4. Grant delegated and application permissions from the matrix separately.
5. Complete CFG-001 through CFG-007.

Exit: redacted evidence replaces the synthetic files for those items.

## Phase 2 — Purview

1. Confirm Purview data security and governance policies cover the agent application location.
2. Call protectionScopes/compute and cache the ETag.
3. Evaluate a synthetic prompt and response with processContent.
4. Record contentActivities without raw content.
5. Confirm a block stops the model call.

Exit: CFG-008 through CFG-011 have reviewer-approved tenant evidence.

## Phase 3 — Model, tools, and telemetry

1. Install `agent-framework` and `agent-framework-openai` in the tenant environment.
2. Point Azure OpenAI at the approved deployment.
3. Install `microsoft-opentelemetry` and choose delegated or S2S export.
4. Deploy Application Insights only after accepting the billable template.
5. Exercise the MCP allowlist.

Exit: CFG-012 through CFG-016 pass. Export failures are not recorded as success.

## Phase 4 — Detection

1. Run `getschema` for SigninLogs, AuditLogs, and MicrosoftGraphActivityLogs.
2. Run the Defender hunting queries and confirm CloudAppEvents and AlertInfo columns.
3. Create `AgentGovernance_CL` from [deploy/agent-governance-table.json](deploy/agent-governance-table.json).
4. Enable analytics rules only after schema confirmation. The ARM template defaults `deployRules` to false and each rule to disabled.

Exit: CFG-018 and CFG-019 pass.

## Phase 5 — Production gate

1. Replace every synthetic evidence file using [REPLACE-SYNTHETIC-EVIDENCE.md](REPLACE-SYNTHETIC-EVIDENCE.md).
2. Obtain reviewer approval.
3. Do not claim regulatory compliance from [CONTROL-CATALOG.md](CONTROL-CATALOG.md).
