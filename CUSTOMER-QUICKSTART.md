# Customer quick start

Use this after [CUSTOMER-AUDIT-GUIDE.md](CUSTOMER-AUDIT-GUIDE.md). The guide is the explanation. This page is the setup sequence.

1. Agree which six audit questions the customer must answer, and copy [templates/audit-evidence-index.csv](templates/audit-evidence-index.csv).
2. Read [PRODUCTION-GATES.md](PRODUCTION-GATES.md) and [SECURITY.md](SECURITY.md).
3. Create a test tenant or an isolated test subscription. Do not start in production.
4. Copy [config/customer.template.json](config/customer.template.json) to a location that is not committed.
5. Replace placeholders:

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

6. Grant permissions from [config/permissions-matrix.json](config/permissions-matrix.json). Delegated and application grants are different. `Agent365.Observability.OtelWrite` is delegated; the S2S exporter route is the alternative for a registered agent instance.
7. Run the offline demo to learn the control flow: `python examples/offline_demo.py`.
8. Follow [checklists/tenant-configuration-checklist.md](checklists/tenant-configuration-checklist.md).
9. For one correlation ID, export the Entra, Purview, and Defender or Sentinel records named in the audit guide. Put each export on its own evidence-index row.
10. Replace synthetic evidence using [REPLACE-SYNTHETIC-EVIDENCE.md](REPLACE-SYNTHETIC-EVIDENCE.md). A second person reviews the hash and the pass criteria.

Optional tenant packages. They are not installed by the offline demo, and importing one is not a production sign-off:

```bash
pip install -r requirements-tenant.txt
```

Deploy Azure resources only after changing `deployResources` to true in a reviewed parameter file. The templates default that switch to false.
