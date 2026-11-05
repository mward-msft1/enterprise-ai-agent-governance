# Customer audit guide

Use this page to explain the repository in a customer meeting, then to build the evidence package their internal and external audiences will ask for.

This is not a compliance certification. Microsoft 365 E7 does not, by itself, prove that a custom agent is governed. The license provides the products. The agent must call them, and a reviewer must keep the exports.

## Say this first

Microsoft 365 E7 includes Microsoft 365 E5, Microsoft 365 Copilot, Microsoft Agent 365, and Microsoft Entra Suite. That is the stack a customer uses to show who an agent is, which person it acted for, whether Purview allowed the content, and whether Defender can find the same event later.

This repository walks one custom agent through that stack and names the record each step leaves behind. The customer replaces the synthetic files with exports from their own tenant. Those exports are what internal audit, an external auditor, or the customer's own customer can review.

Do not say the sample output is their evidence. Do not say a control mapping is an attestation.

Source for the E7 bundle: [Microsoft 365 E7](https://www.microsoft.com/en-us/microsoft-365/enterprise/e7). Confirm the customer's agreement before describing a feature as licensed.

## The six questions an audience will ask

| # | Question | Plain answer | Technical record |
| --- | --- | --- | --- |
| 1 | Which agent acted? | An Entra-backed agent identity, not an unnamed script | Agent 365 inventory and Entra application audit |
| 2 | Which person was it acting for? | A signed-in user, separate from the application's own credential | Entra sign-in log, delegated token |
| 3 | Was this content in a Purview scope? | The agent asked Purview before the model ran | `protectionScopes/compute` response and ETag |
| 4 | Did policy allow the prompt and the response? | Purview evaluated both. A block stops the workflow | `processContent` `policyActions` and `processingErrors` |
| 5 | Which tools ran, and were they allowed? | Only the allowlist. A denied tool is not executed | MCP gateway result, plus a customer-logged denial |
| 6 | Can we find that same event later? | One correlation ID ties the audit record to hunting | Purview `contentActivities`, Defender or Sentinel |

If any row has no tenant export, the answer to an auditor is "not yet evidenced," not "the control is operating."

## Two kinds of evidence

E7 already contains products that record identity, data protection, and security events. A custom agent is invisible to those products until it is registered and it emits the events.

| Kind | What it proves | Where it comes from | What the customer must do |
| --- | --- | --- | --- |
| Product records | The tenant saw an identity, a sign-in, a policy decision, or an alert | Entra, Purview Audit, Defender XDR, Agent 365 | Turn the feature on, retain it, and export it |
| Agent-emitted records | This agent asked Purview, logged the decision, and exported telemetry | Graph calls and OpenTelemetry from the agent | Deploy the calls. E7 does not emit them for an agent that never calls Microsoft |

Sentinel is the SIEM surface used by the detections in this repository. A Log Analytics workspace is still an Azure resource the customer creates and connects. Do not describe a workspace as pre-provisioned because the customer bought E7. Confirm any Sentinel benefit in the customer's agreement.

## Which E7 product answers which question

| Product in the E7 stack | What to tell the customer | Evidence they can export | Repo path |
| --- | --- | --- | --- |
| Entra ID and Entra Suite | The agent and the user are different identities. Permission changes are audited. | Sign-in log, Audit log for consent and credentials, Conditional Access result | [config/permissions-matrix.md](config/permissions-matrix.md), `detections/kql/EAG-DET-001` to `EAG-DET-003` |
| Agent 365 | Agents are inventoried and observed in one control plane. The SDK extends an agent. It does not build one. | Package inventory, Agent 365 telemetry after OpenTelemetry export | `src/eagov/agent365/`, `src/eagov/telemetry/` |
| Microsoft Purview | Data protection runs before the model and again before the response. The audit record does not need the raw prompt. | `processContent` decision, `contentActivities` metadata, Purview Audit export | `src/eagov/purview/` |
| Microsoft Defender | Investigation starts from the correlation ID, not from a pasted prompt. | Advanced hunting results for `CloudAppEvents` and `AlertInfo` | `detections/kql/EAG-DET-007` to `EAG-DET-009` |
| Microsoft 365 Copilot and Copilot Studio | Licensed agents can be in the same inventory. A custom Python agent still needs this control path. | Agent 365 catalog export | `src/eagov/agent365/discovery.py` |
| Purview Audit | The durable copy an auditor can request without reading application logs. | Unified Audit Log export for the same time window and correlation ID | [REPLACE-SYNTHETIC-EVIDENCE.md](REPLACE-SYNTHETIC-EVIDENCE.md) |

Some Agent 365 features require Microsoft 365 E7, G7, or an Agent 365 license, and still require admin setup. Check the current feature table before telling a customer a console button is included.

## How to walk the meeting

1. Draw the path: identify the agent, authenticate the user, ask Purview, run the model, call an allowlisted tool, ask Purview again, write the audit record, export telemetry, investigate.
2. Run the offline demo only to show the order. Say out loud that the result is synthetic.
3. In the test tenant, pick one correlation ID from an allowed run and one from a denied run.
4. Show that same ID in the Purview activity, the Entra sign-in, and the hunting query. Three screens, one ID, is the proof.
5. Open the evidence index. Every row needs an exporter, a reviewer, a date, and a hash.
6. Close with what is not claimed: no certification, no production sign-off, no use of the files in `evidence/synthetic`.

## What each audience receives

Give each audience a different slice. Do not hand an external reviewer the raw prompt, the token, or the connection string.

| Audience | What they need | What they should not receive |
| --- | --- | --- |
| Security operations | Correlation ID, denied-tool status, hunting query, and the Defender or Sentinel result | A claim that a green local test means the tenant is protected |
| Internal audit or compliance | Control row, permission used, redacted export, hash, tester, reviewer, and date | Synthetic files relabeled as tenant results |
| External auditor, regulator, or the customer's customer | The six answers above, the evidence index, and an explicit list of untested controls | Secrets, employee personal data, or customer content |
| Engineering | The workflow code, the permissions matrix, and the fail-closed rules | Instructions to skip `processingErrors` and continue to the model |

Copy [templates/audit-evidence-index.csv](templates/audit-evidence-index.csv) for the workpaper. One row is one auditor question for one test. Leave Status as `Not evidenced` until the export exists.

## Minimum package for one agent interaction

Collect these for a single correlation ID before describing that interaction as audited:

1. Agent identity: application ID, agent ID, and an Agent 365 or Entra export.
2. User authentication: sign-in log showing the person, the application, and the result. A delegated call and an application call are separate tests.
3. Protection scope: HTTP status, whether inline evaluation was required, and the ETag. Redact the body if it contains customer content.
4. Prompt decision: `protectionScopeState`, `policyActions`, and `processingErrors`. A block must show that the model did not run.
5. Tool decision: allow or deny, tool name, and proof the denied tool did not execute.
6. Response decision: same fields as the prompt decision.
7. Audit record: `contentActivities` status `201`, with metadata only. Confirm the raw prompt is absent.
8. Investigation: one Defender or Sentinel query result, or a written statement that the required table is not yet connected.
9. Review: a second person, not the tester, signs the evidence index.

Hash the redacted file after redaction. The method is in [REPLACE-SYNTHETIC-EVIDENCE.md](REPLACE-SYNTHETIC-EVIDENCE.md).

## What not to say

- "E7 audits every agent automatically." It audits the events the agent and the tenant are configured to emit.
- "The README sample is our audit evidence." Files marked `SYNTHETIC` are packaging examples.
- "The control catalog means we meet NIST, ISO, SOC 2, HIPAA, GDPR, PCI DSS, SOX, or GLBA." It is a map. The customer's compliance owner decides whether a requirement is met.
- "Sentinel already has our agent denials." `AgentGovernance_CL` is a custom table. Create it before those detections can return rows.
- "A successful package import means production-ready." It does not.

## Where to go next

| If the meeting needs... | Open |
| --- | --- |
| The spoken path and the local demo | [README.md](README.md) |
| The setup sequence in a test tenant | [CUSTOMER-QUICKSTART.md](CUSTOMER-QUICKSTART.md) |
| The control-to-framework map | [CONTROL-CATALOG.md](CONTROL-CATALOG.md) |
| The exact permission and API | [config/permissions-matrix.md](config/permissions-matrix.md) and [SOURCE-REGISTER.md](SOURCE-REGISTER.md) |
| The blank workpaper | [templates/audit-evidence-index.csv](templates/audit-evidence-index.csv) |
