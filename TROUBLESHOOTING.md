# Troubleshooting

## No module named eagov

Set `PYTHONPATH` to the `src` directory before `python -m eagov.cli`. On macOS or Linux use `export PYTHONPATH=src`. In Windows PowerShell use `$env:PYTHONPATH = "src"`. The example scripts add that path themselves.

## Denied run still looks successful

Check the process exit code, not only the JSON. `status=allowed` exits 0. `denied_prompt`, `denied_response`, and `denied_tool` exit 1. The status line is written to standard error.

## Tenant mode exits before any call

`examples/tenant_demo.py` exits when placeholders remain. Replace them in a secret store. Do not remove the check.

## 401 or 403 from Graph

Compare the token type with the route. `/me` requires a delegated token. Application tokens must call `/users/{id}`. Confirm admin consent for the specific permission, not a similarly named permission.

## processContent returns processingErrors

The workflow denies the stage. Do not catch that error and continue to the model. Check the Purview policy location value. It must be the application ID or other location type documented for the policy.

## protectionScopeState is modified

Refresh protection scopes and the cached ETag before the next processContent call. The reference client forwards ETag as `If-None-Match`.

## Agent Framework import fails

Tenant mode reports `TenantNotValidated` when `agent-framework` is not installed. Offline mode still runs. Install the package only in the authorized environment and retest. A successful import is not a production sign-off.

## OpenTelemetry does not appear in Agent 365

Confirm the exporter route. Delegated export needs `Agent365.Observability.OtelWrite` and a token resolver. Blueprint agents from `a365 setup all` need the S2S route unless that delegated permission was granted. The Agent 365 exporter does not use the Application Insights connection string.

## Hunting query fails

CloudAppEvents requires Defender for Cloud Apps data, including Microsoft 365 activities. AlertInfo availability depends on deployed Defender products and RBAC. Sentinel rules use `TimeGenerated`. Defender hunting queries use `Timestamp`. Do not paste one surface's query into the other without checking the schema.

## Custom detection returns no table

`AgentGovernance_CL` is not a Microsoft table. Create it from [deploy/agent-governance-table.json](deploy/agent-governance-table.json) before enabling EAG-DET-004 or EAG-DET-005.

## Analytics rule deployment creates nothing

`deployRules` defaults to false. That is intentional.

## Evidence hash mismatch

Regenerate the hash after any edit. Do not update the manifest hash without updating the reviewer status. Synthetic files must not be relabeled as tenant evidence.
