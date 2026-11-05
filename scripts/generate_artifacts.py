"""Generate detection files, checklist, synthetic evidence, and test-result tables.

Synthetic records are labeled and are not customer results.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KQL = ROOT / "detections" / "kql"
ARM = ROOT / "detections" / "arm"
EVIDENCE = ROOT / "evidence" / "synthetic"

DETECTIONS = [
    {
        "id": "EAG-DET-001",
        "priority": "P1",
        "title": "Agent permission changes",
        "surface": "sentinel",
        "query_file": "detections/kql/EAG-DET-001-agent-permission-changes.kql",
        "tables": ["AuditLogs"],
        "columns": [
            "TimeGenerated",
            "OperationName",
            "Category",
            "Result",
            "Identity",
            "InitiatedBy",
            "TargetResources",
            "CorrelationId",
        ],
        "permissions": ["Microsoft Sentinel Reader or Log Analytics Reader on the workspace"],
        "schema_source": "https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs",
        "query": """AuditLogs
| where TimeGenerated > ago(1d)
| where Category == "ApplicationManagement"
| where OperationName has "permission" or OperationName has "role assignment" or OperationName has "Consent to application"
| project TimeGenerated, OperationName, Category, Result, Identity, InitiatedBy, TargetResources, CorrelationId
""",
        "expected": "Rows only when an Entra application-management audit records a permission, role-assignment, or consent change in the lookback window.",
        "false_positives": "Planned admin consent, package deployment, and break-glass access reviews.",
        "investigation": "Open the audit event, identify InitiatedBy, compare TargetResources with the approved agent application ID, and confirm a change ticket.",
        "remediation": "Remove unapproved permission grants, rotate credentials if consent was unexpected, and require admin-consent workflow for agent apps.",
        "arm": True,
        "severity": "High",
        "tactics": ["Persistence"],
        "techniques": ["T1098"],
    },
    {
        "id": "EAG-DET-002",
        "priority": "P1",
        "title": "Suspicious authentication",
        "surface": "sentinel",
        "query_file": "detections/kql/EAG-DET-002-suspicious-authentication.kql",
        "tables": ["SigninLogs"],
        "columns": [
            "TimeGenerated",
            "UserPrincipalName",
            "AppId",
            "AppDisplayName",
            "IPAddress",
            "ResultType",
            "RiskLevelDuringSignIn",
            "ConditionalAccessStatus",
            "Location",
            "CorrelationId",
        ],
        "permissions": ["Microsoft Sentinel Reader or Log Analytics Reader"],
        "schema_source": "https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs",
        "query": """SigninLogs
| where TimeGenerated > ago(1d)
| where AppId == "REPLACE_WITH_APPLICATION_ID"
| where ResultType != 0 or RiskLevelDuringSignIn has "high" or ConditionalAccessStatus == "failure"
| project TimeGenerated, UserPrincipalName, AppId, AppDisplayName, IPAddress, ResultType, RiskLevelDuringSignIn, ConditionalAccessStatus, Location, CorrelationId
""",
        "expected": "Failed, high-risk, or Conditional Access failure sign-ins to the agent application.",
        "false_positives": "Users who have not registered MFA, conditional-access report-only experiments, and lab tenants.",
        "investigation": "Correlate ResultType, IPAddress, and Location with the user's normal pattern. Do not disable the account from this query alone.",
        "remediation": "Require MFA or a compliant device, revoke sessions if risk is confirmed, and review the app's audience.",
        "arm": True,
        "severity": "High",
        "tactics": ["CredentialAccess"],
        "techniques": ["T1078"],
    },
    {
        "id": "EAG-DET-003",
        "priority": "P1",
        "title": "Application credential changes",
        "surface": "sentinel",
        "query_file": "detections/kql/EAG-DET-003-application-credential-changes.kql",
        "tables": ["AuditLogs"],
        "columns": [
            "TimeGenerated",
            "OperationName",
            "Result",
            "Identity",
            "InitiatedBy",
            "TargetResources",
            "CorrelationId",
        ],
        "permissions": ["Microsoft Sentinel Reader or Log Analytics Reader"],
        "schema_source": "https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs",
        "query": """AuditLogs
