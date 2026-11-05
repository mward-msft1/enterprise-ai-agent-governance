# Permissions matrix

Reviewed 2026-11-05 from Microsoft Learn. Re-check before consent. Personal Microsoft accounts are not supported for these permissions. Admin consent is required.

`/me` routes need a delegated token. Application permissions must use `/users/{userId}`.

| Permission | Delegated | Application | Higher privileged | API or surface |
| --- | --- | --- | --- | --- |
| CopilotPackages.Read.All | Supported. Least privileged. | Supported. Least privileged. | CopilotPackages.ReadWrite.All | GET /copilot/admin/catalog/packages |
| ProtectionScopes.Compute.User | Supported. Least privileged. | Supported. Least privileged. | ProtectionScopes.Compute.All | POST /users/{userId}/dataSecurityAndGovernance/protectionScopes/compute |
| Content.Process.User | Supported. Least privileged. | Supported. Least privileged. | Content.Process.All | POST /users/{userId}/dataSecurityAndGovernance/processContent |
| ContentActivity.Write | Supported. Least privileged. No higher permission published. | Supported. Least privileged. No higher permission published. | None | POST /users/{userId}/dataSecurityAndGovernance/activities/contentActivities |
| Agent365.Observability.OtelWrite | Supported for the delegated Agent 365 exporter route. Admin consent required. | Not the application permission for this exporter. A registered agent instance can use the service-to-service route without this delegated permission. | None published | Microsoft OpenTelemetry Distro Agent 365 exporter |

Machine-readable copy: [permissions-matrix.json](permissions-matrix.json).
