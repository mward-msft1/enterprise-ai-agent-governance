# Tenant configuration checklist

Status values in this file are not tenant results. Complete them in an authorized test tenant.
Implementing a row does not by itself establish regulatory compliance.

| Item | Requirement | Required permissions | Status |
| --- | --- | --- | --- |
| CFG-001 | Record the Entra tenant ID | Tenant reader | Not started — tenant validation required |
| CFG-002 | Register the agent application | Application Administrator | Not started — tenant validation required |
| CFG-003 | Create a distinct agent identity | Agent 365 administrator | Not started — tenant validation required |
| CFG-004 | Grant delegated permissions and admin consent | Privileged Role Administrator | Not started — tenant validation required |
| CFG-005 | Grant application permissions only where supported | Privileged Role Administrator | Not started — tenant validation required |
| CFG-006 | Validate delegated user authentication | Identity tester | Not started — tenant validation required |
| CFG-007 | Validate application authentication separately | Identity tester | Not started — tenant validation required |
| CFG-008 | Compute Purview protection scopes | Compliance administrator | Not started — tenant validation required |
| CFG-009 | Evaluate a prompt with processContent | Compliance administrator | Not started — tenant validation required |
| CFG-010 | Evaluate the model response with processContent | Compliance administrator | Not started — tenant validation required |
| CFG-011 | Record contentActivities | Compliance administrator | Not started — tenant validation required |
| CFG-012 | Configure Azure OpenAI and Agent Framework | Azure OpenAI user | Not started — tenant validation required |
| CFG-013 | Enforce the tool allowlist | Agent owner | Not started — tenant validation required |
| CFG-014 | Register the MCP server | Agent owner | Not started — tenant validation required |
| CFG-015 | Configure Microsoft OpenTelemetry for Agent 365 | Agent 365 administrator | Not started — tenant validation required |
| CFG-016 | Configure Application Insights | Monitoring contributor | Not started — tenant validation required |
| CFG-017 | Deploy the APIM policy in a non-production gateway | API Management operator | Not started — tenant validation required |
| CFG-018 | Confirm Defender advanced hunting access | Security reader | Not started — tenant validation required |
| CFG-019 | Confirm Sentinel workspace and analytics rules | Sentinel contributor | Not started — tenant validation required |
| CFG-020 | Replace synthetic evidence | Control owner and reviewer | Not started — tenant validation required |
| CFG-021 | Inventory packages with CopilotPackages.Read.All | Agent 365 administrator | Not started — tenant validation required |
| CFG-022 | Keep secrets out of the repository | Security reviewer | Not started — tenant validation required |

Full procedures, pass criteria, fail criteria, and expected evidence are in `tenant-configuration-checklist.csv`.

