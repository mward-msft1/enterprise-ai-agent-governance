# Enterprise AI agent governance

## What this is

This is a reference implementation for governing a custom Microsoft AI agent. Run it locally, review the control path, and adapt the patterns in an authorized test tenant. It is not a production service, and installing it does not make an organization compliant with NIST, ISO, SOC 2, HIPAA, GDPR, PCI DSS, SOX, or GLBA.

Use it to see, test, and adapt one control path:

1. Identify the agent and the user.
2. Check Microsoft Purview before the model runs.
3. Run the model only if policy allows it.
4. Call only allowlisted tools.
5. Check the response before returning it.
6. Record an audit event and telemetry.
7. Hand the correlation ID to Defender or Sentinel for investigation.

The runnable sample is a Python application in `src/eagov`. The rest of the repository is the surrounding kit: a permissions matrix, KQL detections, Azure deployment examples, a tenant checklist, and labeled synthetic evidence.

It has two modes:

| Mode | What you get | What it is not |
| --- | --- | --- |
| Offline synthetic | A full local run with fake users, fake policy decisions, and fake evidence | Proof that your tenant is configured |
| Authorized test tenant | Request builders for Graph, Purview, Entra, Agent 365, and OpenTelemetry | Production-ready until you replace placeholders and complete tenant tests |

This repository is original work. It uses [judeper/FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) as architectural inspiration only. It is not a fork, and it does not copy that repository's code.

## How to use it

Start locally. Do not connect a tenant until the offline path makes sense.

### 1. Run the sample on your machine

You need Python 3.10 or later. No packages are required for the offline demo. From the repository root:

macOS or Linux:

```bash
export PYTHONPATH=src
python -m unittest discover -s tests -v
python examples/offline_demo.py
python -m eagov.cli --mode offline --prompt "Summarize the public status page."
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python examples/offline_demo.py
python -m eagov.cli --mode offline --prompt "Summarize the public status page."
```

`examples/offline_demo.py` adds `src` to the path for you. The CLI does not, so set `PYTHONPATH` before `python -m eagov.cli`. An allowed run exits 0. A denied run exits 1 and prints `status=` on standard error.

The demo prints two outcomes: an allowed request, and a request denied because it contains `SYNTHETIC_BLOCK_TOKEN`. Both results are synthetic. They are not customer evidence.

Try a denied tool, then a response-policy denial:

```bash
python -m eagov.cli --mode offline --tool shell_exec
python -m eagov.cli --mode offline --prompt "SYNTHETIC_RESPONSE_BLOCK"
```

`shell_exec` is not on the allowlist, so the gateway rejects it before the tool runs.

### 2. Read the control path before changing it

| If you want to... | Start here |
| --- | --- |
| Understand the design | [ARCHITECTURE.md](ARCHITECTURE.md) |
| See the enforced order of checks | `src/eagov/workflow.py` |
| See which Graph permissions are delegated vs application | [config/permissions-matrix.md](config/permissions-matrix.md) |
| Review detections | `detections/` |
| Plan a tenant rollout | [IMPLEMENTATION-ROADMAP.md](IMPLEMENTATION-ROADMAP.md) and [CUSTOMER-QUICKSTART.md](CUSTOMER-QUICKSTART.md) |
| Decide whether it can go to production | [PRODUCTION-GATES.md](PRODUCTION-GATES.md) |

### 3. Prepare an authorized test tenant

Copy [config/customer.template.json](config/customer.template.json) to a file that is not committed, or store the values in a secret store. Replace every `REPLACE_WITH_*` value, including tenant ID, client ID, application ID, agent identity, Azure subscription, resource group, Azure OpenAI endpoint, model deployment, Application Insights connection string, and Sentinel workspace.

Then confirm the gate refuses to call Microsoft while placeholders remain:

```powershell
python examples/tenant_demo.py
```

That command must exit without calling Graph. Only after the placeholders are gone should you grant the permissions in the matrix and follow [checklists/tenant-configuration-checklist.md](checklists/tenant-configuration-checklist.md).

Optional tenant packages are listed in `requirements-tenant.txt`. They were not installed or integration-tested when this repository was created. Do not treat an import as a production sign-off.

### 4. Replace the synthetic evidence

`evidence/synthetic` and `TENANT-TEST-RESULTS.md` are packaging examples. Follow [REPLACE-SYNTHETIC-EVIDENCE.md](REPLACE-SYNTHETIC-EVIDENCE.md) before anyone describes a control as tested in a tenant.

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
- [config/permissions-matrix.md](config/permissions-matrix.md)
