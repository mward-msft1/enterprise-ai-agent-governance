# Architecture

## Intent

The reference application keeps policy enforcement outside the model. The model and tools run only after identity, authentication, and Purview evaluation succeed. Audit and telemetry run on both allow and deny paths.

```text
Caller
  |
  v
GovernanceWorkflow
  |-- Agent identity (Entra agent ID, blueprint ID, application ID)
  |-- User authentication (delegated) or app-only token (application permissions)
  |-- Agent 365 package inventory (CopilotPackages.Read.All)
  |-- Purview protectionScopes/compute
  |-- Purview processContent (uploadText)
  |-- Microsoft Agent Framework / Azure OpenAI
  |-- MCP allowlist gateway
  |-- Purview processContent (downloadText)
  |-- contentActivities audit (metadata only)
  |-- OpenTelemetry buffer or Microsoft OpenTelemetry Distro
  |-- Defender hunting / Sentinel investigation bundle
```

## Modes

Offline mode uses an in-memory Graph transport and a deterministic model stub. It is for structure, unit tests, and customer walkthroughs.

Tenant mode requires a caller-supplied `GraphClient` and a token provider with `execute=True`. The CLI does not silently call Microsoft. Live model and Agent 365 export adapters report themselves as not validated when their packages are absent.

## Technology boundaries

| Technology | Role in this repository | Tenant-validated here |
| --- | --- | --- |
| Microsoft Agent Framework | Optional import of `agent_framework` and `OpenAIChatClient` | No |
| Microsoft Agent 365 | Inventory and capability map; SDK does not build the agent | No |
| Microsoft Agent 365 SDK | Documented boundary only; not imported | No |
| Microsoft OpenTelemetry Distro | Optional `use_microsoft_opentelemetry` | No |
| Microsoft Purview | Graph data security and governance request builders | No |
| Microsoft Defender XDR | Advanced hunting KQL for CloudAppEvents and AlertInfo | No |
| Microsoft Sentinel | Analytics-rule ARM template, disabled by default | No |
| Microsoft Entra | Token request builders and permission comparison | No |
| Microsoft Graph | Injectable HTTP client | No |
| Azure OpenAI | Endpoint and deployment configuration for Agent Framework | No |
| Azure Monitor / Application Insights | Deployment template and connection-string placeholder | No |
| Azure API Management | JWT, rate-limit, and correlation policy | No |
| MCP | Local JSON-RPC allowlist gateway | Local only |

## Fail-closed rules

- Tenant calls are refused while any `REPLACE_WITH_*` value remains.
- `processingErrors` from processContent deny the stage.
- `restrictAccess` denies the stage. `restrictionAction=block` is the documented block action.
- Tools absent from `tools.allowlist` are not executed.
- Audit bodies do not include raw prompt or response text.
- `production_ready` is always false in workflow results from this version.

## Data sent to Microsoft

In tenant mode, processContent sends the prompt and response text to Microsoft Graph so Purview can evaluate it. That is required for inline evaluation. The contentActivities call in this repository sends metadata only. Customers must confirm that split with their compliance owner before production use.

## Investigation

The workflow does not query Defender or Sentinel. It emits a bundle of detection IDs and query paths keyed by correlation ID. An analyst runs those queries in the authorized portal.
