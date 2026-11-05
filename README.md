# Enterprise AI agent governance

Cross-industry reference implementation for governing a custom Microsoft AI agent. It covers identity, user authentication, Microsoft Purview policy evaluation, Microsoft Agent Framework execution, allowlisted MCP tools, audit, OpenTelemetry, and Defender/Sentinel investigation.

This repository is original work. It uses [judeper/FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) as architectural inspiration only. It is not a fork, and it does not copy that repository's code.

## Status

| Mode | What it does | Production-ready |
| --- | --- | --- |
| Offline synthetic | Runs the full workflow locally with labeled synthetic data | No |
| Authorized test tenant | Builds Microsoft API calls after placeholders are replaced | No, until `TENANT-TEST-RESULTS.md` is completed with real evidence |

Do not treat a passing local test as tenant validation. Do not treat control mappings as a compliance certification.

## Workflow

```text
Agent identity
→ User authentication
→ Purview protection scope computation
→ Prompt policy evaluation
→ Microsoft Agent Framework execution
→ Authorized tool/MCP interaction
→ Response policy evaluation
→ Audit recording
→ Microsoft OpenTelemetry export
→ Defender/Sentinel investigation bundle
```

## Quick start

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python examples/offline_demo.py
python -m eagov.cli --mode offline --prompt "Summarize the public status page."
```

Run commands from the repository root. `PYTHONPATH=src` is required for the CLI.

Tenant mode refuses to run while `REPLACE_WITH_*` values remain:

```bash
python examples/tenant_demo.py
```

## Layout

| Path | Purpose |
| --- | --- |
| `src/eagov` | Executable reference workflow |
| `config` | Customer template and permissions matrix |
| `detections` | Prioritized KQL and Sentinel ARM rules |
| `deploy` | Disabled-by-default Azure templates and APIM policy |
| `checklists` | Tenant configuration checklist |
| `evidence/synthetic` | Labeled synthetic evidence, not customer results |
| `examples` | Offline demo, tenant gate, and MCP server |
| `.github/workflows` | Unit tests and security scanning |

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [IMPLEMENTATION-ROADMAP.md](IMPLEMENTATION-ROADMAP.md)
- [CONTROL-CATALOG.md](CONTROL-CATALOG.md)
- [SOURCE-REGISTER.md](SOURCE-REGISTER.md)
- [CUSTOMER-QUICKSTART.md](CUSTOMER-QUICKSTART.md)
- [PRODUCTION-GATES.md](PRODUCTION-GATES.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [REPLACE-SYNTHETIC-EVIDENCE.md](REPLACE-SYNTHETIC-EVIDENCE.md)
- [SECURITY.md](SECURITY.md)

## Customer configuration

Copy `config/customer.template.json` to a secret-free local file outside git, or to a secret store. Replace every `REPLACE_WITH_*` value. Required values include tenant ID, client ID, application ID, agent identity, Azure subscription, resource group, Azure OpenAI endpoint, model deployment, Application Insights connection string, and Sentinel workspace.

The permissions matrix is in [config/permissions-matrix.json](config/permissions-matrix.json).
