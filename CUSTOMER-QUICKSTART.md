# Customer quick start

1. Read [PRODUCTION-GATES.md](PRODUCTION-GATES.md) and [SECURITY.md](SECURITY.md).
2. Create a test tenant or an isolated test subscription. Do not start in production.
3. Copy [config/customer.template.json](config/customer.template.json) to a location that is not committed.
4. Replace placeholders:

| Placeholder | Value |
| --- | --- |
| `REPLACE_WITH_TENANT_ID` | Entra tenant ID |
| `REPLACE_WITH_CLIENT_ID` | Application client ID |
| `REPLACE_WITH_APPLICATION_ID` | Application object or configured location ID used by Purview |
| `REPLACE_WITH_AGENT_ID` | Agent instance ID |
| `REPLACE_WITH_AGENT_BLUEPRINT_ID` | Agent blueprint ID |
| `REPLACE_WITH_AGENT_DISPLAY_NAME` | Agent display name |
| `REPLACE_WITH_AZURE_SUBSCRIPTION_ID` | Azure subscription |
| `REPLACE_WITH_RESOURCE_GROUP` | Resource group |
| `REPLACE_WITH_AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `REPLACE_WITH_MODEL_DEPLOYMENT` | Model deployment name |
| `REPLACE_WITH_AZURE_OPENAI_API_KEY` | Secret-store reference only |
| `REPLACE_WITH_APPINSIGHTS_CONNECTION_STRING` | Secret-store reference only |
| `REPLACE_WITH_SENTINEL_WORKSPACE_NAME` | Log Analytics workspace name |
| `REPLACE_WITH_SENTINEL_WORKSPACE_ID` | Workspace customer ID |

5. Grant permissions from [config/permissions-matrix.json](config/permissions-matrix.json). Delegated and application grants are different. `Agent365.Observability.OtelWrite` is delegated; the S2S exporter route is the alternative for a registered agent instance.
6. Run the offline demo to learn the control flow: `python examples/offline_demo.py`.
7. Follow [checklists/tenant-configuration-checklist.md](checklists/tenant-configuration-checklist.md).
8. Replace synthetic evidence using [REPLACE-SYNTHETIC-EVIDENCE.md](REPLACE-SYNTHETIC-EVIDENCE.md).

Optional tenant packages, not installed or integration-tested in the authoring environment:

```bash
pip install -r requirements-tenant.txt
```

Deploy Azure resources only after changing `deployResources` to true in a reviewed parameter file. The templates default that switch to false.