| where TimeGenerated > ago(1d)
| where OperationName has "credential" or OperationName has "Certificates and secrets"
| project TimeGenerated, OperationName, Result, Identity, InitiatedBy, TargetResources, CorrelationId
""",
        "expected": "Audit events that add, update, or remove application or service-principal credentials.",
        "false_positives": "Scheduled certificate rotation performed by the approved automation identity.",
        "investigation": "Confirm the initiator, credential type, expiry, and whether the target application ID matches the agent registration.",
        "remediation": "Remove unexpected credentials, rotate dependent secrets, and restrict who can update application certificates.",
        "arm": True,
        "severity": "High",
        "tactics": ["Persistence"],
        "techniques": ["T1098"],
    },
    {
        "id": "EAG-DET-004",
        "priority": "P2",
        "title": "Agent policy denials",
        "surface": "sentinel-custom",
        "query_file": "detections/kql/EAG-DET-004-agent-policy-denials.kql",
        "tables": ["AgentGovernance_CL"],
        "columns": [
            "TimeGenerated",
            "CorrelationId",
            "AgentId",
            "Stage",
            "Decision",
            "UserId",
            "Allowed",
        ],
        "permissions": ["Log Analytics Reader on the workspace that hosts the custom table"],
        "schema_source": "deploy/agent-governance-table.json",
        "query": """AgentGovernance_CL
| where TimeGenerated > ago(1d)
| where Allowed == false and Stage in ("prompt", "response")
| project TimeGenerated, CorrelationId, AgentId, Stage, Decision, UserId, Allowed
""",
        "expected": "Custom-table rows emitted by this reference app when Purview or the synthetic policy engine denies a prompt or response.",
        "false_positives": "Policy tests, red-team exercises, and synthetic dry runs if they are ingested into the production workspace.",
        "investigation": "Use CorrelationId to retrieve the local workflow record. Do not copy raw prompt text into the ticket.",
        "remediation": "Tune the Purview policy if the denial is expected business content, or block the user/tool path if it is not.",
        "arm": True,
        "severity": "Medium",
        "tactics": ["DefenseEvasion"],
        "techniques": ["T1562"],
    },
    {
        "id": "EAG-DET-005",
        "priority": "P2",
        "title": "Unusual tool execution",
        "surface": "sentinel-custom",
        "query_file": "detections/kql/EAG-DET-005-unusual-tool-execution.kql",
        "tables": ["AgentGovernance_CL"],
        "columns": ["TimeGenerated", "AgentId", "ToolName", "UserId", "Stage"],
        "permissions": ["Log Analytics Reader"],
        "schema_source": "deploy/agent-governance-table.json",
        "query": """AgentGovernance_CL
| where TimeGenerated > ago(1d)
| where Stage == "tool"
| where ToolName !in ("knowledge_lookup", "policy_status")
| summarize ToolCalls = count() by AgentId, ToolName, UserId, bin(TimeGenerated, 1h)
| where ToolCalls > 0
""",
        "expected": "Tool names outside the customer allowlist.",
        "false_positives": "A newly approved tool that has not been added to the query allowlist.",
        "investigation": "Compare ToolName with config tools.allowlist and the MCP gateway log for the same correlation ID.",
        "remediation": "Remove the tool from the agent, rotate MCP credentials, and update the allowlist only through change control.",
        "arm": True,
        "severity": "Medium",
        "tactics": ["Execution"],
        "techniques": ["T1059"],
    },
    {
        "id": "EAG-DET-006",
        "priority": "P2",
        "title": "Purview evaluation failures",
        "surface": "sentinel",
        "query_file": "detections/kql/EAG-DET-006-purview-evaluation-failures.kql",
        "tables": ["MicrosoftGraphActivityLogs"],
        "columns": [
            "TimeGenerated",
            "RequestUri",
            "RequestMethod",
            "ResponseStatusCode",
            "AppId",
            "UserId",
        ],
        "permissions": ["Log Analytics Reader; Microsoft Graph activity logs connector enabled"],
        "schema_source": "https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/microsoftgraphactivitylogs",
        "query": """MicrosoftGraphActivityLogs
