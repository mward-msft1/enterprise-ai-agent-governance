# Control catalog

These mappings help a customer relate this reference implementation to common frameworks. They are not an attestation. Implementing a control in this repository does not by itself establish NIST, ISO, SOC 2, HIPAA, GDPR, PCI DSS, SOX, or GLBA compliance.

| ID | Control | Implementation | NIST AI RMF | NIST CSF 2.0 | ISO 27001:2022 | ISO 42001 | SOC 2 | HIPAA | GDPR | PCI DSS | SOX | GLBA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EAG-CTL-001 | Distinct agent identity | `identity/agent_identity.py` | GOVERN 1.1 | GV.OC | A.5.16 | 5.2 | CC6.1 | 164.312(a)(1) | Art. 5(1)(f) | 7.2, 8.2 | ITGC access | Safeguards access |
| EAG-CTL-002 | Separated delegated and application permissions | `config/permissions-matrix.json` | GOVERN 1.2 | PR.AA | A.5.15, A.8.2 | 8.2 | CC6.1, CC6.3 | 164.312(a)(1) | Art. 32 | 7.1, 8.2 | ITGC access | Safeguards access |
| EAG-CTL-003 | User authentication before evaluation | `auth/graph_auth.py` | MEASURE 2.7 | PR.AA | A.5.17, A.8.5 | 8.3 | CC6.1 | 164.312(d) | Art. 32 | 8.3 | ITGC access | Safeguards access |
| EAG-CTL-004 | Protection-scope computation | `purview/protection_scopes.py` | MAP 1.5 | GV.PO | A.5.1 | 6.1 | CC2.1 | 164.308(a)(1) | Art. 5, 24 | 12.1 | Change management | Privacy rule process |
| EAG-CTL-005 | Prompt policy evaluation | `purview/process_content.py` | MEASURE 2.6 | PR.DS | A.5.34, A.8.12 | 9.2 | CC6.7, CC7.1 | 164.312(e)(1) | Art. 32 | 3.4, 6.5 | ITGC processing | Safeguards integrity |
| EAG-CTL-006 | Response policy evaluation | workflow response stage | MEASURE 2.6 | PR.DS | A.5.34 | 9.3 | CC6.7 | 164.312(e)(1) | Art. 5(1)(c) | 3.4 | ITGC processing | Safeguards integrity |
| EAG-CTL-007 | Allowlisted tools and MCP | `tools/mcp_gateway.py` | MANAGE 2.2 | PR.PS | A.8.9, A.8.28 | 8.4 | CC6.8 | 164.312(a)(1) | Art. 25 | 6.4 | Change management | Safeguards service providers |
| EAG-CTL-008 | Metadata-only audit | `purview/content_activities.py` | GOVERN 4.2 | PR.PS | A.8.15 | 9.4 | CC7.2 | 164.312(b) | Art. 30 | 10.2 | ITGC audit | Safeguards monitoring |
| EAG-CTL-009 | Telemetry export | `telemetry/otel_export.py` | MEASURE 2.4 | DE.CM | A.8.16 | 9.1 | CC7.2 | 164.308(a)(1)(ii)(D) | Art. 32 | 10.6 | ITGC monitoring | Safeguards monitoring |
| EAG-CTL-010 | Detection and investigation | `detections/` | MANAGE 3.1 | DE.AE, RS.AN | A.5.24, A.5.25 | 10.2 | CC7.3 | 164.308(a)(6) | Art. 33 process support | 12.10 | Incident disclosure support | Safeguards incident response |
| EAG-CTL-011 | Secret exclusion | `.gitignore`, APIM policy check | GOVERN 6.1 | PR.DS | A.5.33, A.8.24 | 7.5 | CC6.1 | 164.312(a)(2)(iv) | Art. 32 | 3.5, 8.3 | ITGC change | Safeguards encryption |
| EAG-CTL-012 | Evidence integrity | `REPLACE-SYNTHETIC-EVIDENCE.md` | GOVERN 4.2 | GV.OV | A.5.36 | 4.5 | CC4.1 | 164.308(a)(8) | Art. 5(2) | 12.1 | Record retention | Safeguards oversight |

## How to use the catalog

1. Select the frameworks that apply to the customer. Not every column applies to every organization.
2. Map each selected cell to the customer's own control statement.
3. Attach tenant evidence, not the synthetic files in this repository.
4. Record residual risk where a cell is only partially implemented.
5. Have the compliance owner, not this repository, decide whether a framework requirement is met.

HIPAA, PCI DSS, SOX, and GLBA rows are relevance aids for covered entities, merchants, public companies, and financial institutions. They are not legal advice and they are not an implementation of those regimes.
