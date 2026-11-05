# Production gates

All gates are required. A local unit-test pass does not satisfy a tenant gate.

| Gate | Evidence | Blocker if missing |
| --- | --- | --- |
| G0 Local tests pass | CI log | Workflow regression |
| G1 No placeholders in the tenant secret store | Secret-store reference, not the secret | Accidental call with template values |
| G2 Delegated and application grants match the matrix | Entra export with secrets removed | Wrong permission type |
| G3 Purview block prevents model and tool execution | Tenant trace of a denied prompt | Fail-open policy path |
| G4 contentActivities body has no raw content | Request capture with text redacted | Prompt leakage into audit |
| G5 Agent Framework package and Azure OpenAI tested | One authorized completion metadata record | Untested model path |
| G6 OpenTelemetry reaches the selected backend or the failure is explicit | Exporter result | Silent telemetry loss |
| G7 Defender and Sentinel schemas confirmed | `getschema` or hunting column list | Invalid analytics rule |
| G8 Custom table exists before custom detections are enabled | Table schema | Rules that cannot run |
| G9 APIM policy rejects missing tokens and contains no secret | Gateway trace | Unauthenticated backend |
| G10 Synthetic evidence replaced and reviewed | Signed manifest | Synthetic data presented as customer results |
| G11 Compliance owner accepts residual risk | Written acceptance | Implied regulatory compliance |

Until G1–G11 are complete, describe this repository as a reference implementation, not a production deployment.