| where TimeGenerated > ago(1d)
| where RequestUri has "dataSecurityAndGovernance"
| where ResponseStatusCode !in (200, 201, 202, 204)
| project TimeGenerated, RequestUri, RequestMethod, ResponseStatusCode, AppId, UserId
""",
        "expected": "Non-success Graph calls to dataSecurityAndGovernance endpoints.",
        "false_positives": "Consent propagation delay, throttling (429), and intentional negative tests.",
        "investigation": "Group by ResponseStatusCode and AppId. 401/403 indicates permission or consent failure. 429 indicates throttling.",
        "remediation": "Restore the least-privileged permission, honor retry-after on 429, and do not bypass processContent on failure.",
        "arm": True,
        "severity": "Medium",
        "tactics": ["DefenseEvasion"],
        "techniques": ["T1562"],
    },
    {
        "id": "EAG-DET-007",
        "priority": "P2",
        "title": "Suspicious cloud application activity",
        "surface": "defender-hunting",
        "query_file": "detections/kql/EAG-DET-007-suspicious-cloud-app-activity.kql",
        "tables": ["CloudAppEvents"],
        "columns": [
            "Timestamp",
            "ActionType",
            "Application",
            "OAuthAppId",
            "AccountObjectId",
            "AccountDisplayName",
            "IsAdminOperation",
            "IPAddress",
            "CountryCode",
            "ReportId",
        ],
        "permissions": ["Defender XDR advanced hunting; Defender for Cloud Apps connected"],
        "schema_source": "https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-cloudappevents-table",
        "query": """CloudAppEvents
| where Timestamp > ago(1d)
| where OAuthAppId == "REPLACE_WITH_APPLICATION_ID" or Application has "Copilot"
| where IsAdminOperation == true or ActionType has "Consent"
| project Timestamp, ActionType, Application, OAuthAppId, AccountObjectId, AccountDisplayName, IsAdminOperation, IPAddress, CountryCode, ReportId
""",
        "expected": "Admin or consent activity for the agent OAuth app or Copilot-related cloud app events.",
        "false_positives": "Security administrator reviews and approved Copilot admin operations.",
        "investigation": "Pivot on ReportId and AccountObjectId. Confirm the OAuth app ID before containment.",
        "remediation": "Disable the OAuth app or remove consent if the actor is unapproved. Preserve the hunting result as evidence.",
        "arm": False,
        "severity": "Medium",
        "tactics": ["Collection"],
        "techniques": ["T1530"],
    },
    {
        "id": "EAG-DET-008",
        "priority": "P1",
        "title": "Anonymous proxy activity",
        "surface": "defender-hunting",
        "query_file": "detections/kql/EAG-DET-008-anonymous-proxy.kql",
        "tables": ["CloudAppEvents"],
        "columns": [
            "Timestamp",
            "ActionType",
            "Application",
            "OAuthAppId",
            "AccountObjectId",
            "IPAddress",
            "IsAnonymousProxy",
            "CountryCode",
            "City",
            "Isp",
            "ReportId",
        ],
        "permissions": ["Defender XDR advanced hunting"],
        "schema_source": "https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-cloudappevents-table",
        "query": """CloudAppEvents
| where Timestamp > ago(1d)
| where IsAnonymousProxy == true
| where OAuthAppId == "REPLACE_WITH_APPLICATION_ID" or Application has "REPLACE_WITH_AGENT_DISPLAY_NAME"
| project Timestamp, ActionType, Application, OAuthAppId, AccountObjectId, IPAddress, IsAnonymousProxy, CountryCode, City, Isp, ReportId
""",
        "expected": "Cloud app events whose client IP is classified as an anonymous proxy.",
        "false_positives": "Approved privacy relays and corporate secure web gateways that Defender classifies as proxy.",
        "investigation": "Check Isp, CountryCode, and whether the account is an agent operator. Compare with SigninLogs for the same window.",
        "remediation": "Block anonymous proxy sign-in with Conditional Access if confirmed. Do not treat the classification as proof of compromise by itself.",
        "arm": False,
        "severity": "High",
        "tactics": ["DefenseEvasion"],
        "techniques": ["T1090"],
    },
    {
        "id": "EAG-DET-009",
        "priority": "P1",
        "title": "High-severity Defender alerts",
        "surface": "defender-hunting",
        "query_file": "detections/kql/EAG-DET-009-high-severity-alerts.kql",
        "tables": ["AlertInfo"],
        "columns": [
            "Timestamp",
            "AlertId",
            "Title",
            "Category",
            "Severity",
            "ServiceSource",
            "DetectionSource",
            "AttackTechniques",
        ],
        "permissions": ["Defender XDR advanced hunting; service data access depends on deployed Defender products and RBAC"],
        "schema_source": "https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertinfo-table",
        "query": """AlertInfo
