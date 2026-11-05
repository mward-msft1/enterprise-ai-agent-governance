# Source register

Reviewed 2026-11-05 against Microsoft Learn. Re-verify before production. Page content can change, and beta or preview surfaces are not a production commitment.

| Topic | Source | What this repository relies on |
| --- | --- | --- |
| Protection scope compute | https://learn.microsoft.com/en-us/graph/api/userprotectionscopecontainer-compute | `POST /users/{userId}/dataSecurityAndGovernance/protectionScopes/compute`; `ProtectionScopes.Compute.User` and `.All`; delegated and application; `/me` is delegated only |
| processContent | https://learn.microsoft.com/en-us/graph/api/userdatasecurityandgovernance-processcontent | `Content.Process.User` and `.All`; response fields `protectionScopeState`, `policyActions`, `processingErrors`; AI agent `aiAgentInfo` |
| contentActivities | https://learn.microsoft.com/en-us/graph/api/activitiescontainer-post-contentactivities | `ContentActivity.Write` for delegated and application; `201 Created` |
| Package inventory | Microsoft Learn list-packages reference reviewed 2026-11-05 | `GET /copilot/admin/catalog/packages`; `CopilotPackages.Read.All` for delegated and application; Agent 365 license; global service in the reviewed cloud matrix |
| Agent 365 SDK | https://learn.microsoft.com/en-us/microsoft-agent-365/developer/agent-365-sdk | SDK extends an agent; it does not build one |
| OpenTelemetry Distro | https://learn.microsoft.com/en-us/microsoft-agent-365/developer/microsoft-opentelemetry | Python package `microsoft-opentelemetry`; `use_microsoft_opentelemetry`; delegated `Agent365.Observability.OtelWrite`; S2S alternative |
| Agent Framework | https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/openai | `agent_framework.Agent` and `agent_framework.openai.OpenAIChatClient` |
| CloudAppEvents | https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-cloudappevents-table | Columns used by EAG-DET-007 and EAG-DET-008, including `IsAnonymousProxy` and `OAuthAppId` |
| AlertInfo | https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertinfo-table | Columns used by EAG-DET-009. Join to AlertEvidence is investigation guidance, not part of the saved query |
| AuditLogs | https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs | Sentinel columns for EAG-DET-001 and EAG-DET-003. Operation names must be confirmed with `distinct OperationName` |
| SigninLogs | https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs | Sentinel columns for EAG-DET-002 |
| MicrosoftGraphActivityLogs | https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/microsoftgraphactivitylogs | Columns for EAG-DET-006. Confirm with `getschema` |
| AgentGovernance_CL | [deploy/agent-governance-table.json](deploy/agent-governance-table.json) | Custom table owned by this repository, not a Microsoft table |

## Not verified in a tenant

No Graph, Purview, Entra, Agent 365, Azure OpenAI, Application Insights, Defender, or Sentinel call was executed while creating this repository. Schema pages were read. Workspace schemas were not.

## Inspiration boundary

Architectural themes such as a control catalog, detection library, and customer checklist are common to governance reference repositories, including judeper/FSI-AgentGov-Solutions. No file from that repository was copied.