| where Timestamp > ago(1d)
| where Severity =~ "High"
| project Timestamp, AlertId, Title, Category, Severity, ServiceSource, DetectionSource, AttackTechniques
""",
        "expected": "High-severity alerts from Defender services and, when onboarded, Sentinel alerts in the Defender portal.",
        "false_positives": "Known pentest windows and noisy policies that the SOC has already accepted.",
        "investigation": "Join AlertEvidence on AlertId in the Defender portal to list entities. This query does not join AlertEvidence so it stays on verified AlertInfo columns.",
        "remediation": "Follow the product incident queue. Contain only confirmed entities. Record the AlertId in the evidence manifest.",
        "arm": False,
        "severity": "High",
        "tactics": ["Impact"],
        "techniques": ["T1565"],
    },
]

CHECKLIST = [
    ("CFG-001", "Record the Entra tenant ID", "Tenant reader", "Store only the tenant ID in the secret-free template copy used by the test tenant.", "Open Entra admin center and compare the tenant ID with the configuration value.", "IDs match and the value is not a REPLACE_WITH placeholder.", "Value missing, malformed, or still a placeholder.", "Redacted configuration excerpt and portal screenshot reference."),
    ("CFG-002", "Register the agent application", "Application Administrator", "Create an app registration and record the client ID. Do not commit the secret.", "Confirm the application object ID and client ID in Entra.", "Application exists and IDs match configuration.", "Application missing or secret stored in git.", "App registration properties export with secrets removed."),
    ("CFG-003", "Create a distinct agent identity", "Agent 365 administrator", "Register the blueprint and agent instance so the agent ID differs from the application ID.", "Compare agent ID, blueprint ID, and application ID.", "Three identifiers are present and agent ID is not the application ID.", "Identifiers missing or equal.", "Agent registry excerpt with IDs partially redacted."),
    ("CFG-004", "Grant delegated permissions and admin consent", "Privileged Role Administrator", "Grant the delegated permissions in the matrix that the user workflow requires.", "Read oauth2PermissionGrants or the consent screen.", "Each required delegated permission is granted and admin-consented.", "Any required delegated permission missing.", "Consent screenshot with user names redacted."),
    ("CFG-005", "Grant application permissions only where supported", "Privileged Role Administrator", "Grant application permissions from the matrix. Do not grant Agent365.Observability.OtelWrite as an application permission.", "Compare app role assignments with the matrix.", "Supported application permissions granted; unsupported ones absent.", "Unsupported permission granted or required application permission missing.", "App role assignment export."),
    ("CFG-006", "Validate delegated user authentication", "Identity tester", "Complete an authorization-code sign-in as a test user.", "Acquire a delegated token and call GET /me with that token.", "GET /me returns the test user and no secret is logged.", "Token acquisition fails or /me is called with an application token.", "HTTP status and token claims with the token itself removed."),
    ("CFG-007", "Validate application authentication separately", "Identity tester", "Use client credentials only for application-permission calls.", "Request a token for https://graph.microsoft.com/.default and inspect roles, not scp.", "Token contains roles for granted application permissions.", "Token missing, or delegated scopes used for an app-only call.", "Redacted token-claim excerpt."),
    ("CFG-008", "Compute Purview protection scopes", "Compliance administrator", "Call protectionScopes/compute for the test user and agent application location.", "Send the reference request body and record executionMode.", "200 response and an ETag are stored.", "Non-success status or empty error handling that fails open.", "Redacted process response and ETag."),
    ("CFG-009", "Evaluate a prompt with processContent", "Compliance administrator", "Submit a synthetic prompt marker, not real customer content.", "Call processContent with activity uploadText.", "200/204 and policyActions interpreted; block stops the model call.", "Model called after a block action.", "Redacted processContent response."),
    ("CFG-010", "Evaluate the model response with processContent", "Compliance administrator", "Submit the model output as downloadText before returning it to the user.", "Call processContent on the response.", "Block prevents the response from being returned.", "Response returned after restrictionAction block.", "Redacted response-evaluation record."),
    ("CFG-011", "Record contentActivities", "Compliance administrator", "Post metadata only after the decision.", "Call contentActivities and confirm raw prompt text is absent.", "201 Created and body has no content.data field.", "Raw prompt stored in the audit body or call fails.", "Redacted 201 response."),
    ("CFG-012", "Configure Azure OpenAI and Agent Framework", "Azure OpenAI user", "Set endpoint and deployment. Install agent-framework in the tenant environment only.", "Import the package and run one authorized completion.", "Completion succeeds and is traced.", "Package missing or endpoint still a placeholder.", "Redacted completion metadata, not the full prompt."),
    ("CFG-013", "Enforce the tool allowlist", "Agent owner", "Configure tools.allowlist.", "Call an allowlisted tool and a denied tool.", "Allowlisted tool returns data; denied tool returns an authorization error.", "Denied tool executes.", "Gateway JSON-RPC transcript."),
    ("CFG-014", "Register the MCP server", "Agent owner", "Run the reference MCP server only on an authorized network.", "initialize and tools/list succeed.", "Only allowlisted tools are advertised.", "Unlisted tool is advertised or callable.", "tools/list response."),
    ("CFG-015", "Configure Microsoft OpenTelemetry for Agent 365", "Agent 365 administrator", "Install microsoft-opentelemetry and supply a token resolver. Grant delegated OtelWrite or use S2S as documented.", "Start the process and emit a test span.", "Span accepted by the intended backend, or a documented failure is recorded.", "Export failure is ignored or reported as success.", "Exporter log with tokens removed."),
    ("CFG-016", "Configure Application Insights", "Monitoring contributor", "Store the connection string in a secret store.", "Confirm the resource exists and a local span can target it.", "Resource ID matches configuration.", "Connection string committed or resource missing.", "Resource ID only."),
    ("CFG-017", "Deploy the APIM policy in a non-production gateway", "API Management operator", "Parameterize tenant and application IDs. Keep deploy off until reviewed.", "Send a request without a token and with a valid test token.", "Unauthenticated call is rejected; valid token reaches the backend.", "Policy contains a secret or fails open.", "APIM trace with tokens removed."),
    ("CFG-018", "Confirm Defender advanced hunting access", "Security reader", "Enable Defender for Cloud Apps Microsoft 365 activities.", "Run the CloudAppEvents and AlertInfo queries for one day.", "Queries parse and return a result set, including an empty set.", "Query fails because a column or table is absent.", "Hunting result count and any schema error."),
    ("CFG-019", "Confirm Sentinel workspace and analytics rules", "Sentinel contributor", "Enable connectors for SigninLogs, AuditLogs, and Microsoft Graph activity.", "Run getschema for each table, then deploy rules only if columns match.", "Schemas match the detection files and rules are enabled only after review.", "Column mismatch or rules deployed while disabled-by-default flag is ignored.", "getschema excerpt and rule deployment output."),
    ("CFG-020", "Replace synthetic evidence", "Control owner and reviewer", "Follow REPLACE-SYNTHETIC-EVIDENCE.md.", "Hash tenant evidence and obtain reviewer approval.", "Manifest hashes match and reviewer status is approved.", "Synthetic records left labeled as customer results.", "Approved manifest."),
    ("CFG-021", "Inventory packages with CopilotPackages.Read.All", "Agent 365 administrator", "Confirm the Agent 365 license, then call the catalog API.", "GET /copilot/admin/catalog/packages.", "200 and a package collection, or a documented license error.", "Call reported as success without a status code.", "Redacted package list."),
    ("CFG-022", "Keep secrets out of the repository", "Security reviewer", "Use a secret store for client secrets, API keys, and connection strings.", "Scan the repository for connection strings and private keys.", "No live secret is present.", "Any live secret committed.", "Scan log."),
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_detections() -> None:
    KQL.mkdir(parents=True, exist_ok=True)
    catalog = {
        "reviewed": "2026-11-05",
        "disclaimer": "Queries use columns documented by Microsoft or the custom table in this repository. Confirm each table with getschema or advanced-hunting schema before enabling an analytics rule. These detections do not establish regulatory compliance.",
        "detections": [],
    }
    for item in DETECTIONS:
        header = (
            f"// Detection ID: {item['id']}\n"
            f"// Priority: {item['priority']}\n"
            f"// Surface: {item['surface']}\n"
            f"// Schema source: {item['schema_source']}\n"
            "// Confirm this query in the customer workspace before enabling it.\n"
        )
        (ROOT / item["query_file"]).write_text(header + item["query"], encoding="utf-8")
        catalog["detections"].append(
            {
                "id": item["id"],
                "priority": item["priority"],
                "title": item["title"],
                "surface": item["surface"],
                "query_file": item["query_file"],
                "required_tables": item["tables"],
                "required_columns": item["columns"],
                "required_permissions": item["permissions"],
                "schema_source": item["schema_source"],
                "analytics_rule": item["arm"],
            }
        )
        md = ROOT / "detections" / f"{item['id']}.md"
        md.write_text(
            "\n".join(
                [
                    f"# {item['id']} {item['title']}",
                    "",
                    f"- Priority: {item['priority']}",
                    f"- Surface: {item['surface']}",
                    f"- Required tables: {', '.join(item['tables'])}",
                    f"- Required columns: {', '.join(item['columns'])}",
                    f"- Required permissions: {item['permissions']}",
                    f"- Schema source: {item['schema_source']}",
                    "- Schema review date: 2026-11-05",
                    "",
                    "## KQL",
                    "",
                    "```kql",
                    item["query"].strip(),
                    "```",
                    "",
                    "## Expected results",
                    "",
                    item["expected"],
                    "",
                    "## False positives",
                    "",
                    item["false_positives"],
                    "",
                    "## Investigation steps",
                    "",
                    item["investigation"],
                    "",
                    "## Remediation guidance",
                    "",
                    item["remediation"],
                    "",
                    "Do not enable this detection in production until a tenant test confirms the table and columns.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    (ROOT / "detections" / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    write_arm()


def write_arm() -> None:
    resources = []
    for item in DETECTIONS:
        if not item["arm"]:
            continue
        resources.append(
            {
                "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
                "apiVersion": "2023-11-01",
                "name": "[concat(parameters('workspaceName'), '/Microsoft.SecurityInsights/', '"
                + item["id"].lower()
                + "')]",
                "condition": "[parameters('deployRules')]",
                "kind": "Scheduled",
                "properties": {
                    "displayName": f"{item['id']} {item['title']}",
                    "description": item["expected"],
                    "severity": item["severity"],
                    "enabled": False,
                    "query": item["query"].strip(),
                    "queryFrequency": "PT1H",
                    "queryPeriod": "P1D",
                    "triggerOperator": "GreaterThan",
                    "triggerThreshold": 0,
                    "suppressionDuration": "PT1H",
                    "suppressionEnabled": False,
                    "tactics": item["tactics"],
                    "techniques": item["techniques"],
                },
            }
        )
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "workspaceName": {
                "type": "string",
                "defaultValue": "REPLACE_WITH_SENTINEL_WORKSPACE_NAME",
            },
            "deployRules": {
                "type": "bool",
                "defaultValue": False,
                "metadata": {
                    "description": "Keep false until tenant schema validation passes. Deployment creates no rule while false."
                },
            },
        },
        "resources": resources,
    }
    (ARM / "analytics-rules.json").write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")


def write_checklist_and_results() -> None:
    checklist_path = ROOT / "checklists" / "tenant-configuration-checklist.csv"
    with checklist_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "Item ID",
                "Configuration requirement",
                "Required permissions",
                "Setup instructions",
                "Validation procedure",
                "Pass criteria",
                "Fail criteria",
                "Expected evidence",
                "Reviewer",
                "Date",
                "Status",
            ],
        )
        writer.writeheader()
        for item_id, requirement, permission, setup, validation, passed, failed, evidence in CHECKLIST:
            writer.writerow(
                {
                    "Item ID": item_id,
                    "Configuration requirement": requirement,
                    "Required permissions": permission,
                    "Setup instructions": setup,
                    "Validation procedure": validation,
                    "Pass criteria": passed,
                    "Fail criteria": failed,
                    "Expected evidence": evidence,
                    "Reviewer": "",
                    "Date": "",
                    "Status": "Not started — tenant validation required",
                }
            )
    lines = [
        "# Tenant configuration checklist",
        "",
        "Status values in this file are not tenant results. Complete them in an authorized test tenant.",
        "Implementing a row does not by itself establish regulatory compliance.",
        "",
        "| Item | Requirement | Required permissions | Status |",
        "| --- | --- | --- | --- |",
    ]
    for item_id, requirement, permission, *_rest in CHECKLIST:
        lines.append(
            f"| {item_id} | {requirement} | {permission} | Not started — tenant validation required |"
        )
    lines.append("")
    lines.append("Full procedures, pass criteria, fail criteria, and expected evidence are in `tenant-configuration-checklist.csv`.")
    lines.append("")
    (ROOT / "checklists" / "tenant-configuration-checklist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    manifest_items = []
    result_rows = []
    for item_id, requirement, permission, setup, validation, passed, failed, evidence in CHECKLIST:
        evidence_name = f"{item_id}-synthetic.json"
        payload = {
            "classification": "SYNTHETIC",
            "not_customer_evidence": True,
            "production_ready": False,
            "test_id": f"TST-{item_id}",
            "checklist_item": item_id,
            "requirement": requirement,
            "synthetic_observation": (
                "Local authoring environment did not connect to a Microsoft tenant. "
                "This record exists so the evidence slot and hash procedure can be tested."
            ),
            "expected_evidence": evidence,
            "actual_result": "SYNTHETIC_NOT_A_TENANT_RESULT",
        }
        path = EVIDENCE / evidence_name
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        digest = sha256_file(path)
        manifest_items.append(
            {
                "test_id": f"TST-{item_id}",
                "path": f"evidence/synthetic/{evidence_name}",
                "sha256": digest,
                "classification": "SYNTHETIC",
                "not_customer_evidence": True,
            }
        )
        result_rows.append(
            {
                "Test ID": f"TST-{item_id}",
                "Checklist item": item_id,
                "Test procedure": validation,
                "Pass criteria": passed,
                "Fail criteria": failed,
                "Expected result": evidence,
                "Actual result": "SYNTHETIC — not a tenant result. No Microsoft API was called for this row.",
                "Evidence reference": f"evidence/synthetic/{evidence_name}",
                "Tester": "local-authoring-environment",
                "Reviewer": "",
                "Status": "Synthetic dry-run only — tenant validation required",
            }
        )
    manifest = {
        "classification": "SYNTHETIC",
        "not_customer_evidence": True,
        "generated_for": "evidence-slot and hash procedure validation",
        "items": manifest_items,
    }
    manifest_path = ROOT / "evidence" / "sample-evidence-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    results_csv = ROOT / "TENANT-TEST-RESULTS.csv"
    with results_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result_rows[0].keys()))
        writer.writeheader()
        writer.writerows(result_rows)
    md = [
        "# Tenant test results",
        "",
        "Every row below is a synthetic dry run. None of these rows is a customer or test-tenant result.",
        "",
        "| Test ID | Checklist item | Status | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in result_rows:
        md.append(
            f"| {row['Test ID']} | {row['Checklist item']} | {row['Status']} | `{row['Evidence reference']}` |"
        )
    md.append("")
    md.append("Pass criteria, fail criteria, procedures, and actual results are in `TENANT-TEST-RESULTS.csv`.")
    md.append("")
    (ROOT / "TENANT-TEST-RESULTS.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def write_table_schema() -> None:
    schema = {
        "table": "AgentGovernance_CL",
        "owner": "this repository",
        "microsoft_published": False,
        "columns": [
            {"name": "TimeGenerated", "type": "datetime"},
            {"name": "CorrelationId", "type": "string"},
            {"name": "AgentId", "type": "string"},
            {"name": "Stage", "type": "string"},
            {"name": "Decision", "type": "string"},
            {"name": "UserId", "type": "string"},
            {"name": "ToolName", "type": "string"},
            {"name": "Allowed", "type": "bool"},
        ],
        "note": "Create this table with a Data Collection Rule before enabling EAG-DET-004 or EAG-DET-005. Do not assume classic custom-log suffixes.",
    }
    (ROOT / "deploy" / "agent-governance-table.json").write_text(
        json.dumps(schema, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    write_detections()
    write_table_schema()
    write_checklist_and_results()
    print("artifacts generated")


if __name__ == "__main__":
    main()
